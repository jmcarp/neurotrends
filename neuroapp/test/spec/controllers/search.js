'use strict';

describe('Controller: SearchCtrl', function() {

  beforeEach(module('neuroApp'));

  var SearchCtrl;
  var rootScope;
  var scope;
  var $location;

  beforeEach(inject(function($controller, $rootScope, _$location_) {
    rootScope = $rootScope;
    scope = $rootScope.$new();
    $location = _$location_;
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

  it('should unserialize lists of authors', function() {
    SearchCtrl.unserialize({authors: ['Hodgkin', 'Huxley']});
    expect(scope.authors).toEqual([
      {label: 'Hodgkin'},
      {label: 'Huxley'},
    ]);
  });

  it('should unserialize a single author', function() {
    SearchCtrl.unserialize({tags: ['afni', 'alphasim']});
    expect(scope.tags).toEqual([
      {label: 'afni'},
      {label: 'alphasim'},
    ]);
  });

  it('should unserialize search parameters', function() {
    SearchCtrl.unserialize({title: 'science'});
    expect(scope.params.title).toBe('science');
  });

  it('should add search parameters to location', function() {
    spyOn($location, 'search');
    scope.params.title = 'science';
    SearchCtrl.fetchArticles();
    expect($location.search).toHaveBeenCalledWith({
      title: 'science',
      page_num: 1,    // jshint ignore:line
      page_size: 10,  // jshint ignore:line
    });
  });

  it('should search on load if query parameters', function() {
    spyOn($location, 'search').andReturn({title: 'science'});
    scope.searchForm = {$invalid: true};
    rootScope.$broadcast('$viewContentLoaded', 'testing');
    scope.$apply();
    expect($location.search).toHaveBeenCalled();
    expect(scope.params.title).toBe('science');
  });

  it('should not search on load if not query parameters', function() {
    spyOn($location, 'search').andReturn({});
    rootScope.$broadcast('$viewContentLoaded', 'testing');
    expect($location.search).toHaveBeenCalled();
    expect(scope.params.title).toBe(null);
  });

});
