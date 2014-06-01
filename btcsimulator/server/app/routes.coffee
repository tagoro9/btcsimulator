module.exports = (match) ->
  match '', 'home#index', name: 'index'
  match 'simulation', 'simulation#new', name: 'simulation'
  match 'stats/network', 'stats#network', name: 'network'
  match 'stats/blocks', 'stats#blocks', name: 'blocks'