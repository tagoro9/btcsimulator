# #Town model

# Load dependencies
Model = require 'models/base/model'
Collection = require 'models/base/collection'
config = require 'config'
State = require 'models/state'

module.exports.Model = class TownModel extends Model
	urlRoot: config.api.host + config.api.root + 'towns'		
	toStringAttr: 'name'
	relations: [
		{
			type: Backbone.HasOne
			key: 'state_id'
			autoFetch: true
			relatedModel: State.Model
		}
	]		

module.exports.Collection = class TownsCollection extends Collection
	model: TownModel
	url: config.api.host + config.api.root + 'towns'
	urlByParent: (parentId) -> config.apiRoot + "states/#{parentId}/towns"
