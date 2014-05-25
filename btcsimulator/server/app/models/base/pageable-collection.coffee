utils = require 'lib/utils'
Model = require 'models/base/model'

# Abstract class which extends both the Chaplin and BackbonePageable collections
# in order to add some functionality.
module.exports = class Collection extends Backbone.PageableCollection
	
	_.extend @prototype, Chaplin.EventBroker
	
	model: Model
	# Pagination mode will be server as default
	mode: 'server'
	# Modify filter query parameters to work with our API
	queryParams:
		totalPages: 'pageCount'
		totalRecords: 'count'
		sortKey: "sort"
		order: "direction"
		pageSize: 'limit'
		directions:
			"-1": "asc"
			"1": "desc"
	
	serialize: ->
		@map utils.serialize
	
	disposed: false

	dispose: ->
		return if @disposed

		# Fire an event to notify associated views.
		@trigger 'dispose', this

		# Empty the list silently, but do not dispose all models since
		# they might be referenced elsewhere.
		@reset [], silent: true

		# Unbind all global event handlers.
		@unsubscribeAllEvents()

		# Unbind all referenced handlers.
		@stopListening()

		# Remove all event handlers on this module.
		@off()

		# Remove model constructor reference, internal model lists
		# and event handlers.
		properties = [
			'model',
			'models', '_byId', '_byCid',
			'_callbacks'
		]
		delete this[prop] for prop in properties

		# Finished.
		@disposed = true

		# You’re frozen when your heart’s not open.
		Object.freeze? this	
