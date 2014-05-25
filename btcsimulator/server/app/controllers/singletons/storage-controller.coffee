module.exports = class StorageController extends Chaplin.Controller

	initialize: () ->
		super
		@subscribeEvent "!storage:get", @getKey
		@subscribeEvent "!storage:set", @setKey

	getKey: (key, deserialize = false) ->
		item = localStorage.getItem key
		item = JSON.parse(item) if deserialize
		Chaplin.mediator[key] = item
		@publishEvent "storage:#{key}", item

	setKey: (key, value, serialize = false) ->
		if value?
			if serialize
				localStorage.setItem key, JSON.stringify value
			else
				localStorage.setItem key, value
		else
			localStorage.removeItem key, value
		Chaplin.mediator[key] = value
		@publishEvent "storage:#{key}", value