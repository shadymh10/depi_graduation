const form = document.getElementById('shortenForm');
const longUrlInput = document.getElementById('longUrl');
const shortenButton = document.getElementById('shortenButton');
const buttonText = document.getElementById('button-text');
const loader = document.getElementById('loader');
const outputArea = document.getElementById('output-area');
const shortUrlDisplay = document.getElementById('shortened-url-display');
const copyButton = document.getElementById('copyButton');
const copyText = document.getElementById('copy-text');

async function processUrl(longUrl) {
  if (!longUrl) return;

  shortenButton.disabled = true;
  buttonText.textContent = 'ENCODING... STAND BY';
  loader.classList.remove('hidden');
  outputArea.classList.add('hidden');

  try {
    const response = await fetch("/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ longUrl })
    });

    const data = await response.json();
    if (data.error) {
      alert(data.error);
    } else {
      // Show the short URL returned from backend
      const fullShortUrl = `${window.location.origin}/${data.shortCode}`;
      shortUrlDisplay.textContent = fullShortUrl;
      outputArea.classList.remove('hidden');
    }
  } catch (err) {
    alert("Failed to connect to server");
    console.error(err);
  }

  shortenButton.disabled = false;
  buttonText.textContent = 'INITIATE SHORTENING SEQUENCE';
  loader.classList.add('hidden');
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  processUrl(longUrlInput.value.trim());
});

copyButton.addEventListener('click', () => {
  navigator.clipboard.writeText(shortUrlDisplay.textContent).then(() => {
    copyText.textContent = 'HASH COPIED!';
    setTimeout(() => copyText.textContent = 'COPY HASH', 3000);
  });
});