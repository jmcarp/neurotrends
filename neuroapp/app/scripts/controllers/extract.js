'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:ExtractCtrl
 * @description
 * # ExtractCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('ExtractCtrl', function ($scope, Extract, Utils, _) {

    var self = this;

    $scope.disableSubmit = true;
    $scope.params = {};
    $scope.tags = null;

    self.renderTags = function(tags) {
      _.forEach(tags, function(item) {
        item.highlight = Utils.highlightText(
          item.context,
          item.group,
          'context-highlight'
        );
      });
      $scope.tags = tags;
      $scope.extractForm.$setPristine();
    };

    $scope.submit = function() {
      if (!$scope.extractForm.$valid) {
        return;
      }
      Extract.extract(
        $scope.params.text
      ).then(
        self.renderTags
      );
    };

    $scope.$watch('[extractForm.$invalid, extractForm.$pristine]', function() {
      var form = $scope.extractForm;
      $scope.disableSubmit = !form || form.$invalid || form.$pristine;
    }, true);

  });

