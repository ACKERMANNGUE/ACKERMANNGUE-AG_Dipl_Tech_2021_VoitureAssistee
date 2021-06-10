# @file hello.py
# @brief Minimal Flask app

# Author : Ackermann Gawen
# Last update : 10.06.2021

from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    """Default route"""
    return 'Hello, World!'