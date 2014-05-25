# #Application-specific view [helpers](http://handlebarsjs.com/#helpers)
config = require 'config'
# Map helpers
# -----------

# Make 'with' behave a little more mustachey.
Handlebars.registerHelper 'with', (context, options) ->
  if not context or Handlebars.Utils.isEmpty context
    options.inverse(this)
  else
    options.fn(context)

# Inverse for 'with'.
Handlebars.registerHelper 'without', (context, options) ->
  inverse = options.inverse
  options.inverse = options.fn
  options.fn = inverse
  Handlebars.helpers.with.call(this, context, options)

# Get Chaplin-declared named routes. {{url "likes#show" "105"}}
Handlebars.registerHelper 'url', (routeName, params..., options) ->
  Chaplin.helpers.reverse routeName, params

# I18next Helper
Handlebars.registerHelper 't', (path) ->
  result = i18n.t(path)
  new Handlebars.SafeString(result);  

# Convert time to human
Handlebars.registerHelper 'humanTime', (time) ->
  moment.utc(time, "YYYY-MM-DD HH:mm:ss").local().lang(i18n.lng()).fromNow() 

# Convert time to calendar time
Handlebars.registerHelper 'calendarTime', (time) ->
  moment.utc(time, "YYYY-MM-DD HH:mm:ss").local().lang(i18n.lng()).calendar()