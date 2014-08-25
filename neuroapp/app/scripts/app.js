'use strict';

/**
 * @ngdoc overview
 * @name neuroApp
 * @description
 * # neuroApp
 *
 * Main module of the application.
 */
var app = angular
  .module('neuroApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTagsInput',
    'ui.bootstrap',
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .when('/about', {
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl'
      })
      .when('/search', {
        templateUrl: 'views/search.html',
        controller: 'SearchCtrl'
      })
      .when('/api', {
        templateUrl: 'views/api.html',
	controller: 'ApiCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });

app.constant('config', {
  'apiUrl': 'http://localhost:5000/'
});

