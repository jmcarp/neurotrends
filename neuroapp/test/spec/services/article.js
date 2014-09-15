'use strict';

describe('Service: Article', function() {

  var Article;
  var env;
  var httpBackend;

  beforeEach(module('neuroApp'));

  beforeEach(inject(function(_Article_, _env_, $httpBackend) {
    Article = _Article_;
    env = _env_;
    httpBackend = $httpBackend;
  }));

  it('should extend data to `this`', function() {
    var article = new Article({title: 'how to science'});
    expect(article.title).toBe('how to science');
  });

  it('should load an `Article` from `get`', function() {
    httpBackend.whenGET(env.apiUrl + 'articles/1').respond({
      title: 'how to science'
    });
    Article.get('1').then(function(article) {
      expect(article instanceof Article).toBeTruthy();
      expect(article.title).toBe('how to science');
    });
    httpBackend.flush();
  });

  it('should load `Article`s from `query`', function() {
    var titles = ['good science', 'bad science', 'ugly science'];
    httpBackend.whenGET(env.apiUrl + 'articles/?title=science').respond({
      results: _.map(titles, function(title) {return {title: title};}),
      count: 3
    });
    Article.query({title: 'science'}).then(function(data) {
      _.forEach(data.results, function(article, idx) {
        expect(article instanceof Article).toBeTruthy();
        expect(article.title).toBe(titles[idx]);
      });
    });
    httpBackend.flush();
  });

});

