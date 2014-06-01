View = require('views/base/view')
template = require('templates/simulation/simulation')

module.exports = class SimulationView extends View
  template: template
  className: 'simulation'
  events:
    "click #start-simulation": "handleStartClick"
  bindings:
    "#miners-number-hint": 'miners'
    "#days-number-hint": 'days'

  initialize: ->
    super
    @model.set 'miners', 3
    @model.set 'days', 3

  render: ->
    super
    @$("select").selectpicker style: 'btn-hg btn-primary', menuStyle: 'dropdown-inverse'
    @$('#miners-number').slider
      min: 1
      max: 20
      value: 3
      orientation: 'horizontal'
      range: "min"
      change: @handleMinersNumberChange
    @$('#days-number').slider
      min: 1
      max: 20
      value: 3
      orientation: 'horizontal'
      range: "min"
      change: @handleDaysNumberChange
    @stickit()

  handleMinersNumberChange: (e, ui) => @model.set 'miners', $(e.target).slider("value")
  handleDaysNumberChange: (e, ui) => @model.set 'days', $(e.target).slider("value")

  handleStartClick: ->
    
  remove: ->
    super
    @unstickit()