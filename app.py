from flask import Flask, request, jsonify, render_template, redirect
import sqlite3
import secrets

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS url_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            long_url TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# دالة توليد كود قصير عشوائي
def generate_short_code():
    return secrets.token_urlsafe(4)[:6]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    data = request.get_json(force=True)
    long_url = data.get("longUrl")

    if not long_url:
        return jsonify({"error": "No longUrl provided"}), 400

    conn = sqlite3.connect("urls.db")
    c = conn.cursor()

    # check existing
    c.execute("SELECT id, short_code FROM url_mappings WHERE long_url=?", (long_url,))
    row = c.fetchone()
    if row:
        conn.close()
        return jsonify({"id": row[0], "shortCode": row[1]})

    # insert new
    c.execute("INSERT INTO url_mappings (long_url) VALUES (?)", (long_url,))
    conn.commit()
    id = c.lastrowid

    short_code = generate_short_code()

    c.execute("UPDATE url_mappings SET short_code=? WHERE id=?", (short_code, id))
    conn.commit()
    conn.close()

    return jsonify({"id": id, "shortCode": short_code})

@app.route("/<short_code>")
def redirect_url(short_code):
    conn = sqlite3.connect("urls.db")
    c = conn.cursor()
    c.execute("SELECT long_url FROM url_mappings WHERE short_code=?", (short_code,))
    row = c.fetchone()
    conn.close()

    if row:
        return redirect(row[0])
    else:
        return "Short URL not found", 404

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
