'use strict';

angular.module('btcsimulatorAppApp')
  .controller('HeaderCtrl', function ($scope, $location) {
    $scope.isActive = function(link) {
      if ($location.path() === "/" + link.href) {
        return true;
      }
      return false;
    }
  });
