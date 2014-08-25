'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:NavCtrl
 * @description
 * # NavCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('NavCtrl', function ($scope, $location) {
    $scope.isActive = function(location, startsWith) {
      if (startsWith) {
        return $location.path().indexOf(location) === 0;
      }
      return $location.path() === location;
    };
  });

