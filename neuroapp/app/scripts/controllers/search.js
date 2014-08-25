'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:SearchCtrl
 * @description
 * # SearchCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('SearchCtrl', function ($scope, $http, config) {

    $scope.params = {};
    $scope.results = [];
    $scope.paging = {
      pageSize: 10,
      maxSize: 10
    };
    $scope.disableSubmit = true;

    var updateResults = function(results) {
      if ($scope.searchForm) {
      	$scope.searchForm.$setPristine();
      }
      $scope.results = results;
    };
    var handleSuccess = function(response) {
      updateResults(response.data.results);
      $scope.paging.numResults = response.data.count;
    };
    var handleError = function() {};

    $scope.setPage = function() {
      fetchArticles();
    };

    $scope.$watch('[params, tags, searchForm.$invalid, searchForm.$pristine]', function() {
      var form = $scope.searchForm;
      if (!form || form.$invalid || form.$pristine) {
	$scope.disableSubmit = true;
	return;
      }
      var serialized = serialize();
      $scope.disableSubmit = Object.keys(serialized).length === 0;
    }, true);

    var serialize = function() {
      var ret = {};
      angular.forEach($scope.params, function(key, value) {
	if (value) {
	  ret[key] = value;
	}
      });
      if ($scope.tags.length) {
        ret.tags = $scope.tags.map(function(item) {
	  return item.label;
	});
      }
      ret.page_num = $scope.paging.currentPage;  // jshint ignore:line
      ret.page_size = $scope.paging.pageSize;    // jshint ignore:line
      return ret;
    };

    $scope.fetchTags = function(query) {
      return $http({
        method: 'get',
        url: config.apiUrl + 'tags/',
        params: {
          label: query
        }
      });
    };

    var fetchArticles = function() {
      $scope.results = [];
      $http({
	    method: 'get',
	    url: config.apiUrl + 'articles/',
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
      fetchArticles();
    };

  });

