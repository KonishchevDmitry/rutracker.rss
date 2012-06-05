#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Receives new torrents info from http://rutracker.org/ and stores them into the
database.
"""

import cookielib
import re
import sys
import time
import urllib2

import analysis
from db import coll

_DEVELOP_MODE = False
"""True if the script is running in develop mode."""




def get_new_torrents():
    """Gets new torrents info."""

    # A regular expression for attribute name
    attribute_name_regex = "[a-zA-Z][-.a-zA-Z0-9:_]*"

    # A regular expression for tag attributes
    tag_attrs_regex = re.sub(r"\s*", "", r"""
        (?:\s+
          """ + attribute_name_regex + r"""
          (?:\s*=\s*
            (?:
              '[^']*'
              |"[^"]*"
              |[^'"/>\s]+
            )
          )?
        )*
    """)

    # A regular expression for a link to torrent page on http://rutracker.org
    torrent_regex = re.compile(
        r"<a" + tag_attrs_regex + r"""
            \s+class=(?:
                "([^"]+)"|
                '([^']+)'
            )
        """ + tag_attrs_regex + r"""\s+href\s*=\s*["'][^'"]+/viewtopic\.php\?t=(\d+)["']""" +
        tag_attrs_regex + r">(.+?)</a>"
    , re.IGNORECASE | re.DOTALL | re.VERBOSE)

    # TODO:
    #jar = cookielib.FileCookieJar("cookies")
    #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(jar))
    #
    #login_post = "login_username=&login_password=&login=%C2%F5%EE%E4"
    #opener.open("http://login.rutracker.org/forum/login.php", login_post)
    #
    #search_post="prev_my=0&prev_new=0&prev_oop=0&f%5B%5D=46&f%5B%5D=2178&f%5B%5D=671&f%5B%5D=2177&f%5B%5D=251&f%5B%5D=97&f%5B%5D=851&f%5B%5D=821&f%5B%5D=2076&f%5B%5D=98&f%5B%5D=56&f%5B%5D=1469&f%5B%5D=2123&f%5B%5D=1280&f%5B%5D=876&f%5B%5D=752&f%5B%5D=1114&f%5B%5D=2380&f%5B%5D=1467&f%5B%5D=672&f%5B%5D=249&f%5B%5D=552&f%5B%5D=500&f%5B%5D=2112&f%5B%5D=1327&f%5B%5D=1468&o=1&s=2&tm=-1&pn=&nm=&submit=%CF%EE%E8%F1%EA"
    #torrents_page = opener.open("http://rutracker.org/forum/tracker.php", search_post).read()
    #
    #match = re.search(r'<a class="pg" href="tracker.php\?search_id=([^&]+)', torrents_page)
    #if match is None:
    #    fsdfsdf
    #search_id = match.group(1)

    for page in xrange(0, 9):
        if _DEVELOP_MODE:
            torrents_page = open(str(page + 2) + ".html").read().decode("cp1251")
    # TODO:
    #    time.sleep(1)
    #    torrents_page = opener.open("http://rutracker.org/forum/tracker.php?search_id=" + search_id + "&start=" + str(page * 50)).read().decode("cp1251")
    #    torrents_page = torrents_page.replace("\n", "")
    #    torrents_page = torrents_page.replace("\r", "")

        counter = 0
        for link_class, _, torrent_id, torrent_name in torrent_regex.findall(torrents_page):
            link_class = link_class.split(" ")
            if "med" not in link_class or "tLink" not in link_class:
                continue
            torrent_id = int(torrent_id)
            print (analysis.get_torrent_fingerprint(torrent_name) + "|" + torrent_name).encode("utf-8")
            counter += 1

        print ""
        print ""
        print ""

        if counter != 50:
            print torrents_page.encode("utf-8")
            print counter
            fsf


def main():
    """The script's main function."""

    global _DEVELOP_MODE
    _DEVELOP_MODE = "--develop-mode" in sys.argv[1:]

    get_new_torrents()



if __name__ == "__main__":
    main()
    # TODO
    #print get_torrent_name(u"Прокурорская<wbr> проверка (Андрей Морозов, Константин Смирнов, Владимир Морозов)(эфи<wbr>ры от 2012.03.16 по 2012.04.02 [2012, ТелеДетектив<wbr>, SATRip]")
