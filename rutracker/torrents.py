"""Provides functions for managing torrents."""

import re
import time

from HTMLParser import HTMLParser

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


def get_fingerprint(torrent_name):
    """
    Tries to obtain a fingerprint from the torrent name that will uniquely
    identify it's group (TV show).
    """

    # Unescape HTML entities
    torrent_name = HTMLParser().unescape(torrent_name)

    # Drop all tags
    torrent_name = re.sub(r"</?[a-z]+>", "", torrent_name)

    # Drop any additional info: timestamps, release versions, etc.
    # -->
    torrent_name = re.sub(r"\s+/.*", "", torrent_name)

    square_braces_regex = re.compile(r"^(.+)\s+\[[^\[\]]+?\](.*)")
    round_braces_regex = re.compile(r"^(.+)\s+\([^()]+?\)(.*)")
    date_regex = re.compile(ur"^(.+)\s+(?:\d{1,2}\.\d{1,2}\.\d{4}|\d{4}\.\d{2}\.\d{2})(.*)")
    # Unable to merge it into date_regex due to some strange behaviour of re
    # module.
    additional_date_regex = re.compile(ur"^(.+)\s+по\s+(?:\d{1,2}\.\d{1,2}\.\d{4}|\d{4}\.\d{2}\.\d{2})(.*)")

    old_torrent_name = None
    while torrent_name != old_torrent_name:
        old_torrent_name = torrent_name

        for regex in (
            additional_date_regex,
            date_regex,
            square_braces_regex,
            round_braces_regex,
        ):
            torrent_name = regex.sub(r"\1\2", torrent_name.strip(" .,"))
    # <--

    # We need all names in lowercase for easier analysis
    torrent_name = torrent_name.lower()

    # Drop any additional info: timestamps, release versions, etc.
    # -->
    torrent_name = torrent_name.replace(u"г.", "")
    torrent_name = re.sub(ur"(:?выпуск|выпуски|серия|серии|эфир от|эфиры от|обновлено)(?:\s|$)", "", torrent_name)

    for month in (
        u"январь",   u"января",
        u"февраль",  u"февраля",
        u"март",     u"марта",
        u"апрель",   u"апреля",
        u"май",      u"мая",
        u"июнь",     u"июня",
        u"июль",     u"июля",
        u"август",   u"августа",
        u"сентябрь", u"сентября",
        u"октябрь",  u"октября",
        u"ноябрь",   u"ноября",
        u"декабрь",  u"декабря",
    ):
        torrent_name = torrent_name.replace(month, "")
    # <--

    # Try to get most possible short fingerprint
    torrent_name = re.sub(ur"^([0-9a-zа-я, \-:]{6,}(?:[:.?]| - | — |\|)).*", r"\1", torrent_name)

    # Drop all punctuation and other non-alphabet characters
    characters = u"abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщьъыэюя"
    torrent_name = torrent_name.replace(".", " ")
    torrent_name = "".join(
        c for c in torrent_name if c in u" " + characters)

    # Drop several spaces
    torrent_name = re.sub(r"\s+", " ", torrent_name).strip()

    return torrent_name.strip()


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


def update(torrent_id, data, upsert = False):
    """Updates the specified torrent."""

    return coll("torrents").update({ "_id": torrent_id }, { "$set": data },
        upsert = upsert, safe = True)["updatedExisting"]


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
