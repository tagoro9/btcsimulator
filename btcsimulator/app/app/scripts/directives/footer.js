'use strict';

angular.module('btcsimulatorAppApp')
  .directive('footer', function () {
    return {
      templateUrl: 'views/footer.html',
      restrict: 'A',
      controller: function($scope) {
        $scope.footerLinks = [
          {
            name: 'Currently 0.0.1'
          },
          {
            name: 'Github',
            href: 'http://github.com'
          },
          {
            name: 'About',
            href: '#about'
          }
        ]
      }
    };
  });
