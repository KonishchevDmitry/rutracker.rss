"""Database utilities."""

from __future__ import unicode_literals

import pymongo


def coll(name):
    """Returns the specified MongoDB collection."""

    return db()[name]


def db():
    """Returns the MongoDB database."""

    connection = pymongo.Connection()
    return connection["rutracker"]
