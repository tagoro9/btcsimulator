Controller = require 'controllers/base/controller'

module.exports = class SimulationController extends Controller

  name: 'SimulationController'

  layout: 'simple'

  new: -> @viewAndModel 'Simulation', 'Simulation'