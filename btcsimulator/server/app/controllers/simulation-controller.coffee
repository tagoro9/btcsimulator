Controller = require 'controllers/base/controller'

module.exports = class SimulationController extends Controller

  name: 'SimulationController'

  network: ->
    @viewAndCollection 'Network', 'Miner'


  blocks: ->
    @viewAndCollection 'Blocks', 'Miner'