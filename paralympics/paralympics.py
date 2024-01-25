from flask import Flask
from markupsafe import escape
from flask import current_app as app
app = Flask(__name__)

@app.route('/')
@app.route("/<name>")
def hello(name=None):
    return f"Hello, {escape(name)}!"
