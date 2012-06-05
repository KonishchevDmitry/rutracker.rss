#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib2
import cookielib
import time

#MAX_URLS = 10
#
#with open("viewed_ids", "r") as f:
#    viewed_ids = [ int(id.strip()) for id in f.read().split("\n") if id.strip() ]

import HTMLParser
html_parser = HTMLParser.HTMLParser()


import pymongo

def coll(name):
    """Returns the specified MongoDB collection."""

    return db()[name]


def db():
    """Returns the MongoDB database."""

    connection = pymongo.Connection()
    return connection["rutracker"]


#def replace(regex, replace, string):
#    match = re.match(regex, string)
#    return string if match is None else match.group(1)
#
#def replace_all(regex, string):
#    new_string = None
#
#    while new_string != string:
#        string = string if new_string is None else new_string
#        new_string = replace(regex, string)
#
#    return new_string

def get_torrent_name(torrent_name):
    torrent_name = html_parser.unescape(torrent_name)

    characters = u"abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщьъыэюя"
    upper_characters = u"ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЫЭЮЯ"

    pos = torrent_name.find(" - ")
    if pos != -1 and torrent_name[pos + len(" - ")] in upper_characters:
        torrent_name = torrent_name[:pos]

    torrent_name = torrent_name.lower()

    old_torrent_name = None
    while torrent_name != old_torrent_name:
        old_torrent_name = torrent_name

        for regex, repl in (
            ( r"^(.+)\s+\[[^\[\]]+\](.*)", r"\1\2"),
            ( r"^(.+)\s+\([^()]+\)(.*)", r"\1\2"),
            ( r"^(.+)\s+\d{1,2}\.\d{1,2}\.\d{4}(.*)", r"\1\2"),
        ):
            torrent_name = re.sub(regex, repl, torrent_name.strip(" ."))

    torrent_name = torrent_name.replace(u"г.", "")
    torrent_name = torrent_name.replace(u"эфир от", "")
    torrent_name = torrent_name.replace(u"обновлено", "")

    torrent_name = re.sub(r"\s+/.*", "", torrent_name)
    torrent_name = re.sub(r"</?[a-z]+>", "", torrent_name)

    torrent_name = "".join(
        c for c in torrent_name if c in u" " + characters)

    torrent_name = re.sub(r"\s+", " ", torrent_name).strip()

    #torrent_name = torrent_name.replace('"', "")
    #torrent_name = torrent_name.replace("-", "")
    #torrent_name = torrent_name.replace(".", "")
    #torrent_name = torrent_name.replace(",", "")
    #torrent_name = torrent_name.replace("?", "")
    #torrent_name = torrent_name.replace("!", "")
    #torrent_name = torrent_name.replace(u"«", "")
    #torrent_name = torrent_name.replace(u"»", "")

    return torrent_name

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
    torrents_page = open(str(page + 2) + ".html").read().decode("cp1251")
#    time.sleep(1)
#    torrents_page = opener.open("http://rutracker.org/forum/tracker.php?search_id=" + search_id + "&start=" + str(page * 50)).read().decode("cp1251")
#    torrents_page = torrents_page.replace("\n", "")
#    torrents_page = torrents_page.replace("\r", "")

    counter = 0
    for torrent_id, torrent_name in re.findall(r'<a class="med tLink[^"]*" href="./viewtopic.php\?t=(\d+)">(.+?)</a>', torrents_page, re.IGNORECASE | re.DOTALL):
        torrent_id = int(torrent_id)
        print (get_torrent_name(torrent_name) + "|" + torrent_name).encode("utf-8")
        counter += 1

    print ""
    print ""
    print ""

    if counter != 50:
        print counter, torrents_page.encode("utf-8")
        fsf

