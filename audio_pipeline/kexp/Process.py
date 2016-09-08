import uuid

from audio_pipeline import Constants
from audio_pipeline.util import Util, Resources
# from . import Resources
from ..util import Process


class ReleaseProcessor(Process.ReleaseProcessor):
    secondary_category = "CATEGORIES/ROTATION-STAGING"

    def process_release(self):
        """
        Extract release metadata we care about from the raw metadata
        """
        if not self._release:
            super().process_release()
            release = self._release

            meta = self.mb_release

            if Constants.batch_constants.category:
                primary_genre = Resources.Genres.get(Constants.batch_constants.category)
                if primary_genre in Resources.Genres.set_secondary:
                    release.secondary_genre = Resources.Genres.set_secondary[primary_genre]

            dist_cat = []
            for artist in meta['artist-credit']:
                if 'artist' in artist:
                    a = artist['artist']
                    dist_cat.append(a['sort-name'])
                    if 'disambiguation' in a:
                        dist_cat.append('(' + a['disambiguation'] + ')')
                else:
                    dist_cat.append(artist)

            dist_cat = Util.string_cleanup(" ".join(dist_cat))
            release.distribution_category = dist_cat

            glossary_title = release.title + " " + release.artist + " " + \
                release.date + " " + release.country + " " + " ".join([l.title for l in release.labels]) \
                             + " " + " ".join(release.format) + " " + " ".join([l.catalog_num for l in release.labels])

            release.glossary_title = Util.string_cleanup(glossary_title)

            self._release = release

    @property
    def release(self):
        if self._release:
            release = self._release
        else:
            self.process_release()
            release = self._release

        return release

    def process_track(self, audio_file):
        """
        Extract the track metadata we care about from the release metadata & AudioFile metadata.
        """

        track = super().process_track(audio_file)
        
        return track
        
    def get_track(self, audio_file):
        track = self.process_track(audio_file)
        return track

        
class ArtistProcessor:

    def __init__(self, mb_artist):
        self.mb_artist = mb_artist
        self._artist = None

    def process_artist(self):
        # make sure we haven't already processed this artist:
        if self._artist:
            artist = self._artist
        else:
            # get MusicBrainz metadata
            meta = self.mb_artist
            
            # extract relevent metadata into an Artist object
            # (at this point, the artist item code is always the artist mbid)
            artist = Resources.Artist(meta['id'])
            
            artist.name = meta['name']
            
            if 'disambiguation' in meta:
                artist.disambiguation = meta['disambiguation']
                artist.title = artist.name + ' (' + artist.disambiguation + ') '
            else:
                artist.title = artist.name
                
            artist.id = meta['id']
            artist.sort_name = meta['sort-name']
            
            if 'annotation' in meta and 'annotation' in meta['annotation']:
                artist.annotation = meta['anotation']['text']
            if 'type' in meta:
                artist.type = meta['type']
            
            if 'begin-area' in meta:
                artist.begin_area.name = meta['begin-area']['name']
                artist.begin_area.id = meta['begin-area']['id']
            if 'end-area' in meta:
                artist.end_area.name = meta['end-area']['name']
                artist.end_area.id = meta['end-area']['id']
                
            if 'life-span' in meta:
                life = meta['life-span']
                if 'begin' in life:
                    artist.begin_date = life['begin']
                if 'end' in life:
                    artist.end_date = life['end']
                if 'ended' in life:
                    if life['ended'].lower() == 'true':
                        artist.ended = '1'
                    else:
                        artist.ended = '0'
            
            if 'country' in meta:
                # check that country is there, but mb's 'country' field is a code (such as 'GB')
                # so the actual information we want is stored in 'area'
                if 'area' in meta:
                    artist.country.name = meta['area']['name']
                    artist.country.id = meta['area']['id']
            
            if 'ipi-list' in meta:
                artist.ipi_list = meta['ipi-list']
                
            if 'isni-list' in meta:
                artist.isni_list = meta['isni-list']
                
            if 'url-relation-list' in meta:
                for link in meta['url-relation-list']:
                    if 'target' in link:
                        artist.url_relation_list.append(link['target'])

            if 'artist-relation-list' in meta:
                for member in meta['artist-relation-list']:
                    if member['type'] == 'member of band' and 'direction' in member \
                            and member['direction'] == 'backward':
                        artist.group_members.append(member['artist']['id'])
                        
        self._artist = artist

    @property
    def artist(self):
        if self._artist:
            # already have info about this artist; don't need to do anything
            artist = self._artist
        else:
            # process this artist
            self.process_artist()
            artist = self._artist
            
        return artist