Model = require 'models/base/model'
Collection = require 'models/base/collection'
config = require 'config'
Link = require 'models/link'

module.exports.Model = class Miner extends Model
  urlRoot: config.api.host + config.api.root + 'miners'
  relations: [
    {
      type: Backbone.HasMany
      key: 'links'
      relatedModel: Link.Model
      collectionType: Link.Collection
    }
  ]

module.exports.Collection = class Miners extends Collection
  url: config.api.host + config.api.root + 'miners'
  model: Miner
  getNetwork: ->
    nodes = @map (miner) -> id: parseInt(miner.id) - 1, group: parseInt(miner.id) - 1, hashrate: miner.get('hashrate')
    links = _.flatten @map (miner) -> miner.get('links').map (link) -> source: parseInt(link.get('origin')) - 1, target: parseInt(link.get('destination')) - 1, value: parseFloat(miner.get('hashrate'))
    nodes: nodes, links: links


