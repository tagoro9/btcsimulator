# #Business Model

# Load dependencies

Model = require 'models/base/model'
Country = require 'models/country'
State = require 'models/state'
Town = require 'models/town'
Category = require 'models/category'
PageableCollection = require 'models/base/pageable-collection'
User = require 'models/user'
config = require 'config'

country = Country.Model.find id:'73'
country = new Country.Model id: '73' unless country?
state = State.Model.find id: '38'
state = new State.Model id: '38' unless state?

towns = new Town.Collection()
towns.url = config.apiRoot + 'states/38/towns'

users = new User.Collection()

module.exports.Model = class BusinessModel extends Model
	urlRoot:  config.api.host + config.api.root + 'businesses'
	toStringAttr: 'name'
	save: ->
		telephone = @get 'telephone'
		email = @get 'email'
		notAvailable = i18n.t "views.business.tabs.contact.not-available"
		@set  'telephone', null if telephone? and (telephone.trim() is '' or telephone is notAvailable)
		@set 'email', null if email? and (email.trim() is '' or email is notAvailable)
		@set 'owner_id', Chaplin.mediator.user
		super
	relations: [
		{
			type: Backbone.HasOne
			key: 'country_id'
			includeInJSON: 'id'
			relatedModel: Country.Model
		}
		{
			type: Backbone.HasOne
			key: 'state_id'
			includeInJSON: 'id'
			relatedModel: State.Model
		}
		{
			type: Backbone.HasOne
			key: 'town_id'
			includeInJSON: 'id'
			relatedModel: Town.Model
		}
		{
			type: Backbone.HasOne
			key: 'owner_id'
			autoFetch: true
			includeInJSON: 'id'
			relatedModel: User.Model
		}	
		{
			type: Backbone.HasOne
			key: 'category_id'
			includeInJSON: 'id'
			relatedModel: Category.Model
		}	
	]
	schema:
		name:
			title: 'Nombre'
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']	
		description:
			title: 'Descripción'
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']		
		town_id:
			title: 'Ciudad'
			type: 'Select'
			options: towns
			editorClass: 'form-control'
			validators: ['required']	
		address:
			editorClass: 'form-control'
			validators: ['required']	
		zip_code:
			title: 'Codigo postal'
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']	
		telephone:
			title: 'Teléfono'
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']	
		email:
			title: 'Email'
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']	
		opening_hours:
			title: 'Horario:'
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']	
		lat:
			title: 'Latitud'
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']	
		lon:
			title: 'Longitud'
			type: 'Text'
			editorClass: 'form-control'
			validators: ['required']	
		owner_id: 
			title: 'Propietario'
			type: 'Select'
			options: users
			editorClass: 'form-control'
			validators: ['required']	


module.exports.Collection = class BusinessesCollection extends PageableCollection
	model: BusinessModel
	url: config.api.host + config.api.root + 'businesses'