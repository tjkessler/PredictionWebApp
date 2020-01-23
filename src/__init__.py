from flask import Flask
from os import urandom
app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(32)
from src import routes
