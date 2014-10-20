#!/usr/bin/env python
# encoding: utf-8

import os
import datetime

from invoke import task, run


DB_PATH = '/usr/local/var/mongodb'
LOG_PATH = '/usr/local/var/log/mongodb/mongo.log'
MONGO_CACHE_PATH = 'fixtures/mongo/cache'


# TODO: Add port, database name to MongoDB tasks

@task
def clear_pyc():
    run('find . | grep "\.pyc$" | xargs rm')


@task
def mongoserver(db_path=DB_PATH, fork=False, log_path=LOG_PATH):
    cmd = 'mongod --dbpath {0}'.format(db_path)
    if fork:
        cmd += ' --fork'
    if log_path:
        cmd += ' --logpath {0}'.format(log_path)
    run(cmd)


@task
def mongoclient():
    cmd = 'mongo neurotrends'
    run(cmd, pty=True)


@task
def count_tags():
    from scripts import count_tags
    count_tags.cache_counts()


@task
def get_stats():
    from scripts import stats
    stats.cache_stats()


@task
def get_distances():
    from neurotrends.analysis import distance
    distance.cache_distances()


@task
def mongodump(path=None, collection=None):
    cmd = 'mongodump --db neurotrends'
    if path:
        cmd += ' --out {0}'.format(path)
    if collection:
        cmd += ' --collection {0}'.format(collection)
    run(cmd)


@task
def mongorestore(path='dump/neurotrends', collection=None, drop=False):
    cmd = 'mongorestore --db neurotrends'
    if collection:
        cmd += ' --collection {0}'.format(collection)
    if drop:
        cmd += ' --drop'
    cmd += ' ' + path
    run(cmd)


@task
def dump_cache():
    mongodump(path=MONGO_CACHE_PATH, collection='cache')


@task
def restore_cache():
    mongorestore(
        path=os.path.join(MONGO_CACHE_PATH, 'neurotrends', 'cache.bson'),
        collection='cache',
        drop=True,
    )


@task
def test(path='tests'):
    clear_pyc()
    cmd = 'py.test'
    if path:
        cmd += ' ' + path
    run(cmd, pty=True)


@task
def install_conda(yes=False):
    cmd = 'conda install --file conda-requirements.txt'
    if yes:
        cmd += ' --yes'
    run(cmd, pty=True)


@task
def install_pip(upgrade=False):
    cmd = 'pip install -r requirements.txt'
    if upgrade:
        cmd += ' --upgrade'
    run(cmd)


@task
def install(upgrade=False):
    install_conda()
    install_pip(upgrade=upgrade)


@task
def piprot():
    run('piprot requirements.txt conda-requirements.txt')


@task
def ensure_indices():
    from neurotrends.model import indices
    indices.ensure_indices()


@task
def scrape(max_count=100, randomize=True):
    from neurotrends import config
    from neurotrends.model import scripts
    scripts.add_missing(config.query, max_count, randomize)


@task
def retag(processes=2):
    from scripts import retag
    retag.batch_retag(processes=processes)


@task
def rescrape(processes=1, months=6, limit=50, missing='any', overwrite=False):
    """
    :param int processes: Number of processes to launch
    :param int months: Minimum time since last scraped
    :param int limit: Max number of articles to scrape
    :param str missing: Missing document type (html, pdf, pmc, any)
    :param bool overwrite: Overwrite existing articles
    """
    from dateutil.relativedelta import relativedelta
    from modularodm import Q
    from scripts import retag
    cutoff_date = datetime.datetime.utcnow() - relativedelta(months=months)
    query = (
        Q('date_last_scraped', 'lt', cutoff_date) |
        Q('date_last_scraped', 'eq', None)
    )
    if missing == 'any':
        query = query & Q('verified.0', 'exists', False)
    else:
        query = query & Q('verified', 'ne', missing)
    retag.batch_rescrape(
        processes=processes,
        query=query,
        limit=limit,
        overwrite=overwrite,
    )


@task
def update_dates(overwrite=False):
    from scripts import update
    update.update_dates(overwrite=overwrite)


@task
def serve_api():
    clear_pyc()
    from api import app
    app.run()
