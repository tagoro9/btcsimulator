Controller = require 'controllers/base/controller'

module.exports = class StatsController extends Controller

  name: 'StatsController'

  network: ->
    @viewAndCollection 'Network', 'Miner'


  blocks: ->
    @viewAndCollection 'Blocks', 'Miner'