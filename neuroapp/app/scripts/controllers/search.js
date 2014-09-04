'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:SearchCtrl
 * @description
 * # SearchCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('SearchCtrl', function ($scope, $http, Tag, env) {

    $scope.params = {};
    $scope.paging = {
      currentPage: 1,
      pageSize: 10,
      maxSize: 10,
    };
    $scope.status = {
      loading: false,
      disableSubmit: true,
      showPaging: false,
    };
    $scope.results = {
      numResults: null,
      articles: [],
    };

    $scope.Tag = Tag;

    var handleSuccess = function(response) {
      $scope.searchForm.$setPristine();
      $scope.results.articles = response.data.results;
      $scope.results.numResults = response.data.count;
      $scope.paging.pageStart = ($scope.paging.currentPage - 1) * $scope.paging.pageSize + 1;
      $scope.paging.pageEnd = Math.min($scope.paging.currentPage * $scope.paging.pageSize, $scope.results.numResults);
      $scope.status.loading = false;
      $scope.status.showPaging = true;
    };
    var handleError = function() {
      $scope.status.loading = false;
    };

    $scope.setPage = function() {
      fetchArticles();
    };

    $scope.$watch('[params, tags, searchForm.$invalid, searchForm.$pristine]', function() {
      var form = $scope.searchForm;
      if (!form || form.$invalid || form.$pristine) {
        $scope.status.disableSubmit = true;
        return;
      }
      var serialized = serialize();
      $scope.status.disableSubmit = Object.keys(serialized).length === 0;
    }, true);

    var serialize = function() {
      var ret = {};
      angular.forEach($scope.params, function(key, value) {
        if (value) {
          ret[key] = value;
        }
      });
      if ($scope.authors.length) {
        ret.authors = $scope.authors.map(function(item) {
          return item.label;
        });
      }
      if ($scope.tags.length) {
        ret.tags = $scope.tags.map(function(item) {
          return item.label;
        });
      }
      ret.page_num = $scope.paging.currentPage;  // jshint ignore:line
      ret.page_size = $scope.paging.pageSize;    // jshint ignore:line
      return ret;
    };

    var fetchArticles = function() {
      $scope.status.loading = true;
      $scope.results.articles = [];
      $http({
        method: 'get',
        url: env.apiUrl + 'articles/',
        params: serialize()
      }).then(
        handleSuccess,
        handleError
      );
    };

    $scope.submit = function(form) {
      if (form.$invalid) {
        return;
      }
      $scope.paging.currentPage = 1;
      $scope.status.showPaging = false;
      fetchArticles();
    };

  });

