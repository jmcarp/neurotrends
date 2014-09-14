'use strict';

var app = angular.module('neuroApp');

app.factory('_', function() {
  return window._;
});

app.factory('moment', function() {
  return window.moment;
});

