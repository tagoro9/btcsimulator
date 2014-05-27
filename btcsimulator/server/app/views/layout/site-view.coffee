View = require 'views/base/view'
template = require 'templates/layout/site'

# Site view is a top-level view which is bound to body.
module.exports = class SiteView extends View
	container: 'body'
	id: 'site-container'
	regions:
		header: '#header-container'
		main: '#page-container .wrapper'
		sidebar: "#sidebar-container"
	template: template
