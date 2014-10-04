'use strict';

angular.module('neuroApp')
  .factory('Tag', function($http, env) {

    var baseUrl = env.apiUrl + 'tags/';

    var Tag = function(data) {
      angular.extend(this, data);
    };

    Tag.list = function(params) {
      return $http({
        method: 'get',
        url: baseUrl,
        params: params,
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

