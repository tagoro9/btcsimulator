# #Offer Model

# Load all dependencias

Model = require 'models/base/model'
Business = require 'models/business'
PageableCollection = require 'models/base/pageable-collection'
DateEditor = require 'lib/editors/date-editor'
config = require 'config'
DateFormatter = require 'lib/live-edit/formatters/date-formatter'

module.exports.Model = class OfferModel extends Model
	urlRoot: config.api.host + config.api.root + 'offers'
	relations: [
		{
			type: Backbone.HasOne
			key: 'business_id'
			relatedModel: Business.Model
			autoFetch: true
			includeInJSON: 'id'
		}
		{
			type: Backbone.HasOne
			key: 'type_id'
			relatedModel: Model
			autoFetch: false
			includeInJSON: 'id'
		}
		{
			type: Backbone.HasOne
			key: 'size_id'
			relatedModel: Model
			autoFetch: false
			includeInJSON: 'id'
		}
	]

	schema:
		description	: 
			title: i18n.t("models.offer.schema.description")
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']			
		start:
			title: i18n.t("models.offer.schema.start")
			type: DateEditor
			validators: ['required']						
		end:
			title: i18n.t("models.offer.schema.end")
			type: DateEditor
			validators: ['required']									
		price:
			title: i18n.t("models.offer.schema.price")		
			type: 'Number'
			editorClass: 'form-control'
			validators: ['required']						
		offer:
			title: i18n.t("models.offer.schema.offer")
			type: 'Number'
			editorClass: 'form-control'
			validators: ['required']						

	initialize: () ->
		super
		businessId = Chaplin.mediator.businesses[0]
		@set 'type_id', Model.find(id: 1) or new Model(id: 1)
		@set 'size_id', Model.find(id: 2) or new Model(id: 2)
		@set 'business_id', Business.Model.findOrCreate(id: businessId)
		@set 'start', moment.utc().format "YYYY-MM-DD HH:mm:ss" unless @get('start')?
		@set 'end', moment.utc().format "YYYY-MM-DD HH:mm:ss" unless @get('end')?

	getChecks: () ->
		$.get("#{@urlRoot}/#{@id}/checks").done (data) =>
			@set 'checks', data
		

	extraProperties: ['restaurante_id', 'descripcion', 'precio_oferta', 'precio_real', 'fecha_inicio', 'fecha_fin', 'foto', 'talla', 'restaurante_nombre', 'restaurante_latitud', 'restaurante_longitud', 'distancia']

	save: ->
		@set('photo', '/img/files/foodicious.png') if @isNew()
		checks = @get 'checks'
		@unset 'checks'
		super
		@set 'checks', checks

	toJSON: ->
		jsonData = super
		_.omit jsonData, @extraProperties

module.exports.Collection = class OffersCollection extends PageableCollection
	model: OfferModel
	url: => config.api.host + config.api.root + "businesses/#{@id}/offers/"
	mode: 'infinite'
	state:
		pageSize: 20
		sortKey: 'modified'
		order: 1
	initialize: (data, options) ->
		super
		if options.id?
			@id = options.id
		else
			throw new Error "You must specifiy an business id for the offers collection"
	parseLinks: (response, xhr) ->
		url = @url()
		pagination = response[0]
		nextUrl = "#{url}?page=#{pagination.page + 1}"
		next: nextUrl unless @state.currentPage is @state.lastPage

	parse: ->
		return if @disposed
		resp = super
		@state.totalRecords -= @state.pageSize		
		@state.lastPage = parseInt Math.ceil @state.totalRecords / @state.pageSize
		@state.totalPage = @state.lastPage
		resp

	comparator: (self) -> - moment.utc(self.get('modified')).format "X"

		