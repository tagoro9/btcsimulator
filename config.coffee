exports.config =
  # See http://brunch.io/#documentation for docs.
  paths:
    public: 'btcsimulator/server/public'
    watched: ['btcsimulator/server/app', 'btcsimulator/server/vendor', 'btcsimulator/server/test']
  files:
    javascripts:
      joinTo:
        'javascripts/app.js': /^btcsimulator\/server\/app/
        'javascripts/vendor.js': /^(bower_components|btcsimulator\/server\/vendor)/
        'test/test.js': /^btcsimulator\/server\/test/
      order:
        after: [
          'btcsimulator/server/test/vendor/scripts/test-helper.js'
        ]

    stylesheets:
      joinTo:
        'stylesheets/app.css': /^(?!test)/
        'test/test.css': /^btcsimulator\/server\/test/
      order:
        after: [
          'btcsimulator/server/vendor/styles/helpers.css'
        ]

    templates:
      joinTo: 'javascripts/app.js'

  modules:
    nameCleaner: (path) ->
      path.replace(/^btcsimulator\/server\/app\//, '')