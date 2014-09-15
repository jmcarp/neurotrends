'use strict';

describe('Service: Author', function() {

  var Author;
  var env;
  var httpBackend;

  beforeEach(module('neuroApp'));

  beforeEach(inject(function(_Author_, _env_, $httpBackend) {
    Author = _Author_;
    env = _env_;
    httpBackend = $httpBackend;
  }));

  it('should extend data to `this`', function() {
    var article = new Author({full: 'Nye B'});
    expect(article.full).toBe('Nye B');
  });

  it('should load an `Author` from `get`', function() {
    httpBackend.whenGET(env.apiUrl + 'authors/1').respond({
      full: 'Tyson N'
    });
    Author.get('1').then(function(author) {
      expect(author instanceof Author).toBeTruthy();
      expect(author.full).toBe('Tyson N');
    });
    httpBackend.flush();
  });

  it('should load `Author`s from `query`', function() {
    var names = ['Louis Pasteur', 'Louis Braille'];
    httpBackend.whenGET(env.apiUrl + 'authors/?fullname=louis').respond({
      results: _.map(names, function(name) {return {full: name};}),
      count: 2
    });
    Author.query({fullname: 'louis'}).then(function(authors) {
      _.forEach(authors, function(author, idx) {
        expect(author instanceof Author).toBeTruthy();
        expect(author.full).toBe(names[idx]);
      });
    });
    httpBackend.flush();
  });

  it('should load author tags', function() {
    var authorId = '1';
    var counts = {'science': 1};
    httpBackend.expectGET(env.apiUrl + 'authors/1/tags/').respond({
      author: authorId,
      counts: counts
    });
    Author.tags(authorId).then(function(response) {
      expect(response.data.author).toBe(authorId);
      expect(response.data.counts).toEqual(counts);
    });
    httpBackend.flush();
  });

});

