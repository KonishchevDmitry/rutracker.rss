# -*- coding: utf-8 -*-

"""Various analysis tools."""

import HTMLParser
import re

html_parser = HTMLParser.HTMLParser()


def get_torrent_fingerprint(torrent_name):
    """
    Tries to obtain a fingerprint from the torrent name that will uniquely
    identify it's group (TV show).
    """

    # Unescape HTML entities
    torrent_name = html_parser.unescape(torrent_name)

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
