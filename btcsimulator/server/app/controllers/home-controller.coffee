Controller = require 'controllers/base/controller'

module.exports = class HomeController extends Controller

  name: 'HomeController'
  layout: 'simple'

  index: ->
    @viewAndModel 'Index'