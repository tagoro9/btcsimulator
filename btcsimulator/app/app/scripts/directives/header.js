'use strict';

angular.module('btcsimulatorAppApp')
  .directive('header', function () {
    return {
      templateUrl: 'views/header.html',
      restrict: 'A',
      controller: function($scope) {
        $scope.headerLinks = [
          {
            name: 'Simulation',
            href: 'simulation'
          },
          {
            name: 'Getting started',
            href: 'getting-started'
          },
          {
            name: 'Docs',
            href: 'docs'
          }
        ]
      }
    };
  });
