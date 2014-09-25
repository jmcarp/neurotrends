'use strict';

angular.module('neuroApp')
  .factory('Utils', function($sce) {

    var round = function(value, places) {
      return +value.toFixed(places);
    };

    // From https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
    function escapeRegex(string){
      return string.replace(/([.*+?^${}()|\[\]\/\\])/g, '\\$1');
    }

    var highlightText = function(text, highlight, className) {
      className = className || 'highlight';
      var pattern = new RegExp('(' + escapeRegex(highlight) + ')');
      var wrapped = text.replace(pattern, '<span class="' + className + '">$1</span>');
      return $sce.trustAsHtml(wrapped);
    };

    return {
      round: round,
      highlightText: highlightText
    };

  });

