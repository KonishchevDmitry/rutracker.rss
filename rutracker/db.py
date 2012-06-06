"""Database utilities."""

import pymongo


def coll(name):
    """Returns the specified MongoDB collection."""

    return _db()[name]


def _db():
    """Returns the MongoDB database."""

    connection = pymongo.Connection()
    return connection["rutracker"]
