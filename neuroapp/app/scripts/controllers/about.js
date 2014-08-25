'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:AboutCtrl
 * @description
 * # AboutCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('AboutCtrl', function ($scope) {
    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
  });
