'use strict';

describe('Controller: SearchCtrl', function() {

  beforeEach(module('neuroApp'));

  var SearchCtrl;
  var scope;

  beforeEach(inject(function($controller, $rootScope) {
    scope = $rootScope.$new();
    SearchCtrl = $controller('SearchCtrl', {
      $scope: scope
    });
  }));

  it('should serialize truthy search `params`', function() {
    scope.params = {
      title: 'science',
      journal: ''
    };
    var serialized = SearchCtrl.serialize();
    expect(serialized.title).toBe('science');
    expect(serialized.journal).toBeUndefined();
  });

  it('should serialize search authors', function() {
    scope.authors = [
      {label: 'watson'},
      {label: 'crick'},
      {label: 'franklin'}
    ];
    var serialized = SearchCtrl.serialize();
    expect(serialized.authors).toEqual(['watson', 'crick', 'franklin']);
  });

  it('should serialize search tags', function() {
    scope.tags = [
      {label: 'brain', count: 3},
      {label: 'mind', count: 1}
    ];
    var serialized = SearchCtrl.serialize();
    expect(serialized.tags).toEqual(['brain', 'mind']);
  });

  it('should exclude empty authors or tags', function() {
    var serialized = SearchCtrl.serialize();
    expect(serialized.authors).toBeUndefined();
    expect(serialized.tags).toBeUndefined();
  });

});

