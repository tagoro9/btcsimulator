Application = require 'application'
routes = require 'routes'
config = require 'config'

socket = io.connect(config.api.host + config.api.root + config.api.socket)
socket.on 'connect', () -> console.log("connected to server")
socket.on 'redis', (data) ->
  console.log data
  Chaplin.mediator.publish "redis", data

# Initialize the application on DOM ready event.
$ ->
	# Initialize internationalization first
	i18n.init {fallbackLng: 'en', resGetPath: '/locales/__lng__/__ns__.json'},   () ->

		# Initialize the application
		new Application {
			title: 'Bitcoin simulator',
			controllerSuffix: '-controller',
			routes
		}
