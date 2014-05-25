require 'lib/view-helper' # Just load the view helpers, no return value

module.exports = class View extends Chaplin.View
	autoRender: true
	autoAttach: true
	# Precompiled templates function initializer.
	getTemplateFunction: ->
		@template
	initialize: (options) ->
		super
		@model.fetch() if @model and options.autoFetch
		@listenTo @, 'addedToDOM', @finishProgress

	finishProgress: -> @publishEvent "!progress:done"
		
