'use strict';

/**
 * @ngdoc function
 * @name neuroApp.directive:SearchResult
 */
angular.module('neuroApp')
  .directive('searchResult', function() {
    return {
      restrict: 'E',
      scope: {
        result: '='
      },
      templateUrl: 'scripts/directives/search-result.html',
      controller: function($scope) {

        $scope.showTags = false;
        $scope.tagIndex = null;
        $scope.tagContext = {};

        $scope.toggleTags = function() {
          $scope.showTags = ! $scope.showTags;
        };

        $scope.makeLabel = function(tag) {
          var label = tag.label;
          if (tag.version && tag.version !== '?') {
            label += '[version=' + tag.version + ']';
          }
          if (tag.value) {
            label += '[value=' + tag.value + ']';
          }
          return label;
        };

        $scope.highlightTag = function(index) {
          if ($scope.tagIndex === index) {
            $scope.tagIndex = null;
            $scope.tagContext = {};
          } else {
            $scope.tagIndex = index;
            $scope.tagContext = $scope.result.tags[index].context;
          }
        };

      }
    };
  });

