'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('MainCtrl', function ($scope, Stats) {
    $scope.stats = {};
    $scope.statsLoaded = false;

    var loadStats = function() {
      Stats.get().then(function(stats) {
        $scope.stats = stats;
        $scope.statsLoaded = true;
      });
    };

    loadStats();
  });

