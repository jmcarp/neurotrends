'use strict';

angular.module('neuroApp')
  .factory('Tag', function($http, env) {

    var baseUrl = env.apiUrl + 'tags/';

    var Tag = function(data) {
      angular.extend(this, data);
    };

    Tag.list = function(part) {
      return $http({
        method: 'get',
        url: baseUrl,
        params: {
          label: part
        },
      });
    };

    Tag.counts = function(label, normalize) {
      normalize = typeof(normalize) === 'undefined' ? true : normalize;
      return $http({
        method: 'get',
        url: baseUrl + label + '/counts/',
        params: {normalize: normalize},
      });
    };

    return Tag;

  });

