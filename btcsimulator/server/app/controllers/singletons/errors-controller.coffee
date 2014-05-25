errors = require('config').errors

# # Errors controller
# This contoller will listen to ajax errors and handle them in very different ways
module.exports = class ErrorsController extends Chaplin.Controller
	
	initialize: () ->
		super
		# Listen to all Ajax errors
		$(document).ajaxError @handleAjaxErrors

	handleAjaxErrors: (event, response, request) =>
		# Act depending on the HTTP response code
		# We first check the error code
		if response.responseJSON?
			@handleErrorByCode parseInt(response.responseJSON.code), response.status
		else
			@handleErrorByStatusCode response.status


	handleErrorByCode: (code, status) ->
		switch code
			when errors.accountExpired
				# Publish the account expired event
				@publishEvent "account-expired"
			else		
				@handleErrorByStatusCode status

	handleErrorByStatusCode: (status) ->
		switch status
			# If none matches check status code
			when 401
				# Publish the unauthorized event
				@publishEvent "unauthorized"		

