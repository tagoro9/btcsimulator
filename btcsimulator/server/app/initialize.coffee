Application = require 'application'
routes = require 'routes'
config = require 'config'

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
