from flask import Flask, request, jsonify, redirect
import sqlite3
import string
import random
from datetime import datetime, timedelta
from prometheus_client import Counter, generate_latest, Histogram
from prometheus_flask_exporter import PrometheusMetrics
from flask import Response
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Prometheus Flask Exporter
metrics = PrometheusMetrics(app)

# Custom metrics for business logic
url_creation_counter = Counter('url_shortener_creations_total', 'Total number of URL shortenings')
url_redirect_counter = Counter('url_shortener_redirects_total', 'Total number of URL redirects', ['short_code'])
custom_error_counter = Counter('url_shortener_custom_errors_total', 'Total number of custom errors', ['error_type'])
url_creation_duration = Histogram('url_shortener_creation_duration_seconds', 'Time spent creating short URLs')

# Application info metric
metrics.info('app_info', 'URL Shortener Backend API', version=os.getenv('APP_VERSION', '1.0.0'))

# Configuration from environment variables
class Config:
    # Database Configuration
    DB_PATH = os.getenv('DB_PATH', '/app/url_shortener.db')

    # Application Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')

    # Short URL Configuration
    DEFAULT_SHORT_CODE_LENGTH = int(os.getenv('DEFAULT_SHORT_CODE_LENGTH', 6))
    DEFAULT_EXPIRY_DAYS = int(os.getenv('DEFAULT_EXPIRY_DAYS', 30))
    MAX_SHORT_CODE_LENGTH = int(os.getenv('MAX_SHORT_CODE_LENGTH', 10))

    # Rate Limiting (optional)
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 100))

app.config.from_object(Config)

def get_db_path():
    """Get database path from configuration"""
    return Config.DB_PATH

def init_db():
    """Initialize database with required tables"""
    db_path = get_db_path()
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS urls
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             original_url TEXT NOT NULL,
             short_code TEXT UNIQUE NOT NULL,
             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
             expires_at TIMESTAMP,
             click_count INTEGER DEFAULT 0)
        ''')

        # Create indexes for better performance
        c.execute('CREATE INDEX IF NOT EXISTS idx_short_code ON urls(short_code)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_expires_at ON urls(expires_at)')

        conn.commit()
        conn.close()
        logger.info("Database initialized successfully at %s", db_path)
    except Exception as e:
        logger.error("Database initialization error: %s", e)
        raise

def generate_short_code(length=None):
    """Generate a random short code"""
    if length is None:
        length = Config.DEFAULT_SHORT_CODE_LENGTH

    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_valid_url(url):
    """Basic URL validation"""
    return url.startswith(('http://', 'https://'))

def cleanup_expired_urls():
    """Clean up expired URLs from the database"""
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute('DELETE FROM urls WHERE expires_at < ?', (datetime.now(),))
        deleted_count = c.rowcount
        conn.commit()
        conn.close()

        if deleted_count > 0:
            logger.info("Cleaned up %d expired URLs", deleted_count)

        return deleted_count
    except Exception as e:
        logger.error("Error cleaning up expired URLs: %s", e)
        return 0

@app.route('/')
def home():
    """API Home endpoint"""
    return jsonify({
        'message': 'URL Shortener API',
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'environment': Config.FLASK_ENV,
        'endpoints': {
            'shorten': 'POST /shorten',
            'redirect': 'GET /<short_code>',
            'stats': 'GET /stats/<short_code>',
            'health': 'GET /health',
            'metrics': 'GET /metrics',
            'cleanup': 'POST /cleanup',
            'dashboard': 'GET /dashboard'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for Docker and orchestration"""
    try:
        # Check database connection
        conn = sqlite3.connect(get_db_path())
        conn.close()

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'environment': Config.FLASK_ENV,
            'database': 'connected'
        }), 200
    except Exception as e:
        custom_error_counter.labels(error_type='health_check').inc()
        logger.error("Health check failed: %s", e)
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Create a new short URL"""
    start_time = time.time()

    # Handle both form data and JSON
    if request.is_json:
        data = request.get_json()
        original_url = data.get('url')
        custom_code = data.get('custom_code')
        days_valid = data.get('days_valid', Config.DEFAULT_EXPIRY_DAYS)
    else:
        original_url = request.form.get('url')
        custom_code = request.form.get('custom_code')
        days_valid = int(request.form.get('days_valid', Config.DEFAULT_EXPIRY_DAYS))

    # Validation
    if not original_url:
        custom_error_counter.labels(error_type='validation').inc()
        return jsonify({'error': 'URL is required'}), 400

    if not is_valid_url(original_url):
        original_url = 'http://' + original_url

    # Validate custom code length
    if custom_code and len(custom_code) > Config.MAX_SHORT_CODE_LENGTH:
        custom_error_counter.labels(error_type='validation').inc()
        return jsonify({'error': f'Custom code too long (max {Config.MAX_SHORT_CODE_LENGTH} characters)'}), 400

    short_code = custom_code if custom_code else generate_short_code()
    expires_at = datetime.now() + timedelta(days=days_valid)

    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()

        # Check if custom code already exists
        if custom_code:
            c.execute('SELECT short_code FROM urls WHERE short_code = ?', (short_code,))
            if c.fetchone():
                custom_error_counter.labels(error_type='duplicate_code').inc()
                return jsonify({'error': 'Custom code already exists'}), 409

        # Insert new URL
        c.execute('''
            INSERT INTO urls (original_url, short_code, expires_at)
            VALUES (?, ?, ?)
        ''', (original_url, short_code, expires_at))

        conn.commit()
        conn.close()

        # Update metrics
        url_creation_counter.inc()
        url_creation_duration.observe(time.time() - start_time)

        logger.info("URL shortened: %s -> %s", original_url, short_code)

        return jsonify({
            'original_url': original_url,
            'short_code': short_code,
            'short_url': f"/{short_code}",
            'expires_at': expires_at.isoformat(),
            'message': 'URL shortened successfully'
        }), 201

    except sqlite3.IntegrityError:
        custom_error_counter.labels(error_type='integrity').inc()
        logger.warning("Integrity error for short code: %s", short_code)
        return jsonify({'error': 'Short code already exists, try again'}), 409
    except Exception as e:
        custom_error_counter.labels(error_type='database').inc()
        logger.error("Error shortening URL: %s", e)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect to original URL"""
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()

        c.execute('''
            SELECT original_url, expires_at FROM urls
            WHERE short_code = ? AND (expires_at IS NULL OR expires_at > ?)
        ''', (short_code, datetime.now()))

        result = c.fetchone()

        if not result:
            custom_error_counter.labels(error_type='not_found').inc()
            logger.info("URL not found or expired: %s", short_code)
            return jsonify({'error': 'URL not found or expired'}), 404

        original_url, expires_at = result

        # Update click count
        c.execute('UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?', (short_code,))
        conn.commit()
        conn.close()

        url_redirect_counter.labels(short_code=short_code).inc()
        logger.info("Redirect: %s -> %s", short_code, original_url)

        return redirect(original_url, code=302)

    except Exception as e:
        custom_error_counter.labels(error_type='database').inc()
        logger.error("Error redirecting URL %s: %s", short_code, e)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/stats/<short_code>')
def get_stats(short_code):
    """Get statistics for a short URL"""
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()

        c.execute('''
            SELECT original_url, short_code, created_at, expires_at, click_count
            FROM urls WHERE short_code = ?
        ''', (short_code,))

        result = c.fetchone()
        conn.close()

        if not result:
            custom_error_counter.labels(error_type='not_found').inc()
            return jsonify({'error': 'URL not found'}), 404

        original_url, short_code_db, created_at, expires_at, click_count = result

        # Check if URL is active
        is_active = not expires_at or datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S') > datetime.now()

        return jsonify({
            'original_url': original_url,
            'short_code': short_code_db,
            'short_url': f"/{short_code_db}",
            'created_at': created_at,
            'expires_at': expires_at,
            'click_count': click_count,
            'is_active': is_active
        })

    except Exception as e:
        custom_error_counter.labels(error_type='database').inc()
        logger.error("Error getting stats for %s: %s", short_code, e)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/dashboard')
def dashboard():
    """API endpoint for dashboard data"""
    try:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()

        # Get recent URLs
        recent_urls = c.execute('''
            SELECT short_code, original_url, created_at, click_count
            FROM urls
            ORDER BY created_at DESC
            LIMIT 20
        ''').fetchall()

        # Get total stats
        c.execute('SELECT COUNT(*) FROM urls')
        total_urls = c.fetchone()[0]

        c.execute('SELECT SUM(click_count) FROM urls')
        total_clicks = c.fetchone()[0] or 0

        c.execute('SELECT COUNT(*) FROM urls WHERE expires_at > ? OR expires_at IS NULL', (datetime.now(),))
        active_urls = c.fetchone()[0]

        conn.close()

        # Convert to list of dicts for JSON
        urls_list = []
        for url in recent_urls:
            urls_list.append({
                'short_code': url[0],
                'original_url': url[1],
                'created_at': url[2],
                'click_count': url[3]
            })

        return jsonify({
            'recent_urls': urls_list,
            'total_urls': total_urls,
            'total_clicks': total_clicks,
            'active_urls': active_urls
        })

    except Exception as e:
        custom_error_counter.labels(error_type='database').inc()
        logger.error("Error loading dashboard: %s", e)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Clean up expired URLs (admin endpoint)"""
    try:
        deleted_count = cleanup_expired_urls()
        return jsonify({
            'message': 'Cleanup completed',
            'deleted_urls': deleted_count
        }), 200
    except Exception as e:
        logger.error("Error during cleanup: %s", e)
        return jsonify({'error': 'Cleanup failed'}), 500

@app.route('/metrics')
def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), content_type='text/plain')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    custom_error_counter.labels(error_type='404').inc()
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    custom_error_counter.labels(error_type='500').inc()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    custom_error_counter.labels(error_type='405').inc()
    return jsonify({'error': 'Method not allowed'}), 405

if __name__ == '__main__':
    # Wait a bit for the system to be ready
    logger.info("Starting URL Shortener Backend...")
    logger.info("Environment: %s", Config.FLASK_ENV)
    logger.info("Database path: %s", Config.DB_PATH)
    logger.info("Host: %s", Config.HOST)
    logger.info("Port: %d", Config.PORT)
    logger.info("Debug mode: %s", Config.DEBUG)

    time.sleep(5)
    init_db()

    # Perform initial cleanup
    cleanup_expired_urls()

    port = Config.PORT
    host = Config.HOST
    debug = Config.DEBUG

    logger.info("Server starting on %s:%d", host, port)
    app.run(host=host, port=port, debug=debug)
