View = require 'views/base/view'
template = require 'templates/stats/block'

module.exports = class BlockView extends View
  template: template
  className: 'chain-block'
  tagName: 'tr'
  getTemplateData: -> id: @cid
  bindings: ->
    bindings = {}
    bindings["#block-#{@cid}-hash"] =
      observe: 'hash'
      onGet: (val) -> val.substr(0,10) + "..." if val?
    bindings["#block-#{@cid}-height"] =
      observe: 'height'
    bindings["#block-#{@cid}-miner"] =
      observe: 'miner'
    bindings["#block-#{@cid}-size"] =
      observe: 'size'
      onGet: (val) -> "#{(val / 1024).toFixed(2)} KB" if val?
    bindings["#block-#{@cid}-time"] =
      observe: 'time'
      onGet: (val) ->
        if val?
          now = moment()
          later = moment(now).add 'seconds', Math.ceil(val)
          @secondsToTime later.diff(now) / 1000
    bindings

  secondsToTime: (seconds) ->
    minutes = Math.floor seconds / 60
    hours = Math.floor minutes / 60
    minutes = minutes % 60
    days = Math.floor hours / 24
    hours = hours % 24
    seconds = seconds % 60
    str = ""
    str += "#{days}d " if days > 0
    str += "#{hours}h " if hours > 0
    str += "#{minutes}m " if minutes > 0
    str += "#{seconds}s " if seconds > 0
    str

  render: ->
    super
    @stickit @model, @bindings()