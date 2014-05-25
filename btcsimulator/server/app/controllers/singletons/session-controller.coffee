# # Session controller
# This controller handles all the session management

config = require 'config'

module.exports = class SessionController extends Chaplin.Controller

	initialize: () ->
		super
		# Listen to all URL matches in a controller so we can act depending on the user permissions and the url visited
		# It is not feasible to listen to the *roter:match* event since this one is trigger before the controllers 
		# initialization and thus we can't force a redirect (an error will be trown by the router)
		@subscribeEvent "controller:match", @handleUrlMatch

	# ## Routes

	# Act whenever the URL changes. 
	# Depending on the url visited and the permissions, this controller will trigger 
	# different events. A normal controller will never compose a layout or create a view
	# until it recieves the continue event.
	handleUrlMatch: (route) ->
		eventName = "continue"
		# Publish the actual event
		@publishEvent eventName					