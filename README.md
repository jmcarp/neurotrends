neurotrends
============

NeuroTrends is a collection of tools for identifying, downloading, and analyzing published research articles. Given a PubMed query, NeuroTrends can find research articles, download HTML and PDF download, extract text from PDFs, find arbitrarily complex patterns in text samples, and visualize results.

## Getting Started

* Install GhostScript
* Install Tesseract

Mac:
```bash
$ brew install ghostscript
$ brew install tesseract
```

* Install requirements

```bash
pip install -r requirements.txt
```

## Running Tests

To run all tests:

```bash
$ nosetests
```

To run a particular test class or method:

```bash
$ nosetests tests/test_module.py:TestClass.test_method
```
