Model = require 'models/base/model'
Collection = require 'models/base/collection'
config = require 'config'

module.exports.Model = class StatModel extends Model

module.exports.Collection = class StatsCollection extends Collection
	model: StatModel
	initialize: (models, options) ->
		super
		_.merge @, _.pick options, ['what', 'business', 'when','type', 'chart', 'year']
		@url = -> config.api.host + config.api.root + "stats/#{@what}/#{@type}/#{@business}/#{@when}/#{@year}"

	prepare: () ->
		if (@chart == 'gauge')
			@generateGaugeData()
		else if (@chart == 'barChart')
			if (@type == 'revenueByTime')
				@generateBarData()
			else if (@type == 'revenue')
				@generateBarRevenuePerOffer()
		else
			@generateGraphData()
	
	generateGaugeData : () ->
		data = []
		opts =
			lines: 2 
			angle: 0 
			lineWidth: 0.48 
			pointer:
				length: 0.6 
				strokeWidth: 0.03
				color: "#{}464646" 
			limitMax: "true" 
			colorStart: "#fa8564"
			colorStop: "#fa8564" 
			strokeColor: "#F1F1F1"
			generateGradient: true
		data.push opts;
		model =  @findWhere 'month' : moment.utc().format("M")
		if model 
			data.push  model.get "total"
		else
			#Hack to make Gauge Work
			Gauge.prototype.displayedValue = 1
			data.push "0"
		data

	generateData: () =>
		data = []
		size = 12
		switch  @when
			when 'month'
				size = 12
			when 'weekday'
				size = 7
		for i in [1..size]
			hash = {}
			hash[@when] = i.toString()
			model = @findWhere(hash)
			if model
				data.push  model.get "total"
			else
				data.push 0
		data

	generateBarDataPerMonth: () =>
		data = [0,0,0,0,0,0,0,0,0,0,0,0]
		_.each @models,(model)->
			month = model.get "month"
			price = parseFloat(model.get "offer") * parseFloat(model.get "total")
			data[month-1] += price
		data
	generateLabels: ()->
		switch @when
			when 'month'
				data = [
					i18n.t "data.months.January"
					i18n.t "data.months.February"
					i18n.t "data.months.March"
					i18n.t "data.months.April"
					i18n.t "data.months.May"
					i18n.t "data.months.June"
					i18n.t "data.months.July"
					i18n.t "data.months.August"
					i18n.t "data.months.September"
					i18n.t "data.months.October"
					i18n.t "data.months.November"
					i18n.t "data.months.December"
				]
			when 'weekday'
				data = [
					i18n.t "data.weekday.Monday"
					i18n.t "data.weekday.Tuesday"
					i18n.t "data.weekday.Wednesday"
					i18n.t "data.weekday.Thursday"
					i18n.t "data.weekday.Friday"
					i18n.t "data.weekday.Saturday"
					i18n.t "data.weekday.Sunday"
				] 

	generateDataSet: (data) ->
		switch @what
			when 'checks'
				if (@type == 'revenueByTime' || @type == 'revenue')
					{
						fillColor : "#d35400",
						strokeColor : "#d35400",
						pointColor : "#d35400",
						pointStrokeColor: "#fff"
						data: data()
					}
				else
					{
						fillColor : "#25a35a",
						strokeColor : "#25a35a",
						pointColor : "#25a35a",
						pointStrokeColor: "#fff"
						data: data()
					}
			when 'visits'
				{
					fillColor : "#3498db",
					strokeColor : "#3498db",
					pointColor : "#3498db",
					pointStrokeColor: "#fff"
					data: data()
				}
			when 'offers'
				{
					fillColor : "#e74c3c",
					strokeColor : "#e74c3c",
					pointColor : "#e74c3c",
					pointStrokeColor: "#fff"
					data: data()
				}

	generateGraphData: () ->
		labels: @generateLabels()
		datasets: [
			@generateDataSet(@generateData)
		]

	generateBarData: () ->
		labels: @generateLabels()
		datasets: [
			@generateDataSet(@generateBarDataPerMonth)
		]
	genRevenue: () ->
		data = @map (model)->
			price = parseFloat(model.get "offer") * parseFloat(model.get "total")
			price: price, offer: model.get('offer_id'), description: model.get 'description'
		sortData =_.sortBy(data, 'price')
		sortData = _(sortData).reverse().value()
		sortData.slice(0,5)

	generateBarRevenuePerOffer: () ->
		labels = []
		dataValue = []
		_.each @genRevenue(), (data, ind) ->
			labels.push data.description
			dataValue.push data.price
		labels: labels
		datasets: [
			@generateDataSet(() -> dataValue)
		]