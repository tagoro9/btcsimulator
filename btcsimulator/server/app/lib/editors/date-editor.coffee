module.exports = class DateEditor extends Backbone.Form.editors.Base

	tagName: 'p'

	events:
		'change': -> this.trigger 'change', this
		'focus': -> this.trigger 'focus', this
		'blur': -> this.trigger 'blur', this

	initialize: (options) ->
		super
		@pickerId = "datePicker" + _.uniqueId() 

	render: ->
		@$el.html @template @getTemplateData()
		@setValue @value
		@startDatePicker()
		@

	startDatePicker: ->
		@picker = @$("##{@pickerId}").datetimepicker
			language: i18n.lng()
			showToday: true
			format: "HH:mm:ss DD/MM/YYYY"

	getTemplateData: ->
		id: @pickerId

	template: _.template """
            <div class='input-group date' data id='<%= id %>'>
                <input type='text' class="form-control" />
                <span class="input-group-addon"><i class="fa fa-calendar"></i>
                </span>
            </div>
	"""

	getValue: ->
		moment(@$('input').val(), "HH:mm:ss DD/MM/YYYY").utc().format "YYYY-MM-DD HH:mm:ss"

	setValue: (value) ->
		@$('input').val moment.utc(value, "YYYY-MM-DD HH:mm:ss").local().format "HH:mm:ss DD/MM/YYYY"

	focus: ->
		@$el.focus() unless @hasFocus

	blur: ->
		@$el.blur() unless !@.hasFocus

