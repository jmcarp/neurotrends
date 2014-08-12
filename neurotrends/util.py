# Imports
import time
from bs4 import UnicodeDammit

# Project imports
import neurotrends as nt
from trendpath import *

import os, errno

# From http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def short_name(full_path):
    return os.path.split(full_path)[-1]

def file_path(pmid, file_type, file_info):
    return '%s/%s.%s' % (
        file_info[file_type]['base_path'],
        pmid,
        file_info[file_type]['file_ext']
    )

def retry(f, ntry, delay, *args, **kwargs):
    """
    Retry a function
    Arguments:
        f (function): Function to retry
        ntry (int): Max number of tries
        delay (number): Delay between tries
        args (list): Function arguments
        kwargs (dict): Function keyword arguments
    """

    for tryidx in range(ntry - 1):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            print 'Exception: %s; retrying in %ds...' % (str(e), delay)
            time.sleep(delay)
    return f(*args, **kwargs)


def apply_recursive(func, data):
    if isinstance(data, dict):
        return {
            key: func(value)
            for key, value in data.iteritems()
        }
    if isinstance(data, list):
        return [
            func(value)
            for value in data
        ]
    return func(data)


def string_lower(value):
    try:
        return value.lower()
    except AttributeError:
        return value

