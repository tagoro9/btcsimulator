Model = require 'models/base/model'
config = require 'config'

module.exports.Model = class Summary extends Model
  urlRoot: config.api.host + config.api.root + 'summary'
  getBlockRatio: ->
    return 0 unless @get('blocks')? and @get('days')?
    seconds = 24 * 3600 * parseInt @get('days')
    blocks = parseInt @get 'blocks'
    blocksEvery = seconds / blocks
    [Math.floor(blocksEvery / 60), Math.floor(blocksEvery % 60)]