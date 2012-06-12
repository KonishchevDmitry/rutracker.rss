"""Provides functions for managing torrent blacklist."""

import pymongo.errors

from pycl.core import Error

from rutracker.db import coll


def add(rule):
    """Adds the specified rule."""

    try:
        coll("blacklist").insert({ "_id": rule }, safe = True)
    except pymongo.errors.DuplicateKeyError:
        raise Error("Rule '{rule}' already exists.", rule = _format_rule(rule))


def find():
    """Returns all blacklist rules."""

    return coll("blacklist").find()


def remove(rule):
    """Removes the specified rule."""

    if not coll("blacklist").remove({ "_id": rule }, safe = True)["n"]:
        raise Error("Rule '{rule}' doesn't exist in the blacklist.".format(
            rule = _format_rule(rule)))


def _format_rule(rule):
    """Formats a rule for output."""

    return rule.replace("\\", "\\\\").replace("'", "\\'")
