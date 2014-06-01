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
    @$('#configuration').transition x: @$('.jumbotron').width() + 100, duration: 500, easing: 'easeInOutCubic', () =>
      @$('#in-progress').css 'height', @$('#configuration').outerHeight()
      @$('#configuration').css 'display', 'none'
      @$('#in-progress').css 'opacity', 0
      @$('#in-progress').css 'display', 'block'
      @$('#in-progress').transition opacity: 1
      @startSpinner()

  # Inspired by http://codepen.io/joshy/pen/cojbD
  startSpinner: ->
    $('[class^="circle-"]').animate({opacity:1},500)
    $path = $('.atom-1')
    path = $path[0]
    $path2 = $('.atom-2')
    path2 = $path2[0]
    $path3 = $('.atom-3')
    path3 = $path3[0]
    $obj = $('.circle-1')
    $obj2 = $('.circle-2')
    $obj3 = $('.circle-3')
    pathLength = path.getTotalLength()
    pathLength2 = path2.getTotalLength()
    pathLength3 = path3.getTotalLength()

    tween = new TWEEN.Tween({ length: 0  })
    .to({ length: pathLength }, 1500)
    .onUpdate(() ->
      point = path.getPointAtLength(@length)
      $obj.css({
        'transform': 'translate(' + point.x + 'px,' + point.y + 'px)'
      })
    ).repeat(999999999).start()

    tween2 = new TWEEN.Tween({ length: 0  })
    .to({ length: pathLength2 }, 1500)
    .onUpdate(() ->
      point2 = path2.getPointAtLength(@length)
      $obj2.css({
        'transform': 'translate(' + point2.x + 'px,' + point2.y + 'px)'
      })
    ).repeat(999999999).start()

    tween3 = new TWEEN.Tween({ length: 0  })
    .to({ length: pathLength3 }, 1500)
    .onUpdate(() ->
      point3 = path3.getPointAtLength(@length)
      $obj3.css({
        'transform': 'translate(' + point3.x + 'px,'+ point3.y + 'px)'
      })
    ).repeat(999999999).start()

    animate = () ->
      requestAnimationFrame animate
      TWEEN.update()

    animate()



  remove: ->
    super
    @unstickit()