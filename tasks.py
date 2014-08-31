# -*- coding: utf-8 -*-

import datetime

from invoke import task, run


DB_PATH = '/usr/local/var/mongodb'
LOG_PATH = '/usr/local/var/log/mongodb/mongo.log'


# TODO: Add port, database name to MongoDB tasks

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
    cmd = 'python -m scripts.count_tags'
    run(cmd)


@task
def get_stats():
    cmd = 'python -m scripts.get_stats'
    run(cmd)


@task
def mongodump(path=None):
    cmd = 'mongodump --db neurotrends'
    if path:
        cmd += ' --out {0}'.format(path)
    run(cmd)


@task
def mongorestore(path='dump/neurotrends', drop=False):
    cmd = 'mongorestore --db neurotrends'
    if drop:
        cmd += ' --drop'
    cmd += ' ' + path
    run(cmd)


@task
def test(path='tests'):
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
def rescrape(processes=2, months=6, limit=50, overwrite=False):
    from dateutil.relativedelta import relativedelta
    from modularodm import Q
    from scripts import retag
    cutoff_date = datetime.datetime.utcnow() - relativedelta(months=months)
    query = (
        (
            Q('date_last_scraped', 'lt', datetime.datetime.utcnow()) |
            Q('date_last_scraped', 'eq', None)
        ) &
        Q('verified.0', 'exists', False)
    )
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
    run('python api.py')

