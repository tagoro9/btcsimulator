config = require 'config'

# The application object.
module.exports = class Application extends Chaplin.Application
	initialize: () ->
		# Initialize singleton controllers that will be listening to global events
		@initControllers()
		super
		@publishEvent '!storage:get', 'token'		

	initMediator: () ->
		# Load into the mediator all the keys needed for the app to work
		for key in config.init.keys
			Chaplin.mediator[key.key] = null
			@publishEvent '!storage:get', key.key, key.serialized
		super

	# Initialize controllers defined in configuration file
	initControllers: ->
		for controller in config.init.controllers
			controllerClass = require("controllers/singletons/#{controller.toLowerCase()}-controller")
			new controllerClass()