# Application-specific utilities
# ------------------------------

# Delegate to Chaplin’s utils module.
utils = Chaplin.utils.beget Chaplin.utils

_(utils).extend
	mixOf: (base, mixins...) ->
		class Mixed extends base
		for mixin in mixins by -1 #earlier mixins override later ones
			for name, method of mixin::
				Mixed::[name] = method
		Mixed
#  someMethod: ->

# Prevent creating new properties and stuff.
Object.seal? utils

module.exports = utils
