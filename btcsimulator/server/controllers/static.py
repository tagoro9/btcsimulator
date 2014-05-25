__author__ = 'victor'

from . import app

@app.route('/')
def root():
    return app.send_static_file('index.html')