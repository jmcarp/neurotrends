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
      controller: function($scope, Utils, moment) {

        $scope.showTags = false;
        $scope.tagIndex = null;
        $scope.tagContext = {};

        $scope.date = moment($scope.result.date);

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

        var formatContext = function(tag) {
          var ret = {};
          var keys = Object.keys(tag.context);
          var key;
          for (var i=0; i<keys.length; i++) {
            key = keys[i];
            ret[key] = Utils.highlightText(tag.context[key], tag.group[key], 'context-highlight');
          }
          return ret;
        };

        $scope.highlightTag = function(index) {
          if ($scope.tagIndex === index) {
            $scope.tagIndex = null;
            $scope.tagContext = {};
          } else {
            $scope.tagIndex = index;
            $scope.tagContext = formatContext($scope.result.tags[index]);
          }
        };

        $scope.pubMedUrl = function(pmid) {
          return 'http://www.ncbi.nlm.nih.gov/pubmed/' + pmid;
        };
        $scope.crossRefUrl = function(doi) {
          return 'http://dx.doi.org/' + doi;
        };

      }
    };
  });

