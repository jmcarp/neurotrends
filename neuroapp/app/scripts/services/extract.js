'use strict';

angular.module('neuroApp')
  .factory('Extract', function($http, env) {

    var baseUrl = env.apiUrl + 'extract/';

    var Extract = {};

    Extract.extract = function(text) {
      return $http({
        method: 'post',
        url: baseUrl,
        data: {text: text}
      }).then(function(response) {
        return response.data.tags;
      });
    };

    return Extract;

  });

