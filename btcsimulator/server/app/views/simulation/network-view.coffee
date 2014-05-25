View = require 'views/base/view'
template = require 'templates/simulation/network'

module.exports = class NetworkView extends View
  template: template
  id: 'network'
  initialize: ->
    @listenTo @collection, 'reset', @createNetwork
    @listenTo @, 'addedToDOM', @fetchNetwork

  fetchNetwork: -> @collection.fetch reset: true

  createNetwork: () ->
    data = @collection.getNetwork()
    width = 900
    height = 500
    color = d3.scale.category20()
    force = d3.layout.force()
    .charge(-120)
    .linkDistance(80)
    .size([width, height])
    .gravity(0.5)

    svg = d3.select('#network').append('svg')
    .attr('width', width)
    .attr('height', height)

    force.nodes(data.nodes)
    .links(data.links)
    .start()

    link = svg.selectAll('.link')
    .data(data.links)
    .enter().append("line")
    .attr("class", "link")
    .style("stroke-width", (d) -> 0.5)
    .style("stroke", '#000')

    node = svg.selectAll(".node")
    .data(data.nodes)
    .enter().append("circle")
    .attr("class", "node")
    .attr("r", (d) -> 5 + 10*d.hashrate)
    .style("fill", (d) -> color(d.id))
    .style("stroke", "#fff")
    .style("stroke-width", "1.5px")
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
