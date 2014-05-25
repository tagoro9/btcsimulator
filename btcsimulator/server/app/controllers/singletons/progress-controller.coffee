
# Controller which will listen to show progress requests.
module.exports = class NotificationsController extends Chaplin.Controller

	initialize: () ->
		super
		# Listen to progress requests
		@subscribeEvent "!progress:start", @startProgress
		@subscribeEvent "!progress:done", @endProgress
		@subscribeEvent "!progress:inc", @incProgress
		@subscribeEvent "!progress:set", @setProgress

	startProgress: -> NProgress.start()
	endProgress: -> NProgress.done()
	incProgress: -> NProgress.inc()
	setProgress: (val) -> NProgress.set val

