import html
import os
import re
import subprocess

from flask import Flask, request


app = Flask(__name__)


@app.get("/")
def index():
    user = request.args.get("user")
    try:
        if not user or not re.fullmatch(r"\w+", user, re.ASCII):
            user = None
    except UnicodeDecodeError:
        pass

    cmdline = ["./build/nyakov", "chatlogs"]
    if user:
        cmdline.append(user)

    os.chdir("/home/nyakov/nyakov/nyakov")
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

    user_input = '<input type="text" id="user" name="user" placeholder="Twitch user (optional)"'
    if user:
        user_input += f' value="{user}"'
    user_input += ">"

    return fr"""<!DOCTYPE html>
<html>
  <head>
    <title>Nyakov chat generator</title>
    <meta name="viewport" content="width=device-width">
    <link rel="icon" href="/favicon.png" type="image/png">
    <style>
      body {{
        background: black;
        color: white;
        font-family: sans-serif;
      }}
      a {{
        color: skyblue;
        text-decoration: none;
      }}
      .bottom {{
        position: absolute;
        bottom: 0;
        font-size: smaller;
      }}
    </style>
  </head>
  <body>
    <p id="text">{html.escape(text)}</p>
    <p>
      <button id="copy">Copy</button>
      <button id="copy-discord">Copy (Discord-safe)</button>
    </p>
    <form id="new-form" action="/">
      {user_input}
      <button id="new-button">New quote</button>
    </form>
    <p class="bottom">Generates nonsense from Twitch chatlogs with <a href="https://en.wikipedia.org/wiki/Markov_chain">Markov chains</a>. Code available on <a href="https://github.com/pettinen/nyakov">GitHub</a>.</p>
  <script>
    const copyListener = function(discordSafe) {{
      return async () => {{
        let text = document.getElementById("text").textContent;
        if (discordSafe)
          text = text.replace(/[\\/|:_*~`]/gu, "\\$&");
        await navigator.clipboard.writeText(text);
      }};
    }};

    document.getElementById("copy").addEventListener("click", copyListener(false));
    document.getElementById("copy-discord").addEventListener("click", copyListener(true));

    document.getElementById("new-form").addEventListener("submit", event => {{
      document.getElementById("new-button").textContent = "Loading\u2026";
      if (!document.getElementById("user").value) {{
        event.preventDefault();
        location.href = "https://nyakov.aho.ge/";
      }}
    }});
  </script>
  </body>
</html>
"""
