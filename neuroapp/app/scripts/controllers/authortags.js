'use strict';

/**
 * @ngdoc function
 * @name neuroApp.controller:AuthorTagsCtrl
 * @description
 * # TagsCtrl
 * Controller of the neuroApp
 */
angular.module('neuroApp')
  .controller('AuthorTagsCtrl', function ($scope, $location, Author, Utils, _) {

    // Constants

    var PIX_PER_TAG = 15;

    // Private variables

    var cache = {};
    var queued = [];
    var displayAuthors = [];

    // Public variables

    $scope.series = [];
    $scope.authors = [];
    $scope.height = 200;
    $scope.yAxisTickFormat = function(value) {
      return Utils.round(value, 3);
    };
    $scope.chartStyle = {height: 800};

    $scope.Author = Author;

    // Private functions

    /**
     *
     */
    var sortSeries = function() {
      updateDisplayAuthors();
      var tagCounts = getTagCounts();
      var sortedTags = sortTagCounts(tagCounts);
      $scope.chartStyle.height = PIX_PER_TAG * sortedTags.length;
      $scope.series = _.map(displayAuthors, function(author) {
        return buildSeries(sortedTags, author);
      });
    };

    /**
     *
     */
    var getTagCounts = function() {
      var counts = {};
      _.forEach(displayAuthors, function(author) {
        var cached = cache[author._id];
        _.forEach(cached, function(count, label) {
          if (!counts[label]) {
            counts[label] = count;
          } else {
            counts[label] += count;
          }
        });
      });
      return counts;
    };

    /**
     *
     */
    var sortTagCounts = function(counts) {
      return _.chain(
        counts
      ).map(function(value, key) {
        return [key, value];
      }).sortBy(function(item) {
        return item[1];
      }).map(function(item) {
        return item[0];
      }).reverse()
        .value();
    };

    /**
     *
     */
    var buildSeries = function(tags, author) {
      var values = _.map(tags, function(tag) {
        var count = tag in cache[author._id] ? cache[author._id][tag] : 0;
        return [tag, count];
      });
      return {
        key: author.full,
        values: values
      };
    };

    var updateDisplayAuthors = function() {
      displayAuthors = _.filter($scope.authors, function(author) {
        return author._id in cache;
      });
    };

    var addSeries = function(key, values) {
      $scope.series.push({
        key: key,
        values: values,
      });
    };

    var loadTagsSuccess = function(response) {
      var author = response.data.author;
      cache[author] = response.data.counts;
      sortSeries();
    };

    var enqueueAuthor = function(author) {
      if (cache[author]) {
        addSeries(author, cache[author]);
      } else if (queued.indexOf(author) === -1) {
        queued.push(author);
        Author.tags(author).then(loadTagsSuccess);
      }
    };

    // Listeners

    $scope.$watch('authors', function() {
      for (var i=0; i<$scope.authors.length; i++) {
        enqueueAuthor($scope.authors[i]._id);
      }
      sortSeries();
    }, true);

  });

