'use strict';

angular.module('neuroApp')
  .factory('Author', function($http, env) {

    var baseUrl = env.apiUrl + 'authors/';

    var Author = function(data) {
      angular.extend(this, data);
    };

    Author.get = function(id) {
      return $http.get(baseUrl + id).then(function(response) {
        return new Author(response.data);
      });
    };

    Author.query = function(params) {
      return $http({
        method: 'get',
        url: baseUrl,
        params: params
      }).then(function(response) {
        return response.data.results.map(function(author) {
          return new Author(author);
        });
      });
    };

    Author.tags = function(id) {
      return $http({
        method: 'get',
        url: baseUrl + id + '/tags/',
      });
    };

    return Author;

  });

