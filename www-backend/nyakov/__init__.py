from flask import Flask

from .api_v1 import api_v1


app = Flask(__name__)
app.register_blueprint(api_v1, url_prefix="/api/v1")
