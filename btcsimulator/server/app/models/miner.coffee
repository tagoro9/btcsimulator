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
  # Get the network structure adapted to a **d3 force layout**
  getNetwork: ->
    nodes = @map (miner) -> id: parseInt(miner.id) - 1, group: parseInt(miner.id) - 1, hashrate: miner.get('hashrate')
    links = _.flatten @map (miner) -> miner.get('links').map (link) -> source: parseInt(link.get('origin')) - 1, target: parseInt(link.get('destination')) - 1, value: parseFloat(miner.get('hashrate'))
    nodes: nodes, links: links
  # Return the most common head
  getHead: ->
    # Group miners by their head
    grouped = @groupBy (miner) -> miner.get('head')
    head = undefined
    max = 0
    _.each grouped, (val, key) ->
      head = key if head is undefined or val.length > max
      max = val.length if val.length > max
    head


