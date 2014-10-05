'use strict';

angular.module('neuroApp')
  .factory('Tag', function($http, env) {

    var baseUrl = env.apiUrl + 'tags/';

    var countDefaults = {
      normalize: true,
    };
    var versionDefaults = {
      normalize: true,
      threshold: 0.01,
    };

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

    Tag.counts = function(label, options) {
      var params = angular.extend({}, countDefaults, options);
      return $http({
        method: 'get',
        url: baseUrl + label + '/counts/',
        params: params,
      });
    };

    Tag.versions = function(label, options) {
      var params = angular.extend({}, versionDefaults, options);
      return $http({
        method: 'get',
        url: baseUrl + label + '/versions/',
        params: params,
      });
    };

    return Tag;

  });

