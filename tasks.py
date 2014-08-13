# -*- coding: utf-8 -*-

from invoke import task, run


DB_PATH = '/usr/local/var/mongodb'
LOG_PATH = '/usr/local/var/log/mongodb/mongo.log'


# TODO: Add port, database name to MongoDB tasks

@task
def mongod(db_path=DB_PATH, fork=False, log_path=LOG_PATH):
    cmd = 'mongod --dbpath {0}'.format(db_path)
    if fork:
        cmd += ' --fork'
    if log_path:
        cmd += ' --logpath {0}'.format(log_path)
    run(cmd)


@task
def mongodump(out_path=None):
    cmd = 'mongodump --db neurotrends'
    if out_path:
        cmd += ' --out {0}'.format(out_path)
    run(cmd)


@task
def mongorestore(db_path=DB_PATH, path=None, drop=False):
    cmd = 'mongorestore --db neurotrends'
    if drop:
        cmd += ' --drop'
    if path:
        cmd += path
    run(cmd)


@task
def install_conda():
    cmd = 'conda install --file conda-requirements.txt'
    run(cmd)


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

