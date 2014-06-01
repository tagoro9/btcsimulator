__author__ = 'victor'

def start_pubsub():

    from btcsimulator.server import app
    from btcsimulator.server.core import r
    from flask.ext.socketio import emit, SocketIO
    from gevent import Greenlet, monkey

    # Add socket io capabilites
    socketio = SocketIO(app)

    monkey.patch_all()
    def sub(pubsub):
        # Subscribe to channel
        pubsub.subscribe(app.config['SIMULATOR_NAMESPACE'])
        for message in pubsub.listen():
            # Process new messages when they arrive
            Greenlet.spawn(process_received_mesg, message)

    def process_received_mesg(message):
        # Notify all clients the message
        print(message['data'])
        socketio.emit('redis', message['data'], namespace=app.config['SIMULATOR_NAMESPACE'])

    @socketio.on('connect', namespace=app.config['SIMULATOR_NAMESPACE'])
    def connect():
        print("Connected")
        emit('status', {'data': 'Connected'})

    pubsub = r.pubsub()
    Greenlet.spawn(sub, pubsub)
    return socketio
