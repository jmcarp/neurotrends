'use strict';

/**
 * @ngdoc function
 * @name neuroappApp.controller:PlacetagsCtrl
 * @description
 * # PlaceTagsCtrl
 * Controller of the neuroappApp
 */
angular.module('neuroApp')
  .controller('PlaceTagsCtrl', function ($scope, Tag, Place, _) {

    var self = this;

    // Private variables

    self.cache = {};

    // Public variables

    $scope.series = [];
    $scope.tags = [];

    $scope.Tag = Tag;

    // Private functions

    self.refreshChart = function() {
      if (_.isEmpty(self.cache)) {
        return;
      }
      $scope.series = _.map($scope.tags, function(tag) {
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

    $scope.$watch('tags', function() {
      self.refreshChart();
    }, true);

    // Initialization

    $scope.$on('$viewContentLoaded', function() {
      self.fetch(10);
    });

  });

