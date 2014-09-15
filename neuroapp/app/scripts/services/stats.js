'use strict';

angular.module('neuroApp')
  .factory('Stats', function($http, env) {

    var baseUrl = env.apiUrl + 'stats/';

    var Stats = {};

    Stats.get = function() {
      return $http({
        method: 'get',
        url: baseUrl
      });
    };

    return Stats;

  });

