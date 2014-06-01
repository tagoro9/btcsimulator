module.exports = (match) ->
  match '', 'home#index', name: 'index'
  match 'simulation', 'simulation#new', name: 'simulation'
  match 'simulation/network', 'simulation#network', name: 'network'
  match 'simulation/blocks', 'simulation#blocks', name: 'blocks'