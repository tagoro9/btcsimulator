__author__ = 'victor'
from flask import Flask
import settings

app = Flask(__name__, static_url_path='', static_folder='public')
app.config.from_object(settings)
app.url_map.strict_slashes=False


import core
import tasks
import controllers