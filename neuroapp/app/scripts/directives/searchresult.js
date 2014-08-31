'use strict';

// From https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
function escapeRegex(string){
  return string.replace(/([.*+?^${}()|\[\]\/\\])/g, '\\$1');
}

var highlightText = function(text, highlight, className) {
  className = className || 'highlight';
  var pattern = new RegExp('(' + escapeRegex(highlight) + ')');
  return text.replace(pattern, '<span class="' + className + '">$1</span>');
};

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
      controller: function($scope, $sce) {

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
            ret[key] = $sce.trustAsHtml(
                highlightText(tag.context[key], tag.group[key], 'context-highlight')
            );
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

