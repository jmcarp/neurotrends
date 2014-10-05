'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:VersionsCtrl
 * @description
 * # VersionsCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('VersionsCtrl', function ($scope, $location, Tag, Utils, _) {

    var self = this;

    // Private variables

    var cache = {};
    var emptyOption = {label: 'Please select a tag'};

    // Public variables

    $scope.chart = {};
    $scope.chart.yAxisTickFormat = function(value) {
      return Utils.round(value, 3);
    };

    // Private functions

    self.getUrlLabel = function() {
      var label = $location.search().label;
      return angular.isArray(label) ? label[0] : label;
    };

    self.setUrlLabel = function(label) {
      $location.search('label', label);
    };

    self.updateLabelFromUrl = function() {
      var urlLabel = self.getUrlLabel();
      var option = _.find($scope.options, function(item) {
        return item.label === urlLabel;
      });
      if (option) {
        $scope.chart.tag = option;
        self.setTag(urlLabel);
      }
    };

    self.fetchTags = function() {
      return Tag.list({versions: true}).then(function(response) {
        $scope.options = [emptyOption].concat(response.data);
        $scope.chart.tag = emptyOption;
        self.updateLabelFromUrl();
      });
    };

    self.parseCounts = function(counts) {
      return _.map(counts.counts, function(value, key) {
        return {
          key: key,
          values: value,
        };
      });
    };

    self.setTag = function(label) {
      if (cache[label]) {
        $scope.chart.series = cache[label];
      } else {
        Tag.versions(label).then(function(response) {
          var counts = self.parseCounts(response.data);
          cache[label] = counts;
          $scope.chart.series = counts;
        });
      }
    };

    // Listeners

    $scope.$watch('chart.tag', function(value) {
      if (value && value !== emptyOption) {
        self.setUrlLabel(value.label);
      }
    });

    $scope.$on('$routeUpdate', function() {
      self.updateLabelFromUrl();
    });

    // Initialization

    $scope.$on('$viewContentLoaded', function() {
      self.fetchTags();
    });

  });

