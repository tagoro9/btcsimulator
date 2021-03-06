View = require 'views/base/view'
template = require 'templates/layout/header'
Summary = require('models/summary')

module.exports = class HeaderView extends View
  tagName: 'header'
  className: 'navbar navbar-inverse navbar-fixed-top'
  region: 'header'
  template: template
  attributes:
    "role": "navigation"
  initialize: ->
    @listenTo @, 'addedToDOM', @changeURLFirstTime
    @subscribeEvent "router:match", @handleUrlChange

  handleUrlChange: (url) ->
    @changeURL path: url.path.split("/")[0]



  changeURL: (url) ->
    path = "/" + url.path
    @$('li').removeClass 'active'
    @$("li a").each () -> $(@).parent().addClass('active') if $(@).attr('href').indexOf(path) >= 0 and path.length > 1

  hashOrRoot: (path) =>
    path = path.split("/")[0]
    if _.any @$('a'), ((ele) ->  "/#{path}".indexOf($(ele).attr('href')) >= 0) then path else ""

  changeURLFirstTime: ->
      setTimeout () =>
        @changeURL path: @hashOrRoot window.location.pathname.substring 1
      , 50


