config =
	# API configuration
	api: 
		host: 'http://localhost:5000'
		root: '/'
	# Keys to be loaded in the mediator at application initialization
	init:
		keys: []
		# List of singleton controllers to be initialized when app is loading
		controllers: [
			'Progress'
			'Storage'
			'Errors'
			'Session'
		]

# Prevent creating new properties and stuff.
Object.seal? config

module.exports = config