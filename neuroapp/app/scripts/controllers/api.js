'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:ApiCtrl
 * @description
 * # ApiCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('ApiCtrl', function ($scope, config) {
    $scope.apiUrl = config.apiUrl;
  });

