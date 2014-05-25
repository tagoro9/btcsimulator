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
		"right-sidebar": "#right-sidebar-container"
		footer: '#footer-container'
	template: template
	###
	events:
		"click #cc-approve-button-thissite": 'handleCloseCookiesClick'	
		"click #cc-notification-moreinfo": 'handleViewDetailsClick'
	initialize: () ->
		super
		@listenTo @, 'addedToDOM', @displayCookieConsent		
		
	handleCloseCookiesClick: (e) ->
		e.preventDefault()
		@$("#cc-notification").slideToggle()	

	handleViewDetailsClick: (e) ->
		e.preventDefault()
		if $(e.target).html() is 'ver detalles'
			@$("#cc-approve-button-allsites").show()
			$(e.target).html 'ocultar'
		else
			@$("#cc-approve-button-allsites").hide()
			$(e.target).html 'ver detalles'
		@$("#cc-notification-logo").fadeToggle()
		@$("#cc-notification-permissions").slideToggle()
		@$(e.target).blur()

	displayCookieConsent: ->
		if !$.cookie 'policies'
			$.cookie 'policies', 'accept'
			$("#cc-notification").delay(500).slideToggle()		
	###	
