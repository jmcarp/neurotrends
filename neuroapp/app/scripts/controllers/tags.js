'use strict';

var round = function(value, places) {
  return +value.toFixed(places);
};

/**
 * @ngdoc function
 * @name neuroApp.controller:TagsCtrl
 * @description
 * # TagsCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('TagsCtrl', function ($scope, $http, Tag) {

    var cache = {};
    $scope.series = [];
    $scope.tags = [];
    $scope.yAxisTickFormat = function(value) {
      return round(value, 3);
    };

    $scope.Tag = Tag;

    var clearLabels = function() {
      $scope.series = [];
    };

    var enqueueLabel = function(label) {
      if (cache[label]) {
        addSeries(label, cache[label]);
      } else {
        Tag.counts(label).then(loadTagsSuccess);
      }
    };

    var loadTagsSuccess = function(response) {
      var label = response.data.label;
      var series = response.data.counts;
      cache[label] = series;
      $scope.series.push({
        key: label,
        values: series,
      });
    };

    var addSeries = function(key, values) {
      $scope.series.push({
        key: key,
        values: values,
      });
    };

    $scope.$watch('tags', function(oldValue, newValue) {
      clearLabels();
      for (var i=0; i<$scope.tags.length; i++) {
        enqueueLabel($scope.tags[i].label);
      }
    }, true);

  });

