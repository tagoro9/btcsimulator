View = require 'views/base/view'
template = require 'templates/stats/blocks'
Summary = require 'models/summary'

module.exports = class BlocksView extends View
  template: template
  id: 'blocks'
  className: 'container simulation-info'
  blockBindings:
    "#total-blocks": 'blocks'
    "#block-ratio":
      observe: ["blocks", "days"]
      onGet: "getBlockRatio"
  chartModelBindings:
    "#head":
      observe: 'head'
      onGet: (value) -> value.substring 0,10 if value?
      attributes: [
        {
          name: 'href'
          observe: 'head'
          onGet: (value) -> "/stats/explorer/#{value}" if value?
        }
      ]

  initialize: ->
    super
    @summary = new Summary.Model()
    @summary.fetch reset: true
    @listenTo @, 'addedToDOM', @fetchData
    @listenTo @collection, 'reset', @renderChart

  fetchData: ->
    @$('.chart-container').height 300 #@$('.row').height()
    @collection.fetch reset: true

  processData: (data) ->
    [
      {
        key: 'Blocks mined'
        values: data
      }
    ]

  renderChart: () ->
    @chartData = @processData @collection.toJSON()
    @createChartModel()
    @stickit @summary, @blockBindings
    unless @chart? then @blocksChart() else @chart.update()

  createChartModel: ->
    @chartModel = new Chaplin.Model head: @collection.getHead()
    @stickit @chartModel, @chartModelBindings

  blocksChart: ->
    @createChart()

  getBlockRatio: ->
    ratio = @summary.getBlockRatio()
    "#{if ratio[0] > 0 then ratio[0] + i18n.t "global.minutes" else ""} #{if ratio[1] > 0 then ratio[1] + i18n.t "global.seconds" else ""}"

  createChart: ->
    nv.addGraph () =>
      chart = nv.models.discreteBarChart()
      .x((d) -> "Miner #{d.id}")
      .y((d)-> d.blocks_mined)
      .staggerLabels(true)
      .showValues(true)
      .tooltips(false).transitionDuration(350)
      chart.yAxis
      .tickFormat(d3.format('d'))
      chart.valueFormat(d3.format('d'))
      d3.select("#blocks-chart svg").datum(@chartData).call chart
      nv.utils.windowResize(chart.update)
      chart
