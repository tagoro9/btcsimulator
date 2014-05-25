__author__ = 'victor'
from flask import Flask
app = Flask(__name__, static_url_path='', static_folder='public')
app.config.from_object('server.settings')
app.url_map.strict_slashes=False

from server import core
from server import controllers