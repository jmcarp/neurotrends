.. image:: https://travis-ci.org/jmcarp/neurotrends.png?branch=master
    :target: https://travis-ci.org/jmcarp/neurotrends

neurotrends
============

NeuroTrends is a collection of tools for identifying, downloading, and analyzing published research articles. Given a PubMed query, NeuroTrends can find research articles, download HTML and PDF download, extract text from PDFs, find arbitrarily complex patterns in text samples, and visualize results.

## Getting Started

# Install system dependencies

```bash
$ brew bundle
```

# Install python dependencies

```bash
$ pip install invoke
$ invoke install
```

## Running Tests

```bash
$ invoke test
```

