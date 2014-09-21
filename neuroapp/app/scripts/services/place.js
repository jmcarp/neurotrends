'use strict';

angular.module('neuroApp')
  .factory('Place', function($http, env) {

    var baseUrl = env.apiUrl + 'places/';

    var Place = function(data) {
      angular.extend(this, data);
    };

    Place.list = function(part) {
      return $http({
        method: 'get',
        url: baseUrl,
        params: {
          label: part
        },
      });
    };

    Place.tags = function(place) {
      return $http({
        method: 'get',
        url: baseUrl + place + '/tags/',
      });
    };

    Place.topTags = function(params) {
      return $http({
        method: 'get',
        url: baseUrl + 'tags/top/',
        params: params,
      }).then(function(response) {
        return response.data;
      });
    };

    return Place;

  });

