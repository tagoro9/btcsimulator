Controller = require 'controllers/base/controller'

module.exports = class HomeController extends Controller

	name: 'SimulatorController'

	network: -> @viewAndCollection 'Network'