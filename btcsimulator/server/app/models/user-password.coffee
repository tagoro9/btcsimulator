# Model for a user password
Model = require 'models/base/model'
config = require 'config'

module.exports.Model = class UserPassword extends Model
	url: -> config.api.host + config.api.root + "users/#{@id}/password"
	schema: ->
		oldPassword:
			title: i18n.t "views.profile.form.oldPassword"			
			type: 'Password'
			editorClass: 'form-control'
			validators: ['required']
		password:
			title: i18n.t "views.profile.form.password"
			type: 'Password'
			editorClass: 'form-control'
			validators: [{type: 'match', field: "passwordConfirmation"}, 'required']
		passwordConfirmation:
			title: i18n.t "views.profile.form.confirmation"
			type: 'Password'
			editorClass: 'form-control'
			validators: [{type: 'match', field: "password"}, 'required']	