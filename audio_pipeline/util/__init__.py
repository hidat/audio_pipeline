from . import Exceptions
from . import MBInfo
from . import Tag
from . import Util
from . import format
from . import Discogs
import re


# unknown artist input pattern:
class Utilities:
    unknown_artist_pattern = re.compile(r'unknown artist|^\s*$', flags=re.I)

    @classmethod
    def know_artist_name(cls, artist):
        """
        Returns false if 'artist' is "unknown artist" or empty
        :param artist:
        :return:
        """
        unknown_artist = not (artist or artist.isspace() or cls.unknown_artist_pattern.search(artist))
        return unknown_artist
