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
    'nvd3ChartDirectives',
    'monospaced.elastic',
    'config'
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
      .when('/trends/tags', {
        templateUrl: 'views/tags.html',
        controller: 'TagsCtrl',
        reloadOnSearch: false
      })
      .when('/trends/authors', {
        templateUrl: 'views/author-tags.html',
        controller: 'AuthorTagsCtrl'
      })
      .when('/trends/places', {
        templateUrl: 'views/place-tags.html',
        controller: 'PlaceTagsCtrl'
      })
      .when('/tools/extract', {
        templateUrl: 'views/extract.html',
        controller: 'ExtractCtrl'
      })
      .when('/api', {
        templateUrl: 'views/api.html',
        controller: 'ApiCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });

