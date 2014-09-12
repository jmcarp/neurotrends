'use strict';

angular.module('neuroApp')
  .factory('Utils', function() {

    var round = function(value, places) {
      return +value.toFixed(places);
    };

    return {
      round: round
    };

  });

