import html
import os
import re
import subprocess

from flask import Flask, request


app = Flask(__name__)


@app.get("/")
def index():
    os.chdir("/home/nyakov/nyakov/nyakov")
    cmdline = ["./build/nyakov", "chatlogs"]
    try:
        if re.fullmatch(r"\w+", request.query_string.decode(), re.ASCII):
            cmdline.append(request.query_string)
    except UnicodeDecodeError:
        pass

    process = subprocess.run(
        cmdline,
        capture_output=True,
        encoding="UTF-8",
    )
    if process.returncode == 0:
        text = process.stdout.strip()
    elif process.returncode == 1:
        text = "No such user."
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
    <button id="copy">Copy</button>
    <button id="copy-discord">Copy (Discord-safe)</button>
    <button id="reload">New quote</button>
    <p class="bottom"><a href="https://github.com/pettinen/nyakov">Code</a></p>
  <script>
    const copyListener = function(discordSafe) {{
      return async () => {{
        let text = document.getElementById("text").textContent;
        if (discordSafe)
          text = text.replace(/[\\:@_*~`]/gu, "\\$&");
        await navigator.clipboard.writeText(text);
      }};
    }};

    document.getElementById("copy").addEventListener("click", copyListener(false));
    document.getElementById("copy-discord").addEventListener("click", copyListener(true));

    const reloadListener = event => {{
      event.target.textContent = "Loading\u2026";
      event.target.removeEventListener("click", reloadListener);
      location.reload();
    }};
    document.getElementById("reload").addEventListener("click", reloadListener);
  </script>
  </body>
</html>
"""
