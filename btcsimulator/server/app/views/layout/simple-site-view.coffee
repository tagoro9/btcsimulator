View = require 'views/base/view'
template = require 'templates/layout/simple-site'

# Site view is a top-level view which is bound to body.
module.exports = class SimpleSiteView extends View
	container: 'body'
	id: 'site-container'
	regions:
		'simpleHeader': '#simple-header-container'
		main: '#page-container .wrapper'
	template: template
