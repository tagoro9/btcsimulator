Model = require 'models/base/model'
Collection = require 'models/base/collection'
config = require 'config'

module.exports.Model = class Block extends Model
  urlRoot: config.api.host + config.api.root + 'blocks'

module.exports.Collection = class Blocks extends Collection
  url: ->
    config.api.host + config.api.root + "chain/#{@chainHead}"
  model: Block
  initialize: (attr, options) ->
    # Get chain head from parameters
    _.merge @, _.pick options, ['chainHead']
    super