Model = require 'models/base/model'
config = require 'config'

module.exports.Model = class Summary extends Model
  urlRoot: config.api.host + config.api.root + 'summary'