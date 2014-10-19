'use strict';

/**
 * @ngdoc function
 * @name neuroappApp.controller:TagDistCtrl
 * @description
 * # TagDistCtrl
 * Controller of the neuroappApp
 */
angular.module('neuroApp')
  .controller('TagDistCtrl', function ($scope, Tag, Utils, _) {

    var self = this;

    // Private variables

    self.cache = {};

    // Public variables

    $scope.chart = {
      tag: null,
      selection: null,
      distances: null,
    };

    // Private methods

    self.prepareDistances = function(distances) {
      return _.map(distances, function(value, key) {
        return {label: key, value: Utils.round(value, 3)};
      });
    };

    // Public methods

    $scope.selectTag = function(label) {
      $scope.chart.tag = label;
      if (self.cache[label]) {
        $scope.chart.distances = self.cache[label];
      } else {
        Tag.distances(label).then(function(response) {
          var prepared = self.prepareDistances(response.data.distances);
          self.cache[label] = prepared.slice(0, 20);
          $scope.chart.distances = self.cache[label];
        });
      }
    };

    $scope.search = function(part) {
      return Tag.list({label: part}).then(function(response) {
        return _.map(response.data, function(item) {
          return item.label;
        });
      });
    };

  });
