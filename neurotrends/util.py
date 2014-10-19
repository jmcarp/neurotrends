#!/usr/bin/env python
# encoding: utf-8

import os
import time
import errno
import weakref


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            return
        raise


def apply_recursive(func, data):
    if isinstance(data, dict):
        return {
            key: apply_recursive(func, value)
            for key, value in data.iteritems()
        }
    if isinstance(data, list):
        return [
            apply_recursive(func, value)
            for value in data
        ]
    return func(data)


class lazyproperty(object):
    """Cached property method decorator.

    :param method: Method to cache
    """
    def __init__(self, method):
        self.data = weakref.WeakKeyDictionary()
        self.method = method

    def __get__(self, instance, owner):
        try:
            return self.data[instance]
        except KeyError:
            value = self.method(instance)
            self.data[instance] = value
            return value
