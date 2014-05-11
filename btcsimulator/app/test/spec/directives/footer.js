'use strict';

describe('Directive: footer', function () {

  // load the directive's module
  beforeEach(module('btcsimulatorAppApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<footer></footer>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the footer directive');
  }));
});
