'use strict';

describe('Controller: PlaceTagsCtrl', function () {

  // load the controller's module
  beforeEach(module('neuroApp'));

  var PlaceTagsCtrl;
  var scope;
  var rootScope;
  var q;
  var Place;

  var mockData = {
    Michigan: {
      spm: 5,
      fsl: 2
    },
    Illinois: {
      fsl: 7
    }
  };

  var mockSeries = [
    {key: 'spm', values: [['Michigan', 5], ['Illinois', 0]]},
    {key: 'fsl', values: [['Michigan', 2], ['Illinois', 7]]}
  ];

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope, $q, _Place_) {
    scope = $rootScope.$new();
    PlaceTagsCtrl = $controller('PlaceTagsCtrl', {
      $scope: scope
    });
    rootScope = $rootScope;
    q = $q;
    Place = _Place_;
  }));

  it('should fetch tag counts', function() {
    var deferred = q.defer();
    spyOn(Place, 'topTags').andReturn(deferred.promise);
    PlaceTagsCtrl.fetch(10).then(function() {
      expect(PlaceTagsCtrl.cache).toEqual(mockData);
    });
    expect(Place.topTags).toHaveBeenCalledWith({count: 10, normalize: true});
    deferred.resolve(mockData);
    rootScope.$apply();
  });

  it('should skip refreshChart if cache is empty', function() {
    PlaceTagsCtrl.cache = {};
    scope.tags = [{label: 'spm'}, {label: 'fsl'}];
    PlaceTagsCtrl.refreshChart();
    expect(scope.chart.series).toEqual(null);
  });

  it('should refresh series data if cache is not empty', function() {
    PlaceTagsCtrl.cache = mockData;
    scope.chart.tags = [{label: 'spm'}, {label: 'fsl'}];
    scope.chart.series = [];
    PlaceTagsCtrl.refreshChart();
    expect(scope.chart.series).toEqual(mockSeries);
  });

});

