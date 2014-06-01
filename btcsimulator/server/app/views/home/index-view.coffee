View = require('views/base/view')
template = require('templates/home/index')

module.exports = class IndexView extends View
  template: template
  className: 'home'