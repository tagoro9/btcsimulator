View = require('views/base/view')
template = require 'templates/layout/sidebar'

module.exports = class SidebarView extends View
  region: 'sidebar'
  template: template
  initialize: ->
    @listenTo @, 'addedToDOM', @changeURLFirstTime
    @subscribeEvent "router:match", @handleUrlChange

  handleUrlChange: (url) ->
    @changeURL url


  changeURL: (url) ->
    path = "/" + url.path
    @$('a').removeClass 'active'
    @$("a").each () -> $(@).addClass('active') if path.indexOf($(@).attr('href')) >= 0

  hashOrRoot: (path) =>
    if _.any @$('a'), ((ele) ->  "/#{path}".indexOf($(ele).attr('href')) >= 0) then path else ""

  changeURLFirstTime: ->
      setTimeout () =>
        @changeURL path: @hashOrRoot window.location.pathname.substring 1
      , 50