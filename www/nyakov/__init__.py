import html
import os
import subprocess

from flask import Flask


app = Flask(__name__)


@app.get("/")
def index():
    os.chdir("/home/nyakov/nyakov/nyakov")
    process = subprocess.run(
        ["./build/nyakov", "chatlogs"],
        capture_output=True,
        encoding="UTF-8",
    )
    if process.returncode == 0:
        text = process.stdout
    else:
        text = "Unexpected error."

    return fr"""<!DOCTYPE html>
<html>
  <head>
    <title>Nyakov chat generator</title>
    <meta name="viewport" content="width=device-width">
    <link rel="icon" href="/favicon.png" type="image/png">
    <style>
      body {{
        font-family: sans-serif;
      }}
      .bottom {{
        position: absolute;
        bottom: 0;
      }}
    </style>
  </head>
  <body>
    <p id="text">{html.escape(text)}</p>
    <button id="copy">Copy (Discord-safe)</button>
    <button id="new-quote">New quote</button>
    <p class="bottom"><a href="https://github.com/pettinen/nyakov">Code</a></p>
  </body>
  <script>
    document.getElementById("copy").addEventListener("click", async () => {{
      const text = document.getElementById("text").textContent.replace(/[\\:@_*~`]/gu, "\\$&");
      await navigator.clipboard.writeText(text);
    }});
    document.getElementById("new-quote").addEventListener("click", event => {{
      event.target.textContent = "Loading\u2026";
      location.reload();
    }});
  </script>
</html>
"""
