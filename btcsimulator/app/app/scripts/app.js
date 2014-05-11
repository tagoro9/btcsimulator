'use strict';

angular
  .module('btcsimulatorAppApp', [
    'ngCookies',
    'ngResource',
    'ngSanitize',
    'ngRoute'
  ])
  .config(function ($routeProvider, $locationProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .when('/simulation', {
        templateUrl: 'views/simulation.html',
        controller: 'SimulationCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
