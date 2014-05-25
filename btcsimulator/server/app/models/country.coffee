# #Country model

# Load all dependencies
Model = require 'models/base/model'
Collection = require 'models/base/collection'
config = require 'config'

module.exports.Model = class CountryModel extends Model
	urlRoot: config.api.host + config.api.root + 'countries'
	toStringAttr: 'name'

module.exports.Collection = class CountriesCollection extends Collection
	model: CountryModel
	url: config.api.host + config.api.root + 'countries'