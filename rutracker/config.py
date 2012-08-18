"""Stores configuration values."""

from __future__ import unicode_literals

from pycl import constants

MAX_FEED_AGE = 5 * constants.DAY_SECONDS
"""Max age of torrents appeared in the RSS feed."""

MAX_TORRENTS_IN_FEED = 50
"""Maximum number of torrents in the feed."""

MAX_TORRENT_AGE = 3 * constants.MONTH_SECONDS
"""Maximum age of a torrent stored in the database."""
