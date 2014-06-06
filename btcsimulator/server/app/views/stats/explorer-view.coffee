CollectionView = require 'views/base/collection-view'
BlockView = require 'views/stats/block-view'
template = require 'templates/stats/explorer'
Miner = require 'models/miner'
Collection = require 'models/base/collection'

module.exports = class Explorer extends CollectionView
  template: template
  id: 'explorer'
  className: 'container simulation-info'
  listSelector: '#blocks-container'
  itemView: BlockView
  events:
    "keydown #block-search": "handleSearch"
    "click #next-chain-page": "handleNextChainPageClick"
  initialize: ->
    @handleSearch = _.debounce @handleSearch, 100
    $('window').resize @adjustHeight()
    @shadowCollection = @collection
    @collection = new Collection()
    super
    @listenTo @, 'addedToDOM', @adjustHeight
    # If collection has no head, we need to get the chain head from the summary
    @listenTo @shadowCollection, 'reset', @handleDataReset
    if @shadowCollection.chainHead?
      @fetchData()
    else
      @miners = new Miner.Collection()
      @miners.fetch(reset: true).done @handleHeadFetched
      @handleSearch = _.debounce @handleSearch, 100

  createFilter: (hash) -> (item, index) -> item.get('hash').indexOf(hash) >= 0

  handleSearch: (e) ->  @filter @createFilter $(e.target).val()

  adjustHeight: -> @$('table').height @$el.height() - @$('#explorer-title').height() - 4 * @$('#explorer-controls').height() - @$('.table-header').height()

  handleHeadFetched: =>
    @shadowCollection.chainHead = @miners.getHead()
    @fetchData()

  fetchData: ->
    @shadowCollection.fetch reset: true

  handleDataReset: (collection) ->
    @collection.add collection.toJSON()
    @adjustHeight()
    @$('#next-chain-page').addClass('disabled') if collection.last().get('miner') is '-1'

  handleNextChainPageClick: (e) ->
    e.preventDefault()
    @getNextPage() if @shadowCollection.last().get('miner') isnt '-1'

  getNextPage: ->
    @shadowCollection.chainHead = @shadowCollection.last().get('prev')
    @fetchData()