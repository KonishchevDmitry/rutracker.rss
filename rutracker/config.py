"""Stores configuration values."""

from pcore.constants import DAY_SECONDS, MONTH_SECONDS

MAX_FEED_AGE = 5 * DAY_SECONDS
"""Max age of torrents appeared in the RSS feed."""

MAX_TORRENTS_IN_FEED = 50
"""Maximum number of torrents in the feed."""

MAX_TORRENT_AGE = 3 * MONTH_SECONDS
"""Maximum age of a torrent stored in the database."""
