(function(/*! Brunch !*/) {
  'use strict';

  var globals = typeof window !== 'undefined' ? window : global;
  if (typeof globals.require === 'function') return;

  var modules = {};
  var cache = {};

  var has = function(object, name) {
    return ({}).hasOwnProperty.call(object, name);
  };

  var expand = function(root, name) {
    var results = [], parts, part;
    if (/^\.\.?(\/|$)/.test(name)) {
      parts = [root, name].join('/').split('/');
    } else {
      parts = name.split('/');
    }
    for (var i = 0, length = parts.length; i < length; i++) {
      part = parts[i];
      if (part === '..') {
        results.pop();
      } else if (part !== '.' && part !== '') {
        results.push(part);
      }
    }
    return results.join('/');
  };

  var dirname = function(path) {
    return path.split('/').slice(0, -1).join('/');
  };

  var localRequire = function(path) {
    return function(name) {
      var dir = dirname(path);
      var absolute = expand(dir, name);
      return globals.require(absolute, path);
    };
  };

  var initModule = function(name, definition) {
    var module = {id: name, exports: {}};
    cache[name] = module;
    definition(module.exports, localRequire(name), module);
    return module.exports;
  };

  var require = function(name, loaderPath) {
    var path = expand(name, '.');
    if (loaderPath == null) loaderPath = '/';

    if (has(cache, path)) return cache[path].exports;
    if (has(modules, path)) return initModule(path, modules[path]);

    var dirIndex = expand(path, './index');
    if (has(cache, dirIndex)) return cache[dirIndex].exports;
    if (has(modules, dirIndex)) return initModule(dirIndex, modules[dirIndex]);

    throw new Error('Cannot find module "' + name + '" from '+ '"' + loaderPath + '"');
  };

  var define = function(bundle, fn) {
    if (typeof bundle === 'object') {
      for (var key in bundle) {
        if (has(bundle, key)) {
          modules[key] = bundle[key];
        }
      }
    } else {
      modules[bundle] = fn;
    }
  };

  var list = function() {
    var result = [];
    for (var item in modules) {
      if (has(modules, item)) {
        result.push(item);
      }
    }
    return result;
  };

  globals.require = require;
  globals.require.define = define;
  globals.require.register = define;
  globals.require.list = list;
  globals.require.brunch = true;
})();
require.register("application", function(exports, require, module) {
var Application, config, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

config = require('config');

module.exports = Application = (function(_super) {
  __extends(Application, _super);

  function Application() {
    _ref = Application.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  Application.prototype.initialize = function() {
    this.initControllers();
    Application.__super__.initialize.apply(this, arguments);
    return this.publishEvent('!storage:get', 'token');
  };

  Application.prototype.initMediator = function() {
    var key, _i, _len, _ref1;
    _ref1 = config.init.keys;
    for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
      key = _ref1[_i];
      Chaplin.mediator[key.key] = null;
      this.publishEvent('!storage:get', key.key, key.serialized);
    }
    return Application.__super__.initMediator.apply(this, arguments);
  };

  Application.prototype.initControllers = function() {
    var controller, controllerClass, _i, _len, _ref1, _results;
    _ref1 = config.init.controllers;
    _results = [];
    for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
      controller = _ref1[_i];
      controllerClass = require("controllers/singletons/" + (controller.toLowerCase()) + "-controller");
      _results.push(new controllerClass());
    }
    return _results;
  };

  return Application;

})(Chaplin.Application);
});

;require.register("config", function(exports, require, module) {
var config;

config = {
  api: {
    host: '',
    root: '/'
  },
  init: {
    keys: [],
    controllers: ['Progress', 'Storage', 'Errors', 'Session']
  }
};

if (typeof Object.seal === "function") {
  Object.seal(config);
}

module.exports = config;
});

;require.register("controllers/base/controller", function(exports, require, module) {
var Controller, config, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

config = require('config');

module.exports = Controller = (function(_super) {
  __extends(Controller, _super);

  function Controller() {
    _ref = Controller.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  Controller.prototype.name = 'Controller';

  Controller.prototype.layouts = {
    "default": ['site', 'header']
  };

  Controller.prototype.layout = 'default';

  Controller.prototype.region = 'main';

  Controller.prototype.initialize = function() {
    Controller.__super__.initialize.apply(this, arguments);
    this.subscribeEvent("login", this.handleLogin);
    this.subscribeEvent("logout", this.handleLogout);
    this.subscribeEvent("create-business", this.handleCreateBusiness);
    this.subscribeEvent("dashboard", this.handleDashboard);
    this.subscribeEvent("subscribe", this.handleSubscribe);
    return this.subscribeEvent("continue", this.handleContinue);
  };

  Controller.prototype.beforeAction = function(params, route) {
    this.publishEvent("!progress:start");
    this.route = route;
    this.continueDeferred = $.Deferred();
    this.publishEvent("controller:match", route);
    return this.waitForContinue(function() {
      if (this.layout != null) {
        return this.createLayout(this.layouts[this.layout]);
      }
    });
  };

  Controller.prototype.createLayout = function(layout) {
    var region, _i, _len, _results;
    _results = [];
    for (_i = 0, _len = layout.length; _i < _len; _i++) {
      region = layout[_i];
      _results.push(this.reuse(region, require("views/layout/" + region + "-view")));
    }
    return _results;
  };

  Controller.prototype.buildViewOptions = function() {
    var options;
    options = {};
    if (this.collection != null) {
      options.collection = this.collection;
    }
    if (this.model != null) {
      options.model = this.model;
    }
    if (this.region != null) {
      options.region = this.region;
    }
    if (this.container != null) {
      options.container = this.container;
    }
    return options;
  };

  Controller.prototype.getName = function() {
    return this.name.replace("Controller", '').dasherize();
  };

  Controller.prototype.viewAndModel = function(view, model, modelParameters) {
    return this.waitForContinue(function() {
      var modelClass, viewClass;
      if (model != null) {
        modelClass = require("models/" + (model.toLowerCase())).Model;
        this.model = modelClass.findOrCreate(modelParameters);
      }
      viewClass = require("views/" + (this.getName()) + "/" + (view.toLowerCase()) + "-view");
      return this.view = new viewClass(this.buildViewOptions());
    });
  };

  Controller.prototype.viewAndCollection = function(view, collection, colParameters) {
    var collectionClass, viewClass;
    if (collection != null) {
      collectionClass = require("models/" + (collection.toLowerCase())).Collection;
      this.collection = new collectionClass(null, colParameters);
    }
    viewClass = require("views/" + (this.getName()) + "/" + (view.toLowerCase()) + "-view");
    return this.view = new viewClass(this.buildViewOptions());
  };

  Controller.prototype.handleContinue = function() {
    return this.continueDeferred.resolve();
  };

  Controller.prototype.waitForContinue = function(handler) {
    return this.continueDeferred.done(_.bind(handler, this));
  };

  Controller.prototype.redirectToName = function(name) {
    this.continueDeferred.reject();
    this.redirectTo({
      name: name
    });
    return this.dispose();
  };

  Controller.prototype.handleLogin = function() {
    return this.redirectToName('dashboard');
  };

  Controller.prototype.handleLogout = function() {
    return this.redirectToName('login');
  };

  Controller.prototype.handleDashboard = function() {
    return this.redirectToName('dashboard');
  };

  Controller.prototype.handleCreateBusiness = function() {
    return this.redirectToName('welcome');
  };

  Controller.prototype.handleSubscribe = function() {
    return this.redirectToName('payment');
  };

  Controller.prototype.dispose = function() {
    Controller.__super__.dispose.apply(this, arguments);
    if (!('resolved' === this.continueDeferred.state() || 'rejected' === this.continueDeferred.state())) {
      this.continueDeferred.reject();
    }
    return Backbone.Relational.store.reset();
  };

  return Controller;

})(Chaplin.Controller);
});

;require.register("controllers/home-controller", function(exports, require, module) {
var Controller, HomeController, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Controller = require('controllers/base/controller');

module.exports = HomeController = (function(_super) {
  __extends(HomeController, _super);

  function HomeController() {
    _ref = HomeController.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  HomeController.prototype.name = 'HomeController';

  HomeController.prototype.index = function() {
    return this.viewAndModel('Index');
  };

  return HomeController;

})(Controller);
});

;require.register("controllers/singletons/errors-controller", function(exports, require, module) {
var ErrorsController, errors, _ref,
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

errors = require('config').errors;

module.exports = ErrorsController = (function(_super) {
  __extends(ErrorsController, _super);

  function ErrorsController() {
    this.handleAjaxErrors = __bind(this.handleAjaxErrors, this);
    _ref = ErrorsController.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  ErrorsController.prototype.initialize = function() {
    ErrorsController.__super__.initialize.apply(this, arguments);
    return $(document).ajaxError(this.handleAjaxErrors);
  };

  ErrorsController.prototype.handleAjaxErrors = function(event, response, request) {
    if (response.responseJSON != null) {
      return this.handleErrorByCode(parseInt(response.responseJSON.code), response.status);
    } else {
      return this.handleErrorByStatusCode(response.status);
    }
  };

  ErrorsController.prototype.handleErrorByCode = function(code, status) {
    switch (code) {
      case errors.accountExpired:
        return this.publishEvent("account-expired");
      default:
        return this.handleErrorByStatusCode(status);
    }
  };

  ErrorsController.prototype.handleErrorByStatusCode = function(status) {
    switch (status) {
      case 401:
        return this.publishEvent("unauthorized");
    }
  };

  return ErrorsController;

})(Chaplin.Controller);
});

;require.register("controllers/singletons/progress-controller", function(exports, require, module) {
var NotificationsController, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

module.exports = NotificationsController = (function(_super) {
  __extends(NotificationsController, _super);

  function NotificationsController() {
    _ref = NotificationsController.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  NotificationsController.prototype.initialize = function() {
    NotificationsController.__super__.initialize.apply(this, arguments);
    this.subscribeEvent("!progress:start", this.startProgress);
    this.subscribeEvent("!progress:done", this.endProgress);
    this.subscribeEvent("!progress:inc", this.incProgress);
    return this.subscribeEvent("!progress:set", this.setProgress);
  };

  NotificationsController.prototype.startProgress = function() {
    return NProgress.start();
  };

  NotificationsController.prototype.endProgress = function() {
    return NProgress.done();
  };

  NotificationsController.prototype.incProgress = function() {
    return NProgress.inc();
  };

  NotificationsController.prototype.setProgress = function(val) {
    return NProgress.set(val);
  };

  return NotificationsController;

})(Chaplin.Controller);
});

;require.register("controllers/singletons/session-controller", function(exports, require, module) {
var SessionController, config, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

config = require('config');

module.exports = SessionController = (function(_super) {
  __extends(SessionController, _super);

  function SessionController() {
    _ref = SessionController.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  SessionController.prototype.initialize = function() {
    SessionController.__super__.initialize.apply(this, arguments);
    return this.subscribeEvent("controller:match", this.handleUrlMatch);
  };

  SessionController.prototype.handleUrlMatch = function(route) {
    var eventName;
    eventName = "continue";
    return this.publishEvent(eventName);
  };

  return SessionController;

})(Chaplin.Controller);
});

;require.register("controllers/singletons/storage-controller", function(exports, require, module) {
var StorageController, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

module.exports = StorageController = (function(_super) {
  __extends(StorageController, _super);

  function StorageController() {
    _ref = StorageController.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  StorageController.prototype.initialize = function() {
    StorageController.__super__.initialize.apply(this, arguments);
    this.subscribeEvent("!storage:get", this.getKey);
    return this.subscribeEvent("!storage:set", this.setKey);
  };

  StorageController.prototype.getKey = function(key, deserialize) {
    var item;
    if (deserialize == null) {
      deserialize = false;
    }
    item = localStorage.getItem(key);
    if (deserialize) {
      item = JSON.parse(item);
    }
    Chaplin.mediator[key] = item;
    return this.publishEvent("storage:" + key, item);
  };

  StorageController.prototype.setKey = function(key, value, serialize) {
    if (serialize == null) {
      serialize = false;
    }
    if (value != null) {
      if (serialize) {
        localStorage.setItem(key, JSON.stringify(value));
      } else {
        localStorage.setItem(key, value);
      }
    } else {
      localStorage.removeItem(key, value);
    }
    Chaplin.mediator[key] = value;
    return this.publishEvent("storage:" + key, value);
  };

  return StorageController;

})(Chaplin.Controller);
});

;require.register("initialize", function(exports, require, module) {
var Application, config, routes;

Application = require('application');

routes = require('routes');

config = require('config');

$(function() {
  return i18n.init({
    fallbackLng: 'en',
    resGetPath: '/locales/__lng__/__ns__.json'
  }, function() {
    return new Application({
      title: 'Bitcoin simulator',
      controllerSuffix: '-controller',
      routes: routes
    });
  });
});
});

;require.register("lib/editors/date-editor", function(exports, require, module) {
var DateEditor, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

module.exports = DateEditor = (function(_super) {
  __extends(DateEditor, _super);

  function DateEditor() {
    _ref = DateEditor.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  DateEditor.prototype.tagName = 'p';

  DateEditor.prototype.events = {
    'change': function() {
      return this.trigger('change', this);
    },
    'focus': function() {
      return this.trigger('focus', this);
    },
    'blur': function() {
      return this.trigger('blur', this);
    }
  };

  DateEditor.prototype.initialize = function(options) {
    DateEditor.__super__.initialize.apply(this, arguments);
    return this.pickerId = "datePicker" + _.uniqueId();
  };

  DateEditor.prototype.render = function() {
    this.$el.html(this.template(this.getTemplateData()));
    this.setValue(this.value);
    this.startDatePicker();
    return this;
  };

  DateEditor.prototype.startDatePicker = function() {
    return this.picker = this.$("#" + this.pickerId).datetimepicker({
      language: i18n.lng(),
      showToday: true,
      format: "HH:mm:ss DD/MM/YYYY"
    });
  };

  DateEditor.prototype.getTemplateData = function() {
    return {
      id: this.pickerId
    };
  };

  DateEditor.prototype.template = _.template("<div class='input-group date' data id='<%= id %>'>\n    <input type='text' class=\"form-control\" />\n    <span class=\"input-group-addon\"><i class=\"fa fa-calendar\"></i>\n    </span>\n</div>");

  DateEditor.prototype.getValue = function() {
    return moment(this.$('input').val(), "HH:mm:ss DD/MM/YYYY").utc().format("YYYY-MM-DD HH:mm:ss");
  };

  DateEditor.prototype.setValue = function(value) {
    return this.$('input').val(moment.utc(value, "YYYY-MM-DD HH:mm:ss").local().format("HH:mm:ss DD/MM/YYYY"));
  };

  DateEditor.prototype.focus = function() {
    if (!this.hasFocus) {
      return this.$el.focus();
    }
  };

  DateEditor.prototype.blur = function() {
    if (!!this.hasFocus) {
      return this.$el.blur();
    }
  };

  return DateEditor;

})(Backbone.Form.editors.Base);
});

;require.register("lib/utils", function(exports, require, module) {
var utils,
  __slice = [].slice,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

utils = Chaplin.utils.beget(Chaplin.utils);

_(utils).extend({
  mixOf: function() {
    var Mixed, base, method, mixin, mixins, name, _i, _ref, _ref1;
    base = arguments[0], mixins = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
    Mixed = (function(_super) {
      __extends(Mixed, _super);

      function Mixed() {
        _ref = Mixed.__super__.constructor.apply(this, arguments);
        return _ref;
      }

      return Mixed;

    })(base);
    for (_i = mixins.length - 1; _i >= 0; _i += -1) {
      mixin = mixins[_i];
      _ref1 = mixin.prototype;
      for (name in _ref1) {
        method = _ref1[name];
        Mixed.prototype[name] = method;
      }
    }
    return Mixed;
  }
});

if (typeof Object.seal === "function") {
  Object.seal(utils);
}

module.exports = utils;
});

;require.register("lib/view-helper", function(exports, require, module) {
var config,
  __slice = [].slice;

config = require('config');

Handlebars.registerHelper('with', function(context, options) {
  if (!context || Handlebars.Utils.isEmpty(context)) {
    return options.inverse(this);
  } else {
    return options.fn(context);
  }
});

Handlebars.registerHelper('without', function(context, options) {
  var inverse;
  inverse = options.inverse;
  options.inverse = options.fn;
  options.fn = inverse;
  return Handlebars.helpers["with"].call(this, context, options);
});

Handlebars.registerHelper('url', function() {
  var options, params, routeName, _i;
  routeName = arguments[0], params = 3 <= arguments.length ? __slice.call(arguments, 1, _i = arguments.length - 1) : (_i = 1, []), options = arguments[_i++];
  return Chaplin.helpers.reverse(routeName, params);
});

Handlebars.registerHelper('t', function(path) {
  var result;
  result = i18n.t(path);
  return new Handlebars.SafeString(result);
});

Handlebars.registerHelper('humanTime', function(time) {
  return moment.utc(time, "YYYY-MM-DD HH:mm:ss").local().lang(i18n.lng()).fromNow();
});

Handlebars.registerHelper('calendarTime', function(time) {
  return moment.utc(time, "YYYY-MM-DD HH:mm:ss").local().lang(i18n.lng()).calendar();
});
});

;require.register("models/base/collection", function(exports, require, module) {
var Collection, Model, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Model = require('models/base/model');

module.exports = Collection = (function(_super) {
  __extends(Collection, _super);

  function Collection() {
    _ref = Collection.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  Collection.prototype.model = Model;

  return Collection;

})(Chaplin.Collection);
});

;require.register("models/base/model", function(exports, require, module) {
'use strict';
var EventBroker, Model, serializeAttributes, serializeModelAttributes, utils, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

utils = require('lib/utils');

EventBroker = Chaplin.EventBroker;

serializeAttributes = function(model, attributes, modelStack) {
  var delegator, key, otherModel, serializedModels, value, _i, _len, _ref;
  delegator = utils.beget(attributes);
  if (modelStack == null) {
    modelStack = {};
  }
  modelStack[model.cid] = true;
  for (key in attributes) {
    value = attributes[key];
    if (value instanceof Backbone.Model) {
      delegator[key] = serializeModelAttributes(value, model, modelStack);
    } else if (value instanceof Backbone.Collection) {
      serializedModels = [];
      _ref = value.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        otherModel = _ref[_i];
        serializedModels.push(serializeModelAttributes(otherModel, model, modelStack));
      }
      delegator[key] = serializedModels;
    }
  }
  delete modelStack[model.cid];
  return delegator;
};

serializeModelAttributes = function(model, currentModel, modelStack) {
  var attributes;
  if (model === currentModel || model.cid in modelStack) {
    return null;
  }
  attributes = typeof model.getAttributes === 'function' ? model.getAttributes() : model.attributes;
  return serializeAttributes(model, attributes, modelStack);
};

module.exports = Model = (function(_super) {
  __extends(Model, _super);

  function Model() {
    _ref = Model.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  _.extend(Model.prototype, EventBroker);

  Model.prototype.toString = function() {
    return this.get(this.toStringAttr) || this.id;
  };

  Model.prototype.getAttributes = function() {
    return this.attributes;
  };

  Model.prototype.serialize = function() {
    return serializeAttributes(this, this.getAttributes());
  };

  Model.prototype.disposed = false;

  Model.prototype.dispose = function() {
    var prop, properties, _i, _len;
    if (this.disposed) {
      return;
    }
    this.trigger('dispose', this);
    this.unsubscribeAllEvents();
    this.stopListening();
    this.off();
    properties = ['collection', 'attributes', 'changed', '_escapedAttributes', '_previousAttributes', '_silent', '_pending', '_callbacks'];
    for (_i = 0, _len = properties.length; _i < _len; _i++) {
      prop = properties[_i];
      delete this[prop];
    }
    this.disposed = true;
    return typeof Object.freeze === "function" ? Object.freeze(this) : void 0;
  };

  return Model;

})(Backbone.RelationalModel);
});

;require.register("models/base/pageable-collection", function(exports, require, module) {
var Collection, Model, utils, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

utils = require('lib/utils');

Model = require('models/base/model');

module.exports = Collection = (function(_super) {
  __extends(Collection, _super);

  function Collection() {
    _ref = Collection.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  _.extend(Collection.prototype, Chaplin.EventBroker);

  Collection.prototype.model = Model;

  Collection.prototype.mode = 'server';

  Collection.prototype.queryParams = {
    totalPages: 'pageCount',
    totalRecords: 'count',
    sortKey: "sort",
    order: "direction",
    pageSize: 'limit',
    directions: {
      "-1": "asc",
      "1": "desc"
    }
  };

  Collection.prototype.serialize = function() {
    return this.map(utils.serialize);
  };

  Collection.prototype.disposed = false;

  Collection.prototype.dispose = function() {
    var prop, properties, _i, _len;
    if (this.disposed) {
      return;
    }
    this.trigger('dispose', this);
    this.reset([], {
      silent: true
    });
    this.unsubscribeAllEvents();
    this.stopListening();
    this.off();
    properties = ['model', 'models', '_byId', '_byCid', '_callbacks'];
    for (_i = 0, _len = properties.length; _i < _len; _i++) {
      prop = properties[_i];
      delete this[prop];
    }
    this.disposed = true;
    return typeof Object.freeze === "function" ? Object.freeze(this) : void 0;
  };

  return Collection;

})(Backbone.PageableCollection);
});

;require.register("models/business", function(exports, require, module) {
var BusinessModel, BusinessesCollection, Category, Country, Model, PageableCollection, State, Town, User, config, country, state, towns, users, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Model = require('models/base/model');

Country = require('models/country');

State = require('models/state');

Town = require('models/town');

Category = require('models/category');

PageableCollection = require('models/base/pageable-collection');

User = require('models/user');

config = require('config');

country = Country.Model.find({
  id: '73'
});

if (country == null) {
  country = new Country.Model({
    id: '73'
  });
}

state = State.Model.find({
  id: '38'
});

if (state == null) {
  state = new State.Model({
    id: '38'
  });
}

towns = new Town.Collection();

towns.url = config.apiRoot + 'states/38/towns';

users = new User.Collection();

module.exports.Model = BusinessModel = (function(_super) {
  __extends(BusinessModel, _super);

  function BusinessModel() {
    _ref = BusinessModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  BusinessModel.prototype.urlRoot = config.api.host + config.api.root + 'businesses';

  BusinessModel.prototype.toStringAttr = 'name';

  BusinessModel.prototype.save = function() {
    var email, notAvailable, telephone;
    telephone = this.get('telephone');
    email = this.get('email');
    notAvailable = i18n.t("views.business.tabs.contact.not-available");
    if ((telephone != null) && (telephone.trim() === '' || telephone === notAvailable)) {
      this.set('telephone', null);
    }
    if ((email != null) && (email.trim() === '' || email === notAvailable)) {
      this.set('email', null);
    }
    this.set('owner_id', Chaplin.mediator.user);
    return BusinessModel.__super__.save.apply(this, arguments);
  };

  BusinessModel.prototype.relations = [
    {
      type: Backbone.HasOne,
      key: 'country_id',
      includeInJSON: 'id',
      relatedModel: Country.Model
    }, {
      type: Backbone.HasOne,
      key: 'state_id',
      includeInJSON: 'id',
      relatedModel: State.Model
    }, {
      type: Backbone.HasOne,
      key: 'town_id',
      includeInJSON: 'id',
      relatedModel: Town.Model
    }, {
      type: Backbone.HasOne,
      key: 'owner_id',
      autoFetch: true,
      includeInJSON: 'id',
      relatedModel: User.Model
    }, {
      type: Backbone.HasOne,
      key: 'category_id',
      includeInJSON: 'id',
      relatedModel: Category.Model
    }
  ];

  BusinessModel.prototype.schema = {
    name: {
      title: 'Nombre',
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    description: {
      title: 'Descripción',
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    town_id: {
      title: 'Ciudad',
      type: 'Select',
      options: towns,
      editorClass: 'form-control',
      validators: ['required']
    },
    address: {
      editorClass: 'form-control',
      validators: ['required']
    },
    zip_code: {
      title: 'Codigo postal',
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    telephone: {
      title: 'Teléfono',
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    email: {
      title: 'Email',
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    opening_hours: {
      title: 'Horario:',
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    lat: {
      title: 'Latitud',
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    lon: {
      title: 'Longitud',
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    owner_id: {
      title: 'Propietario',
      type: 'Select',
      options: users,
      editorClass: 'form-control',
      validators: ['required']
    }
  };

  return BusinessModel;

})(Model);

module.exports.Collection = BusinessesCollection = (function(_super) {
  __extends(BusinessesCollection, _super);

  function BusinessesCollection() {
    _ref1 = BusinessesCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  BusinessesCollection.prototype.model = BusinessModel;

  BusinessesCollection.prototype.url = config.api.host + config.api.root + 'businesses';

  return BusinessesCollection;

})(PageableCollection);
});

;require.register("models/category", function(exports, require, module) {
var CategoriesCollection, CategoryModel, Model, PageableCollection, config, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Model = require('models/base/model');

PageableCollection = require('models/base/pageable-collection');

config = require('config');

module.exports.Model = CategoryModel = (function(_super) {
  __extends(CategoryModel, _super);

  function CategoryModel() {
    _ref = CategoryModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  CategoryModel.prototype.urlRoot = config.api.host + config.api.root + 'categories';

  CategoryModel.prototype.toStringAttr = 'name';

  return CategoryModel;

})(Model);

module.exports.Collection = CategoriesCollection = (function(_super) {
  __extends(CategoriesCollection, _super);

  function CategoriesCollection() {
    _ref1 = CategoriesCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  CategoriesCollection.prototype.model = CategoryModel;

  CategoriesCollection.prototype.url = config.api.host + config.api.root + 'categories';

  return CategoriesCollection;

})(PageableCollection);
});

;require.register("models/country", function(exports, require, module) {
var Collection, CountriesCollection, CountryModel, Model, config, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Model = require('models/base/model');

Collection = require('models/base/collection');

config = require('config');

module.exports.Model = CountryModel = (function(_super) {
  __extends(CountryModel, _super);

  function CountryModel() {
    _ref = CountryModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  CountryModel.prototype.urlRoot = config.api.host + config.api.root + 'countries';

  CountryModel.prototype.toStringAttr = 'name';

  return CountryModel;

})(Model);

module.exports.Collection = CountriesCollection = (function(_super) {
  __extends(CountriesCollection, _super);

  function CountriesCollection() {
    _ref1 = CountriesCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  CountriesCollection.prototype.model = CountryModel;

  CountriesCollection.prototype.url = config.api.host + config.api.root + 'countries';

  return CountriesCollection;

})(Collection);
});

;require.register("models/offer", function(exports, require, module) {
var Business, DateEditor, DateFormatter, Model, OfferModel, OffersCollection, PageableCollection, config, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

Model = require('models/base/model');

Business = require('models/business');

PageableCollection = require('models/base/pageable-collection');

DateEditor = require('lib/editors/date-editor');

config = require('config');

DateFormatter = require('lib/live-edit/formatters/date-formatter');

module.exports.Model = OfferModel = (function(_super) {
  __extends(OfferModel, _super);

  function OfferModel() {
    _ref = OfferModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  OfferModel.prototype.urlRoot = config.api.host + config.api.root + 'offers';

  OfferModel.prototype.relations = [
    {
      type: Backbone.HasOne,
      key: 'business_id',
      relatedModel: Business.Model,
      autoFetch: true,
      includeInJSON: 'id'
    }, {
      type: Backbone.HasOne,
      key: 'type_id',
      relatedModel: Model,
      autoFetch: false,
      includeInJSON: 'id'
    }, {
      type: Backbone.HasOne,
      key: 'size_id',
      relatedModel: Model,
      autoFetch: false,
      includeInJSON: 'id'
    }
  ];

  OfferModel.prototype.schema = {
    description: {
      title: i18n.t("models.offer.schema.description"),
      type: 'Text',
      editorClass: 'form-control',
      validators: ['required']
    },
    start: {
      title: i18n.t("models.offer.schema.start"),
      type: DateEditor,
      validators: ['required']
    },
    end: {
      title: i18n.t("models.offer.schema.end"),
      type: DateEditor,
      validators: ['required']
    },
    price: {
      title: i18n.t("models.offer.schema.price"),
      type: 'Number',
      editorClass: 'form-control',
      validators: ['required']
    },
    offer: {
      title: i18n.t("models.offer.schema.offer"),
      type: 'Number',
      editorClass: 'form-control',
      validators: ['required']
    }
  };

  OfferModel.prototype.initialize = function() {
    var businessId;
    OfferModel.__super__.initialize.apply(this, arguments);
    businessId = Chaplin.mediator.businesses[0];
    this.set('type_id', Model.find({
      id: 1
    }) || new Model({
      id: 1
    }));
    this.set('size_id', Model.find({
      id: 2
    }) || new Model({
      id: 2
    }));
    this.set('business_id', Business.Model.findOrCreate({
      id: businessId
    }));
    if (this.get('start') == null) {
      this.set('start', moment.utc().format("YYYY-MM-DD HH:mm:ss"));
    }
    if (this.get('end') == null) {
      return this.set('end', moment.utc().format("YYYY-MM-DD HH:mm:ss"));
    }
  };

  OfferModel.prototype.getChecks = function() {
    var _this = this;
    return $.get("" + this.urlRoot + "/" + this.id + "/checks").done(function(data) {
      return _this.set('checks', data);
    });
  };

  OfferModel.prototype.extraProperties = ['restaurante_id', 'descripcion', 'precio_oferta', 'precio_real', 'fecha_inicio', 'fecha_fin', 'foto', 'talla', 'restaurante_nombre', 'restaurante_latitud', 'restaurante_longitud', 'distancia'];

  OfferModel.prototype.save = function() {
    var checks;
    if (this.isNew()) {
      this.set('photo', '/img/files/foodicious.png');
    }
    checks = this.get('checks');
    this.unset('checks');
    OfferModel.__super__.save.apply(this, arguments);
    return this.set('checks', checks);
  };

  OfferModel.prototype.toJSON = function() {
    var jsonData;
    jsonData = OfferModel.__super__.toJSON.apply(this, arguments);
    return _.omit(jsonData, this.extraProperties);
  };

  return OfferModel;

})(Model);

module.exports.Collection = OffersCollection = (function(_super) {
  __extends(OffersCollection, _super);

  function OffersCollection() {
    this.url = __bind(this.url, this);
    _ref1 = OffersCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  OffersCollection.prototype.model = OfferModel;

  OffersCollection.prototype.url = function() {
    return config.api.host + config.api.root + ("businesses/" + this.id + "/offers/");
  };

  OffersCollection.prototype.mode = 'infinite';

  OffersCollection.prototype.state = {
    pageSize: 20,
    sortKey: 'modified',
    order: 1
  };

  OffersCollection.prototype.initialize = function(data, options) {
    OffersCollection.__super__.initialize.apply(this, arguments);
    if (options.id != null) {
      return this.id = options.id;
    } else {
      throw new Error("You must specifiy an business id for the offers collection");
    }
  };

  OffersCollection.prototype.parseLinks = function(response, xhr) {
    var nextUrl, pagination, url;
    url = this.url();
    pagination = response[0];
    nextUrl = "" + url + "?page=" + (pagination.page + 1);
    return {
      next: this.state.currentPage !== this.state.lastPage ? nextUrl : void 0
    };
  };

  OffersCollection.prototype.parse = function() {
    var resp;
    if (this.disposed) {
      return;
    }
    resp = OffersCollection.__super__.parse.apply(this, arguments);
    this.state.totalRecords -= this.state.pageSize;
    this.state.lastPage = parseInt(Math.ceil(this.state.totalRecords / this.state.pageSize));
    this.state.totalPage = this.state.lastPage;
    return resp;
  };

  OffersCollection.prototype.comparator = function(self) {
    return -moment.utc(self.get('modified')).format("X");
  };

  return OffersCollection;

})(PageableCollection);
});

;require.register("models/stat", function(exports, require, module) {
var Collection, Model, StatModel, StatsCollection, config, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

Model = require('models/base/model');

Collection = require('models/base/collection');

config = require('config');

module.exports.Model = StatModel = (function(_super) {
  __extends(StatModel, _super);

  function StatModel() {
    _ref = StatModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  return StatModel;

})(Model);

module.exports.Collection = StatsCollection = (function(_super) {
  __extends(StatsCollection, _super);

  function StatsCollection() {
    this.generateBarDataPerMonth = __bind(this.generateBarDataPerMonth, this);
    this.generateData = __bind(this.generateData, this);
    _ref1 = StatsCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  StatsCollection.prototype.model = StatModel;

  StatsCollection.prototype.initialize = function(models, options) {
    StatsCollection.__super__.initialize.apply(this, arguments);
    _.merge(this, _.pick(options, ['what', 'business', 'when', 'type', 'chart', 'year']));
    return this.url = function() {
      return config.api.host + config.api.root + ("stats/" + this.what + "/" + this.type + "/" + this.business + "/" + this.when + "/" + this.year);
    };
  };

  StatsCollection.prototype.prepare = function() {
    if (this.chart === 'gauge') {
      return this.generateGaugeData();
    } else if (this.chart === 'barChart') {
      if (this.type === 'revenueByTime') {
        return this.generateBarData();
      } else if (this.type === 'revenue') {
        return this.generateBarRevenuePerOffer();
      }
    } else {
      return this.generateGraphData();
    }
  };

  StatsCollection.prototype.generateGaugeData = function() {
    var data, model, opts;
    data = [];
    opts = {
      lines: 2,
      angle: 0,
      lineWidth: 0.48,
      pointer: {
        length: 0.6,
        strokeWidth: 0.03,
        color: "464646"
      },
      limitMax: "true",
      colorStart: "#fa8564",
      colorStop: "#fa8564",
      strokeColor: "#F1F1F1",
      generateGradient: true
    };
    data.push(opts);
    model = this.findWhere({
      'month': moment.utc().format("M")
    });
    if (model) {
      data.push(model.get("total"));
    } else {
      Gauge.prototype.displayedValue = 1;
      data.push("0");
    }
    return data;
  };

  StatsCollection.prototype.generateData = function() {
    var data, hash, i, model, size, _i;
    data = [];
    size = 12;
    switch (this.when) {
      case 'month':
        size = 12;
        break;
      case 'weekday':
        size = 7;
    }
    for (i = _i = 1; 1 <= size ? _i <= size : _i >= size; i = 1 <= size ? ++_i : --_i) {
      hash = {};
      hash[this.when] = i.toString();
      model = this.findWhere(hash);
      if (model) {
        data.push(model.get("total"));
      } else {
        data.push(0);
      }
    }
    return data;
  };

  StatsCollection.prototype.generateBarDataPerMonth = function() {
    var data;
    data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
    _.each(this.models, function(model) {
      var month, price;
      month = model.get("month");
      price = parseFloat(model.get("offer")) * parseFloat(model.get("total"));
      return data[month - 1] += price;
    });
    return data;
  };

  StatsCollection.prototype.generateLabels = function() {
    var data;
    switch (this.when) {
      case 'month':
        return data = [i18n.t("data.months.January"), i18n.t("data.months.February"), i18n.t("data.months.March"), i18n.t("data.months.April"), i18n.t("data.months.May"), i18n.t("data.months.June"), i18n.t("data.months.July"), i18n.t("data.months.August"), i18n.t("data.months.September"), i18n.t("data.months.October"), i18n.t("data.months.November"), i18n.t("data.months.December")];
      case 'weekday':
        return data = [i18n.t("data.weekday.Monday"), i18n.t("data.weekday.Tuesday"), i18n.t("data.weekday.Wednesday"), i18n.t("data.weekday.Thursday"), i18n.t("data.weekday.Friday"), i18n.t("data.weekday.Saturday"), i18n.t("data.weekday.Sunday")];
    }
  };

  StatsCollection.prototype.generateDataSet = function(data) {
    switch (this.what) {
      case 'checks':
        if (this.type === 'revenueByTime' || this.type === 'revenue') {
          return {
            fillColor: "#d35400",
            strokeColor: "#d35400",
            pointColor: "#d35400",
            pointStrokeColor: "#fff",
            data: data()
          };
        } else {
          return {
            fillColor: "#25a35a",
            strokeColor: "#25a35a",
            pointColor: "#25a35a",
            pointStrokeColor: "#fff",
            data: data()
          };
        }
        break;
      case 'visits':
        return {
          fillColor: "#3498db",
          strokeColor: "#3498db",
          pointColor: "#3498db",
          pointStrokeColor: "#fff",
          data: data()
        };
      case 'offers':
        return {
          fillColor: "#e74c3c",
          strokeColor: "#e74c3c",
          pointColor: "#e74c3c",
          pointStrokeColor: "#fff",
          data: data()
        };
    }
  };

  StatsCollection.prototype.generateGraphData = function() {
    return {
      labels: this.generateLabels(),
      datasets: [this.generateDataSet(this.generateData)]
    };
  };

  StatsCollection.prototype.generateBarData = function() {
    return {
      labels: this.generateLabels(),
      datasets: [this.generateDataSet(this.generateBarDataPerMonth)]
    };
  };

  StatsCollection.prototype.genRevenue = function() {
    var data, sortData;
    data = this.map(function(model) {
      var price;
      price = parseFloat(model.get("offer")) * parseFloat(model.get("total"));
      return {
        price: price,
        offer: model.get('offer_id'),
        description: model.get('description')
      };
    });
    sortData = _.sortBy(data, 'price');
    sortData = _(sortData).reverse().value();
    return sortData.slice(0, 5);
  };

  StatsCollection.prototype.generateBarRevenuePerOffer = function() {
    var dataValue, labels;
    labels = [];
    dataValue = [];
    _.each(this.genRevenue(), function(data, ind) {
      labels.push(data.description);
      return dataValue.push(data.price);
    });
    return {
      labels: labels,
      datasets: [
        this.generateDataSet(function() {
          return dataValue;
        })
      ]
    };
  };

  return StatsCollection;

})(Collection);
});

;require.register("models/state", function(exports, require, module) {
var Collection, Country, Model, StateModel, StatesCollection, config, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Model = require('models/base/model');

Country = require('models/country');

Collection = require('models/base/collection');

config = require('config');

module.exports.Model = StateModel = (function(_super) {
  __extends(StateModel, _super);

  function StateModel() {
    _ref = StateModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  StateModel.prototype.urlRoot = config.api.root + 'states';

  StateModel.prototype.toStringAttr = 'name';

  StateModel.prototype.relations = [
    {
      type: Backbone.HasOne,
      key: 'country_id',
      relatedModel: Country.Model,
      autoFetch: true
    }
  ];

  return StateModel;

})(Model);

module.exports.Collection = StatesCollection = (function(_super) {
  __extends(StatesCollection, _super);

  function StatesCollection() {
    _ref1 = StatesCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  StatesCollection.prototype.model = StateModel;

  StatesCollection.prototype.url = config.api.root + 'states';

  StatesCollection.prototype.urlByParent = function(parentId) {
    return config.apiRoot + ("countries/" + parentId + "/states");
  };

  return StatesCollection;

})(Collection);
});

;require.register("models/timeline", function(exports, require, module) {
var Model, PageableCollection, TimelineCollection, TimelineModel, config, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

Model = require('models/base/model');

PageableCollection = require('models/base/pageable-collection');

config = require('config');

module.exports.Model = TimelineModel = (function(_super) {
  __extends(TimelineModel, _super);

  function TimelineModel() {
    _ref = TimelineModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  TimelineModel.prototype.toStringAttr = 'name';

  return TimelineModel;

})(Model);

module.exports.Collection = TimelineCollection = (function(_super) {
  __extends(TimelineCollection, _super);

  function TimelineCollection() {
    this.url = __bind(this.url, this);
    _ref1 = TimelineCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  TimelineCollection.prototype.model = TimelineModel;

  TimelineCollection.prototype.url = function() {
    return config.api.host + config.api.root + ("timeline/" + this.id);
  };

  TimelineCollection.prototype.mode = 'infinite';

  TimelineCollection.prototype.comparator = 'created';

  TimelineCollection.prototype.state = {
    pageSize: 3,
    sortKey: 'created',
    order: 1
  };

  TimelineCollection.prototype.initialize = function(data, options) {
    TimelineCollection.__super__.initialize.apply(this, arguments);
    if (options.id != null) {
      return this.id = options.id;
    } else {
      throw new Error("You must specifiy an business id for the timeline");
    }
  };

  TimelineCollection.prototype.parseLinks = function(response, xhr) {
    var nextUrl, pagination, url;
    url = this.url();
    pagination = response[0];
    nextUrl = "" + url + "?page=" + (pagination.page + 1);
    return {
      next: this.state.currentPage !== this.state.lastPage ? nextUrl : void 0
    };
  };

  TimelineCollection.prototype.parse = function() {
    var resp;
    resp = TimelineCollection.__super__.parse.apply(this, arguments);
    this.state.totalRecords -= this.state.pageSize;
    this.state.lastPage = parseInt(Math.ceil(this.state.totalRecords / this.state.pageSize));
    this.state.totalPage = this.state.lastPage;
    return resp;
  };

  return TimelineCollection;

})(PageableCollection);
});

;require.register("models/town", function(exports, require, module) {
var Collection, Model, State, TownModel, TownsCollection, config, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Model = require('models/base/model');

Collection = require('models/base/collection');

config = require('config');

State = require('models/state');

module.exports.Model = TownModel = (function(_super) {
  __extends(TownModel, _super);

  function TownModel() {
    _ref = TownModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  TownModel.prototype.urlRoot = config.api.host + config.api.root + 'towns';

  TownModel.prototype.toStringAttr = 'name';

  TownModel.prototype.relations = [
    {
      type: Backbone.HasOne,
      key: 'state_id',
      autoFetch: true,
      relatedModel: State.Model
    }
  ];

  return TownModel;

})(Model);

module.exports.Collection = TownsCollection = (function(_super) {
  __extends(TownsCollection, _super);

  function TownsCollection() {
    _ref1 = TownsCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  TownsCollection.prototype.model = TownModel;

  TownsCollection.prototype.url = config.api.host + config.api.root + 'towns';

  TownsCollection.prototype.urlByParent = function(parentId) {
    return config.apiRoot + ("states/" + parentId + "/towns");
  };

  return TownsCollection;

})(Collection);
});

;require.register("models/user-password", function(exports, require, module) {
var Model, UserPassword, config, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Model = require('models/base/model');

config = require('config');

module.exports.Model = UserPassword = (function(_super) {
  __extends(UserPassword, _super);

  function UserPassword() {
    _ref = UserPassword.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  UserPassword.prototype.url = function() {
    return config.api.host + config.api.root + ("users/" + this.id + "/password");
  };

  UserPassword.prototype.schema = function() {
    return {
      oldPassword: {
        title: i18n.t("views.profile.form.oldPassword"),
        type: 'Password',
        editorClass: 'form-control',
        validators: ['required']
      },
      password: {
        title: i18n.t("views.profile.form.password"),
        type: 'Password',
        editorClass: 'form-control',
        validators: [
          {
            type: 'match',
            field: "passwordConfirmation"
          }, 'required'
        ]
      },
      passwordConfirmation: {
        title: i18n.t("views.profile.form.confirmation"),
        type: 'Password',
        editorClass: 'form-control',
        validators: [
          {
            type: 'match',
            field: "password"
          }, 'required'
        ]
      }
    };
  };

  return UserPassword;

})(Model);
});

;require.register("models/user", function(exports, require, module) {
var Model, PageableCollection, UserModel, UsersCollection, config, _ref, _ref1,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

Model = require('models/base/model');

PageableCollection = require('models/base/pageable-collection');

config = require('config');

module.exports.Model = UserModel = (function(_super) {
  __extends(UserModel, _super);

  function UserModel() {
    _ref = UserModel.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  UserModel.prototype.urlRoot = config.api.root + 'users';

  UserModel.prototype.toStringAttr = 'name';

  UserModel.prototype.save = function() {
    this.set('role', 'owner');
    return UserModel.__super__.save.apply(this, arguments);
  };

  return UserModel;

})(Model);

module.exports.Collection = UsersCollection = (function(_super) {
  __extends(UsersCollection, _super);

  function UsersCollection() {
    _ref1 = UsersCollection.__super__.constructor.apply(this, arguments);
    return _ref1;
  }

  UsersCollection.prototype.url = config.api.root + 'users';

  UsersCollection.prototype.model = UserModel;

  return UsersCollection;

})(PageableCollection);
});

;require.register("routes", function(exports, require, module) {
module.exports = function(match) {
  return match('', 'home#index', {
    name: 'index'
  });
};
});

;require.register("templates/home/index", function(exports, require, module) {
var __templateData = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  


  return "<div class=\"row\">\n  <div class=\"col-sm-offset-2 col-sm-8\">\n    <div class=\"jumbotron\">\n      <h1>\n        <i class=\"fa fa-btc\"></i>itcoin simulator <br/>\n      </h1>\n      <p class=\"lead\">\n        A Bitcoin network protocol simulator written in python. <br/>\n        <img src=\"images/btc-miner.jpg\">\n      </p>\n      <p><a class=\"btn btn-lg btn-primary\" ng-href=\"#simulation\">Setup new simulation!</span></a></p>\n    </div>\n  </div>\n</div>";
  });
if (typeof define === 'function' && define.amd) {
  define([], function() {
    return __templateData;
  });
} else if (typeof module === 'object' && module && module.exports) {
  module.exports = __templateData;
} else {
  __templateData;
}
});

;require.register("templates/layout/header", function(exports, require, module) {
var __templateData = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  


  return "  <div class=\"container-fluid\">\n    <!-- Brand and toggle get grouped for better mobile display -->\n    <div class=\"navbar-header\">\n      <button type=\"button\" class=\"navbar-toggle\" data-toggle=\"collapse\" data-target=\"#bs-example-navbar-collapse-1\">\n        <span class=\"sr-only\">Toggle navigation</span>\n        <span class=\"icon-bar\"></span>\n        <span class=\"icon-bar\"></span>\n        <span class=\"icon-bar\"></span>\n      </button>\n      <a class=\"navbar-brand\" href=\"#\"><i class=\"fa fa-btc\"></i></a>\n    </div>\n    <div class=\"collapse navbar-collapse\" id=\"bs-example-navbar-collapse-1\">\n      <ul class=\"nav navbar-nav\">\n      </ul>\n    </div>\n  </div><!-- /.container-fluid -->\n";
  });
if (typeof define === 'function' && define.amd) {
  define([], function() {
    return __templateData;
  });
} else if (typeof module === 'object' && module && module.exports) {
  module.exports = __templateData;
} else {
  __templateData;
}
});

;require.register("templates/layout/site", function(exports, require, module) {
var __templateData = Handlebars.template(function (Handlebars,depth0,helpers,partials,data) {
  this.compilerInfo = [4,'>= 1.0.0'];
helpers = this.merge(helpers, Handlebars.helpers); data = data || {};
  


  return "<!-- Actual content -->\n	<div id=\"header-container\"></div>\n	<div id=\"page-container\">\n		<div class=\"wrapper container\"></div>\n	</div>";
  });
if (typeof define === 'function' && define.amd) {
  define([], function() {
    return __templateData;
  });
} else if (typeof module === 'object' && module && module.exports) {
  module.exports = __templateData;
} else {
  __templateData;
}
});

;require.register("views/base/collection-view", function(exports, require, module) {
var CollectionView, View, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

View = require('views/base/view');

module.exports = CollectionView = (function(_super) {
  __extends(CollectionView, _super);

  function CollectionView() {
    _ref = CollectionView.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  CollectionView.prototype.getTemplateFunction = View.prototype.getTemplateFunction;

  CollectionView.prototype.initialize = function() {
    CollectionView.__super__.initialize.apply(this, arguments);
    return this.listenTo(this, 'addedToDOM', this.finishProgress);
  };

  CollectionView.prototype.finishProgress = View.prototype.finishProgress;

  return CollectionView;

})(Chaplin.CollectionView);
});

;require.register("views/base/view", function(exports, require, module) {
var View, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

require('lib/view-helper');

module.exports = View = (function(_super) {
  __extends(View, _super);

  function View() {
    _ref = View.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  View.prototype.getTemplateFunction = function() {
    return this.template;
  };

  View.prototype.initialize = function(options) {
    View.__super__.initialize.apply(this, arguments);
    if (this.model && options.autoFetch) {
      this.model.fetch();
    }
    return this.listenTo(this, 'addedToDOM', this.finishProgress);
  };

  View.prototype.finishProgress = function() {
    return this.publishEvent("!progress:done");
  };

  return View;

})(Chaplin.View);
});

;require.register("views/home/index-view", function(exports, require, module) {
var IndexView, View, template, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

View = require('views/base/view');

template = require('templates/home/index');

module.exports = IndexView = (function(_super) {
  __extends(IndexView, _super);

  function IndexView() {
    _ref = IndexView.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  IndexView.prototype.template = template;

  IndexView.prototype.autoRender = true;

  IndexView.prototype.autoAttach = true;

  return IndexView;

})(View);
});

;require.register("views/layout/header-view", function(exports, require, module) {
var HeaderView, View, template, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

View = require('views/base/view');

template = require('templates/layout/header');

module.exports = HeaderView = (function(_super) {
  __extends(HeaderView, _super);

  function HeaderView() {
    _ref = HeaderView.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  HeaderView.prototype.tagName = 'header';

  HeaderView.prototype.className = 'navbar navbar-inverse navbar-fixed-top';

  HeaderView.prototype.region = 'header';

  HeaderView.prototype.template = template;

  HeaderView.prototype.attributes = {
    "role": "navigation"
  };

  return HeaderView;

})(View);
});

;require.register("views/layout/site-view", function(exports, require, module) {
var SiteView, View, template, _ref,
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

View = require('views/base/view');

template = require('templates/layout/site');

module.exports = SiteView = (function(_super) {
  __extends(SiteView, _super);

  function SiteView() {
    _ref = SiteView.__super__.constructor.apply(this, arguments);
    return _ref;
  }

  SiteView.prototype.container = 'body';

  SiteView.prototype.id = 'site-container';

  SiteView.prototype.regions = {
    header: '#header-container',
    main: '#page-container .wrapper',
    sidebar: "#sidebar-container",
    "right-sidebar": "#right-sidebar-container",
    footer: '#footer-container'
  };

  SiteView.prototype.template = template;

  /*
  	events:
  		"click #cc-approve-button-thissite": 'handleCloseCookiesClick'	
  		"click #cc-notification-moreinfo": 'handleViewDetailsClick'
  	initialize: () ->
  		super
  		@listenTo @, 'addedToDOM', @displayCookieConsent		
  		
  	handleCloseCookiesClick: (e) ->
  		e.preventDefault()
  		@$("#cc-notification").slideToggle()	
  
  	handleViewDetailsClick: (e) ->
  		e.preventDefault()
  		if $(e.target).html() is 'ver detalles'
  			@$("#cc-approve-button-allsites").show()
  			$(e.target).html 'ocultar'
  		else
  			@$("#cc-approve-button-allsites").hide()
  			$(e.target).html 'ver detalles'
  		@$("#cc-notification-logo").fadeToggle()
  		@$("#cc-notification-permissions").slideToggle()
  		@$(e.target).blur()
  
  	displayCookieConsent: ->
  		if !$.cookie 'policies'
  			$.cookie 'policies', 'accept'
  			$("#cc-notification").delay(500).slideToggle()
  */


  return SiteView;

})(View);
});

;
//# sourceMappingURL=app.js.map