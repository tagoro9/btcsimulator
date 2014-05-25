Controller = require 'controllers/base/controller'

module.exports = class HomeController extends Controller
	
	name: 'HomeController'

	index: -> @viewAndModel 'Index'