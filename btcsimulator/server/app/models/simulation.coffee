Model = require 'models/base/model'
config = require 'config'

module.exports.Model = class Simulation extends Model
  urlRoot: config.api.host + config.api.root + 'simulation'