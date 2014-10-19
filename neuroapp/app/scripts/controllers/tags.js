'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:TagsCtrl
 * @description
 * # TagsCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('TagsCtrl', function ($scope, $location, Tag, Utils) {

    // Private variables

    var cache = {};
    var queued = [];

    // Public variables

    $scope.series = [];
    $scope.tags = [];
    $scope.permalink = null;
    $scope.yAxisTickFormat = function(value) {
      return Utils.round(value, 3);
    };

    $scope.Tag = Tag;

    // Private functions

    var clearLabels = function() {
      $scope.series = [];
    };

    var enqueueLabel = function(label) {
      if (cache[label]) {
        addSeries(label, cache[label]);
      } else if (queued.indexOf(label) === -1) {
        queued.push(label);
        Tag.counts(label).then(loadTagsSuccess);
      }
    };

    var sortSeries = function() {
      var label;
      var series = [];
      for (var i=0; i<$scope.tags.length; i++) {
        label = $scope.tags[i].label;
        if (cache[label]) {
          series.push({
            key: label,
            values: cache[label]
          });
        }
      }
      $scope.series = series;
    };

    var loadTagsSuccess = function(response) {
      var label = response.data.label;
      var series = response.data.counts;
      cache[label] = series;
      sortSeries();
    };

    var addSeries = function(key, values) {
      $scope.series.push({
        key: key,
        values: values,
      });
    };

    var labelsFromUrl = function() {
      var labels = $location.search().label;
      if (!labels || labels === true) {
        return [];
      }
      return Utils.ensureArray(labels);
    };

    var setParamsFromTags = function() {
      $location.search('label', $scope.tags.map(function(tag) {
        return tag.label;
      }));
    };

    var getTagsFromParams = function() {
      var labels = labelsFromUrl();
      $scope.tags = labels.map(function(label) {
        return {label: label};
      });
    };

    var setPermalink = function() {
      $scope.permalink = $location.absUrl();
    };

    // Listeners

    $scope.$watch('tags', function() {
      clearLabels();
      setParamsFromTags();
      setPermalink();
      for (var i=0; i<$scope.tags.length; i++) {
        enqueueLabel($scope.tags[i].label);
      }
    }, true);

    $scope.$on('$routeUpdate', function() {
      getTagsFromParams();
    });

    // Check URL parameters on load
    getTagsFromParams();

  });
