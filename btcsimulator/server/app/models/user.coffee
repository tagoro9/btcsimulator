# User model

# Load dependencies
Model = require 'models/base/model'
PageableCollection = require 'models/base/pageable-collection'
config = require 'config'

# User model
module.exports.Model = class UserModel extends Model
	urlRoot: config.api.root + 'users'
	toStringAttr: 'name'
	save: ->
		@set 'role', 'owner'
		super

module.exports.Collection = class UsersCollection extends PageableCollection
	url: config.api.root + 'users'
	model: UserModel