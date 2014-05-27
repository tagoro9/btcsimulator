View = require('views/base/view')
template = require 'templates/layout/sidebar'

module.exports = class SidebarView extends View
  region: 'sidebar'
  template: template