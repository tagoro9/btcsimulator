__author__ = 'victor'

from . import app

@app.route('/')
@app.route('/simulation')
@app.route('/stats/network')
@app.route('/stats/blocks')
@app.route('/stats/explorer')
def root():
    return app.send_static_file('index.html')