'use strict';

/**
 * @ngdoc function
 * @name neuroappApp.controller:PlacetagsCtrl
 * @description
 * # PlaceTagsCtrl
 * Controller of the neuroappApp
 */
angular.module('neuroApp')
  .controller('PlaceTagsCtrl', function ($scope, Tag, Place, Utils, _) {

    var self = this;

    // Private variables

    self.cache = {};

    // Public variables

    $scope.chart = {
      tags: null,
      series: null,
      yAxisTickFormat: function(value) {
        return Utils.round(value, 3);
      }
    };

    $scope.Tag = Tag;

    // Private functions

    self.refreshChart = function() {
      if (_.isEmpty(self.cache)) {
        return;
      }
      $scope.chart.series = _.map($scope.chart.tags, function(tag) {
        var tagSeries = {
          key: tag.label,
          values: _.map(self.cache, function(counts, place) {
            return [place, counts[tag.label] || 0];
          })
        };
        return tagSeries;
      });
    };

    self.fetch = function(count) {
      return Place.topTags({count: count, normalize: true}).then(function(data) {
        self.cache = data;
        self.refreshChart();
      });
    };

    // Listeners

    $scope.$watch('chart.tags', function() {
      self.refreshChart();
    }, true);

    // Initialization

    $scope.$on('$viewContentLoaded', function() {
      self.fetch(10);
    });

  });

