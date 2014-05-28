module.exports = (match) ->
  match '', 'home#index', name: 'index'
  match 'simulation/network', 'simulation#network', name: 'network'
  match 'simulation/blocks', 'simulation#blocks', name: 'blocks'