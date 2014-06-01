config = require 'config'

# # Base controller
# This controller won't render any view (even layouts) until it receives 
# the continue event. This event can be triggered for example by the **SessionController** which
# will intercept the URL visited and decide if current user has permissions to access it.
module.exports = class Controller extends Chaplin.Controller

  name: 'Controller'

  # ## Initialization

  # List of layouts in the application
  layouts:
    default: [
      'site'
      'header'
      'sidebar'
    ]
    simple: [
      'simple-site'
      'simple-header'
    ]
  # Assign default layout to all the controller views
  layout: 'default'
  # Default region where to render a view
  region: 'main'

  initialize: () ->
    super
    # Listen to redirection request events
    @subscribeEvent "login", @handleLogin
    @subscribeEvent "logout", @handleLogout
    @subscribeEvent "create-business", @handleCreateBusiness
    @subscribeEvent "dashboard", @handleDashboard
    @subscribeEvent "subscribe", @handleSubscribe
    # Listen to the global *continue* event
    @subscribeEvent "continue", @handleContinue

  # ## Filters

  # Function to be run before every action
  beforeAction: (params, route) ->
    # Start Progress
    @publishEvent "!progress:start"
    # Store current route so we can publish it when a view is loaded
    @route = route
    # Create a deferred object wich will be resolved after the continue event is triggered
    @continueDeferred = $.Deferred()
    # Trigger event to notify singleton controllers
    @publishEvent "controller:match", route
    # Create layout if any after the continue event
    @waitForContinue () ->
      @createLayout @layouts[@layout] if @layout?

  # ## Utility functions

  # Create a layout given an array of regions under the following conventions:
  # * Regions represent views
  # * Regions are rendered in order (this order is important since regions can define another regions inside)
  # * Views are stored in views/layout/<region>-view
  createLayout: (layout) ->
    @reuse region, require("views/layout/#{region}-view") for region in layout

  # Build view options from controller properties
  buildViewOptions: () ->
    options = {}
    options.collection = @collection if @collection?
    options.model = @model if @model?
    options.region = @region if @region?
    options.container = @container if @container?
    options

  # Get dash syle controller name
  getName: ->
    @name.replace("Controller", '').dasherize()

  # Create a view and a model given their names following the next conventions:
  # * Views are stored in views/<controller name>/<name>-view
  # * Models are stored in models/<name>
  viewAndModel: (view, model, modelParameters) ->
    @waitForContinue () =>
      if model?
        modelClass = require("models/#{model.toLowerCase()}").Model
        if modelParameters?
          @model = modelClass.findOrCreate modelParameters
        else
          @model = new modelClass
      viewClass = require("views/#{@getName()}/#{view.toLowerCase()}-view")
      @view = new viewClass @buildViewOptions()

  # Create a view and a collection given their names following the next conventions:
  # * Views are stored in views/<controller name>/<name>-view
  # * Collections are stored in models/<name>
  viewAndCollection: (view, collection, colParameters) ->
    if collection?
      collectionClass = require("models/#{collection.toLowerCase()}").Collection
      @collection = new collectionClass null, colParameters
    viewClass = require("views/#{@getName()}/#{view.toLowerCase()}-view")
    @view = new viewClass @buildViewOptions()

  # ## Event handlers

  # Call all the registered handlers for the continue event in order
  handleContinue: ->
    # Resolve the deferred
    @continueDeferred.resolve()

  # Add a resolve handler to the continue deferred object
  waitForContinue: (handler) ->
    @continueDeferred.done _.bind handler, @

  # Redirect to a certain route by its name
  redirectToName: (name) ->
    # Reject the deferred so the layout is not created after redirection
    @continueDeferred.reject()
    # Redirect to the requested page
    @redirectTo name: name
    @dispose()

  # Handle a logged in status event
  handleLogin: ->
    @redirectToName 'dashboard'

  # Handle a logout status event
  handleLogout: ->
    @redirectToName 'login'

  # Handle a dashboard event
  handleDashboard: ->
    @redirectToName 'dashboard'

  # Handle a create-business event
  handleCreateBusiness: ->
    @redirectToName 'welcome'

  # Handle a subscribe event
  handleSubscribe: ->
    @redirectToName 'payment'

  # ## Disposal

  # Destroy the controller
  dispose: ->
    super
    # Reject the deferred if it was never resolved
    @continueDeferred.reject() unless 'resolved' is @continueDeferred.state() or 'rejected' is @continueDeferred.state()
    Backbone.Relational.store.reset()