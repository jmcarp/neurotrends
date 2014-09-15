'use strict';

angular.module('neuroApp')
  .factory('Article', function($http, env) {

    var baseUrl = env.apiUrl + 'articles/';

    var Article = function(data) {
      angular.extend(this, data);
    };

    Article.get = function(id) {
      return $http.get(baseUrl + id).then(function(response) {
        return new Article(response.data);
      });
    };

    Article.query = function(params) {
      return $http({
        method: 'get',
        url: baseUrl,
        params: params
      }).then(function(response) {
        response.data.results = response.data.results.map(function(article) {
          return new Article(article);
        });
        return response.data;
      });
    };

    return Article;

  });

