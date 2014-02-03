"""Database utilities."""

import threading

import pymongo


_CONNECTION = None
"""MongoDB connection."""

_LOCK = threading.Lock()
"""_CONNECTION object lock."""


def coll(name):
    """Returns the specified MongoDB collection."""

    return db()[name]


def db():
    """Returns the MongoDB database."""

    global _CONNECTION
    connection = _CONNECTION

    if connection is None:
        excessive_connection = connection = pymongo.MongoClient()

        try:
            with _LOCK:
                if _CONNECTION is None:
                    _CONNECTION, excessive_connection = connection, None
                else:
                    connection = _CONNECTION
        finally:
            if excessive_connection is not None:
                excessive_connection.close()

    return connection["rutracker"]
