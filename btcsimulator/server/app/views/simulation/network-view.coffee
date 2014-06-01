View = require 'views/base/view'
template = require 'templates/simulation/network'
Summary = require 'models/summary'

module.exports = class NetworkView extends View
  template: template
  id: 'network'
  className: 'container simulation-info'
  summaryBindings:
    "#total-blocks": "blocks"
    "#miners": "miners"
    "#days": "days"
    "#links":
      observe: 'links'
      onGet: (value) -> if value? then value / 2 else ""
    "#events": "events"
  minerBindings:
    "#miner-id": "id"
    "#blocks-mined": "blocks_mined"
    "#hash-rate":
      observe: "hashrate"
      onGet: (value) -> if value? then parseFloat(value).toFixed(2) else ""
    "#miner-links":
      observe: "links"
      onGet: (value) -> if value? then value.length else 0


  initialize: ->
    super
    @summary = new Summary.Model()
    @summary.fetch reset: true
    @listenTo @collection, 'reset', @createNetwork
    @listenTo @, 'addedToDOM', @fetchNetwork

  fetchNetwork: ->
    @$('.chart-container').css 'height', @$('.row').height()
    @collection.fetch reset: true

  render: ->
    super
    @$('#miner-info').hide()
    @stickit @summary, @summaryBindings

  showMiner: (id) ->
    @$('#miner-info').fadeIn()
    @miner = @collection.get id + 1
    @stickit @miner, @minerBindings

  createNetwork: () ->
    that = @
    data = @collection.getNetwork()
    width = @$('#network-chart').width() - 40
    height = @$('#network-chart').height() - 40
    color = d3.scale.category20()
    force = d3.layout.force()
    .charge(-120)
    .linkDistance(180)
    .size([width, height])
    .gravity(0.5)

    resetLinks = ->
      d3.selectAll('.link')
      .transition()
      .style("stroke-width", 0.5)
      .style("stroke", '#000')
      .style("opacity", 0.3)

    hideLinks = (minerId) ->
      d3.selectAll('.link')
      .transition()
      .filter((d) -> d.source.id isnt minerId and d.target.id isnt minerId)
      .style("opacity", 0.1)
      .style("stroke", '#000')
      .style("stroke-width", 0.5)

    focusLinks = (minerId) ->
      d3.selectAll('.link')
      .filter((d) -> d.source.id is minerId or d.target.id is minerId)
      .transition()
      .style("stroke", color minerId)
      .style("stroke-width", 1.5)
      .style("opacity", 1)


    nodeClick = ->
      d3.select(this).classed("node-selected", (d) -> d.selected = !d.selected)
      .each((miner) ->
          d3.selectAll('.node.node-selected').classed("node-selected", (d) ->
            if d.id isnt miner.id
              d.selected = false
            else
              d.selected = true
          )
      )
      resetLinks()
      d3.selectAll('.node.node-selected')
      .each((miner) ->
          that.showMiner miner.id
          hideLinks miner.id
          focusLinks miner.id
      )

    svg = d3.select('#network-chart').append('svg')
    .attr('width', width)
    .attr('height', height)

    g = svg.selectAll('g')
    .data([data])
    .enter().append("g")

    force.nodes(data.nodes)
    .links(data.links)
    .start()

    link = g.selectAll('.link')
    .data(data.links)
    .enter().append("line")
    .attr("class", "link")
    .style("stroke-width", (d) -> 0.5)
    .style("stroke", '#000')
    .style("opacity", 0.3)

    node = g.selectAll(".node")
    .data(data.nodes)
    .enter().append("circle")
    .attr("class", "node")
    .attr("r", (d) -> 5 + 20*d.hashrate)
    .style("fill", (d) -> color(d.id))
    .style("stroke", "#fff")
    .style("stroke-width", "1.5px")
    .on('click', nodeClick)
    .call(force.drag)

    node.append("title")
    .text((d) -> "Miner #{d.id}")

    force.on("tick", () ->
      link.attr("x1", (d) -> d.source.x)
      .attr("y1", (d) -> d.source.y)
      .attr("x2", (d) -> d.target.x)
      .attr("y2", (d) -> d.target.y)

      node.attr("cx", (d) -> d.x)
      node.attr("cy", (d) -> d.y)
    )

    #d3.selectAll(".link")
    #.style("stroke", "#F00")

  remove: ->
    super
    @unstickit()
