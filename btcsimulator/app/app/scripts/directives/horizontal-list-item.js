'use strict';

angular.module('btcsimulatorAppApp')
  .directive('horizontalListItem', function () {
    return {
      templateUrl: 'views/partials/horizontal-list-item.html',
      restrict: 'E'
    };
  });
