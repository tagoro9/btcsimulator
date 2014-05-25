# #State model

# Load all dependencias

Model = require 'models/base/model'
Country = require 'models/country'
Collection = require 'models/base/collection'
config = require 'config'

module.exports.Model = class StateModel extends Model
	urlRoot: config.api.root + 'states'
	toStringAttr: 'name'
	relations: [
		{
			type: Backbone.HasOne
			key: 'country_id'
			relatedModel: Country.Model
			autoFetch: true
		}
	]

module.exports.Collection = class StatesCollection extends Collection
	model: StateModel
	url: config.api.root + 'states'
	urlByParent: (parentId) -> config.apiRoot + "countries/#{parentId}/states"