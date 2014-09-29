'use strict';

angular.module('neuroApp')
  .factory('Links', function(_) {

    var Links = {};

    var linkTypes = {
      doi: {
        key: 'doi',
        label: 'CrossRef',
        icon: '/images/crossref.ico',
        buildUrl: function(doi) {
          return 'http://dx.doi.org/' + doi;
        }
      },
      pmid: {
        key: 'pmid',
        label: 'PubMed',
        icon: '/images/pubmed.ico',
        buildUrl: function(pmid) {
          return 'http://www.ncbi.nlm.nih.gov/pubmed/' + pmid;
        }
      },
      neuroSynth: {
        key: 'pmid',
        label: 'NeuroSynth',
        buildUrl: function(pmid) {
          return 'http://neurosynth.org/studies/' + pmid;
        }
      },
    };

    Links.buildLink = function(article, type) {
      var linkType = linkTypes[type];
      var value = article[linkType.key];
      return {
        label: linkType.label,
        icon: linkType.icon,
        href: linkType.buildUrl(value)
      };
    };

    Links.buildLinks = function(article, types) {
      types = types || Object.keys(linkTypes);
      return _.map(types, function(type) {
        return Links.buildLink(article, type);
      });
    };

    return Links;

  });

