View = require 'views/base/view'
template = require 'templates/layout/header'

module.exports = class HeaderView extends View
  tagName: 'header'
  className: 'navbar navbar-inverse navbar-fixed-top'
  region: 'header'
  template: template
  attributes:
    "role": "navigation"

