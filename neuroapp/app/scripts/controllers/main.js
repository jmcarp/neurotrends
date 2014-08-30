'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('MainCtrl', function ($scope, $http, env) {
    $scope.stats = {};
    $scope.statsLoaded = false;

    var loadStats = function() {
      $http({
        method: 'get',
        url: env.apiUrl + 'stats/',
      }).then(function(response) {
        $scope.stats = response.data;
        $scope.statsLoaded = true;
      });
    };

    loadStats();
  });

