from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    """Default route"""
    return 'Hello, World!'