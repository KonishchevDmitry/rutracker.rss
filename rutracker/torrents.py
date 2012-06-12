"""Provides functions for managing torrents."""

import time

import pymongo

import rutracker.blacklist
from rutracker.db import coll

# TODO: blacklist


def find(age = None, sort = False, limit = None):
    """Returns the specified torrents."""

    query = {}

    if age is not None:
        query["time"] = { "$gte": time.time() - age }

    torrents = coll("torrents").find(query)

    if sort:
        torrents = torrents.sort([( "time", pymongo.DESCENDING )])

    if limit is not None:
        torrents = torrents.limit(limit)

    return torrents


def find_one(torrent_id):
    """Finds the specified torrent."""

    return coll("torrents").find_one({ "_id": torrent_id })


def get_stats(blacklist = False):
    """Returns torrent statistics."""

    query = _blacklist_query() if blacklist else {}

    torrents = coll("torrents").group(
        [ "fingerprint" ], query, { "count": 0 }, """
        function(obj, aggregated) {
            aggregated.name = obj.name;
            aggregated.count++;
        }"""
    )
    torrents.sort(key = lambda a: a["count"], reverse = True)

    return torrents


def update(torrent_id, data):
    """Updates the specified torrent."""

    coll("torrents").update({ "_id": torrent_id }, { "$set": data },
        upsert = True, safe = True)


def _blacklist_query():
    """Returns query that blacklists torrents."""

    query = {}
    blacklist = []

    for rule in rutracker.blacklist.find():
        blacklist.append({
            "fingerprint": { "$regex": rule["_id"] } if rule.get("regex", False) else rule["_id"] })

    if blacklist:
        query["$nor"] = blacklist

    return query
