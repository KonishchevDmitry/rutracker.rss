# -*- coding: utf-8 -*-

"""Provides functions for managing torrents."""

import re
import time

from html.parser import HTMLParser

import pymongo

import rutracker.blacklist

from rutracker import config
from rutracker.database import coll, db


def compact():
    """Compacts the database by removing data that is not already needed."""

    coll("torrents").remove({
        "time": { "$lt": int(time.time()) - config.MAX_TORRENT_AGE } })

    coll("torrents").update({
        "time": { "$lt": int(time.time()) - config.MAX_FEED_AGE }
    },{
        "$unset": { "description": True }
    }, multi = True)

    db().command("compact", "torrents")


def find(age = None, blocklist = False, sort = False, limit = None, fields = None):
    """Returns the specified torrents."""

    query = {}

    if age is not None:
        query["time"] = { "$gte": time.time() - age }

    if blocklist:
        query.update(_blacklist_query())

    torrents = coll("torrents").find(query, fields = fields)

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

    # Minimize typing differences
    torrent_name = torrent_name.replace("ё", "е")

    # Unescape HTML entities
    torrent_name = HTMLParser().unescape(torrent_name)

    # Drop all tags
    torrent_name = re.sub(r"</?[a-z]+>", "", torrent_name)

    # Drop any additional info: timestamps, release versions, etc.
    # -->
    square_braces_regex = re.compile(r"^(.+(?:\s+|\)))\[[^\[\]]+?\](.*)$")
    preceding_square_braces_regex = re.compile(r"^(\s*)\[[^\[\]]+?\](.+)$")
    round_braces_regex = re.compile(r"^(.+(?:\s+|\]))\([^()]+?\)(.*)$")
    angle_braces_regex = re.compile(r"^(.+)\s+<<.*?>>(.*)$")
    date_regex = re.compile(r"^(.+)\s+(?:\d{1,2}\.\d{1,2}\.\d{4}|\d{4}\.\d{2}\.\d{2})(.*)$")
    # Unable to merge it into date_regex due to some strange behaviour of re
    # module.
    additional_date_regex = re.compile(r"^(.+)\s+(?:по|от)\s+(?:\d{1,2}\.\d{1,2}\.\d{4}|\d{4}\.\d{2}\.\d{2})(.*)$")
    release_counter_regex = re.compile(r"^(.+)\s+\d+\s*(?:в|из)\s*\d+(.*)$")

    old_torrent_name = None
    while torrent_name != old_torrent_name:
        old_torrent_name = torrent_name

        for regex in (
            additional_date_regex,
            date_regex,
            preceding_square_braces_regex,
            square_braces_regex,
            round_braces_regex,
            angle_braces_regex,
            release_counter_regex,
        ):
            torrent_name = regex.sub(r"\1\2", torrent_name.strip(" .,"))

    torrent_name = re.sub(r"\s+/.*", "", torrent_name)
    # <--

    # We need all names in lowercase for easier analysis
    torrent_name = torrent_name.lower()

    # Try to get most possible short fingerprint -->
    torrent_name = re.sub(r"^(national\s+geographic\s*:|наука\s+2\.0)\s+", "", torrent_name)

    torrent_name = re.sub(
        r"^«([^»]{6,})»", r"\1", torrent_name)

    torrent_name = re.sub(
        r'^"([^»]{6,})"', r"\1", torrent_name)

    torrent_name = re.sub(
        r"^([0-9a-zабвгдеёжзийклмнопрстуфхцчшщьъыэюя., \-:]{6,}?(?:[:.?!]| - | — |\|)).*", r"\1", torrent_name)
    # Try to get most possible short fingerprint <--

    # Drop all punctuation and other non-alphabet characters
    characters = "abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщьъыэюя"
    torrent_name = torrent_name.replace(".", " ")
    torrent_name = "".join(
        c for c in torrent_name if c in " " + characters)

    # Drop any additional info: timestamps, release versions, etc.
    # -->
    torrent_name = torrent_name.replace("г.", "")
    while True:
        new_torrent_name = re.sub(r"(?:\s|\()(:?выпуск|выпуски|выпусков|обновлено|передачи за|серия из|сезон|серия|серии|премьера|эфир с|эфир от|эфиры от|satrip)(?:\s|\)|$)", "", torrent_name)
        if new_torrent_name == torrent_name:
            break
        torrent_name = new_torrent_name

    for month in (
        "январь",   "января",
        "февраль",  "февраля",
        "март",     "марта",
        "апрель",   "апреля",
        "май",      "мая",
        "июнь",     "июня",
        "июль",     "июля",
        "август",   "августа",
        "сентябрь", "сентября",
        "октябрь",  "октября",
        "ноябрь",   "ноября",
        "декабрь",  "декабря",
    ):
        torrent_name = re.sub(r"\b" + month + r"\b", "", torrent_name)
    # <--

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
            aggregated.count += obj.revision;
        }"""
    )

    for torrent in torrents:
        torrent["count"] = int(torrent["count"])

    torrents.sort(key = lambda a: a["count"], reverse = True)

    return torrents


def get_url(torrent_id):
    """Returns torrent URL."""

    return "http://rutracker.org/forum/viewtopic.php?t={id}".format(id = torrent_id)


def init():
    """Initializes torrents collection."""

    coll("torrents").ensure_index([( "time", pymongo.DESCENDING )])


def update(torrent_id, data, changed = False, upsert = False):
    """Updates the specified torrent."""

    update = { "$set": data }

    if changed:
        update["$inc"] = { "revision": 1 }

    return coll("torrents").update({ "_id": torrent_id }, update,
        upsert = upsert)["updatedExisting"]


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
