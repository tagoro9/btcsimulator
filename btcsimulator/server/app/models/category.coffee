# #Country model

# Load all dependencies
Model = require 'models/base/model'
PageableCollection = require 'models/base/pageable-collection'
config = require 'config'

module.exports.Model = class CategoryModel extends Model
	urlRoot: config.api.host + config.api.root + 'categories'
	toStringAttr: 'name'

module.exports.Collection = class CategoriesCollection extends PageableCollection
	model: CategoryModel
	url: config.api.host + config.api.root + 'categories'