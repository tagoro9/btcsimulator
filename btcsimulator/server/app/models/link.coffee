Model = require 'models/base/model'
Collection = require 'models/base/collection'
config = require 'config'

module.exports.Model = class Link extends Model
  urlRoot: config.api.host + config.api.root + 'links'

module.exports.Collection = class Links extends Collection
  url: config.api.host + config.api.root + 'links'
  model: Link
