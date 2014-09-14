'use strict';

describe('Controller: MainCtrl', function () {

  // load the controller's module
  beforeEach(module('neuroApp'));

  var MainCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    MainCtrl = $controller('MainCtrl', {
      $scope: scope
    });
  }));

  it('should initialize `statsLoaded` to `false`', function () {
    expect(scope.statsLoaded).toBe(false);
  });
});

