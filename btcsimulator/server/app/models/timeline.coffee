# #Timeline model

# Load all dependencies
Model = require 'models/base/model'
PageableCollection = require 'models/base/pageable-collection'
config = require 'config'

module.exports.Model = class TimelineModel extends Model
	toStringAttr: 'name'

module.exports.Collection = class TimelineCollection extends PageableCollection
	model: TimelineModel
	url: => config.api.host + config.api.root + "timeline/#{@id}"
	mode: 'infinite'
	comparator: 'created'
	state:
		pageSize: 3
		sortKey: 'created'
		order: 1
	initialize: (data, options) ->
		super
		if options.id?
			@id = options.id
		else
			throw new Error "You must specifiy an business id for the timeline"
	parseLinks: (response, xhr) ->
		url = @url()
		pagination = response[0]
		nextUrl = "#{url}?page=#{pagination.page + 1}"
		next: nextUrl unless @state.currentPage is @state.lastPage

	parse: ->
		resp = super
		@state.totalRecords -= @state.pageSize		
		@state.lastPage = parseInt Math.ceil @state.totalRecords / @state.pageSize
		@state.totalPage = @state.lastPage
		resp

		