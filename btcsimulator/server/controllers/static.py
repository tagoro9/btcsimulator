__author__ = 'victor'

from . import app

@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.errorhandler(404)
def push_state(e):
    return app.send_static_file('index.html')