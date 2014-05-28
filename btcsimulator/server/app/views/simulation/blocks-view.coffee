View = require 'views/base/view'
template = require 'templates/simulation/blocks'
Summary = require 'models/summary'

module.exports = class BlocksView extends View
  template: template
  id: 'blocks'
  className: 'container simulation-info'
  initialize: ->
    super
    @listenTo @, 'addedToDOM', @fetchData
    @listenTo @collection, 'reset', @renderChart

  fetchData: ->
    @$('.chart-container').height @$('.row').height()
    @collection.fetch reset: true

  processData: (data) ->
    data

  renderChart: () ->
    @chartData = @processData @collection.toJSON()
    unless @chart? then @blocksChart() else @chart.update()

  blocksChart: ->
    @chart = @createChart()
    $(window).on 'resize', @handleWindowResize
    d3.select("#blocks-chart").append('svg').datum(@chartData).call @chart


  xAxisDefinition: ->
    d3.svg.axis().scale(@x).orient("bottom")

  yAxisDefinition: -> d3.svg.axis().scale(@y).orient("left")

  xAxis: ->
    that = @
    xAxis = (selection) ->
      selection.each (data) ->
        container = d3.select(@)
        wrap = container.selectAll("g.x.axis").data [data]
        wrapEnter = wrap.enter().append("g").attr("class", "x axis")
        gEnter = wrapEnter.append("g")
        g = wrap.select("g")
        .attr("transform", "translate(0, #{that.height})")
        .transition()
        .call(that.xAxisDefinition())
    xAxis

  yAxis: ->
    that = @
    yAxis = (selection) ->
      selection.each (data) ->
        container = d3.select(@)
        wrap = container.selectAll("g.y.axis").data [data]
        wrapEnter = wrap.enter().append("g").attr("class", "y axis")
        gEnter = wrapEnter.append("g")
        g = wrap.select("g")
        .transition()
        .call(that.yAxisDefinition())

  createChart: ->
    console.log("Creating chart")
    that = @
    xAxis = @xAxis()
    yAxis = @yAxis()
    margin = @margin = top: 20, right: 0, bottom: 60, left: 40
    padding = @padding = bottom: 60, top: 0, left: 0, right: 0
    chart = (selection) ->
      selection.each (data) ->
        width = that.width = that.$el.width() - margin.left - margin.right - padding.left - padding.right
        height = that.height = that.$('#blocks-chart').height() - margin.top - margin.bottom - padding.bottom - padding.top
        # Get x domain depending on miners
        x_domain = _.map data, (miner) -> miner.id
        # Get maximum number of blocks mined
        y_max = d3.max data, (d) ->d.blocks_mined
        # Get x axis scale
        that.x = x = d3.scale.ordinal().rangeRoundBands([0, width], 0.13).domain(x_domain)
        # Get y axis scale
        that.y = y = d3.scale.linear().range([height, 0], 1).domain [0, 1 + y_max]
        container = d3.select(@)
        wrap = container.selectAll("g.blocks").data [data]
        gEnter = wrap.enter().append("g").attr("class", "blocks").append("g")
        g = wrap.select("g")
        # Move contento to apply margins
        .attr("transform", "translate(#{margin.left}, #{margin.top})")
        .attr("width", width + margin.left + margin.right + padding.left + padding.right)
        .attr("height", height + margin.top + margin.bottom + padding.bottom + padding.top)
        # Add container for the axis
        gEnter.append("g").attr("class", "x-axis-wrap")
        gEnter.append("g").attr("class", "y-axis-wrap")
        # Add x axis
        g.select(".x-axis-wrap").call xAxis
        # Add y axis
        g.select(".y-axis-wrap").call yAxis


    chart