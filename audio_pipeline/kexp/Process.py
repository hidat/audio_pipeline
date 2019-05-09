import uuid

from audio_pipeline import Constants
from audio_pipeline.util import Util, Resources
# from . import Resources
from ..util.MusicBrainz import ExtractMeta


class ReleaseProcessor(ExtractMeta.ReleaseProcessor):
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

        disc_index = audio_file.disc_num.value - 1  # zero-index the disc num
        track_index = audio_file.track_num.value - 1  # zero-index the track num

        release_meta = self.release

        if disc_index < release_meta.disc_count:
            disc = self.mb_release['medium-list'][disc_index]
        else:
            # the disc num in the file tags is not compatible with the number of discs
            # in the musicbrainz release we retrived, so it's probably the wrong release
            # and we are not able to properly extract the metadata
            return track

        if track_index < len(disc['track-list']):
            track_meta = disc['track-list'][track_index]
        else:
            # the track number in the file tags is not compatible with the number of tracks
            # in the musicbrainz release we retrived, so it's probably the wrong release
            # and we are not able to properly extract the metadata
            return track

 
        #####################################################
        # Set KEXP-specific metadata from audio file tags
        #####################################################

        track.primary_genre = Resources.Genres.get(str(audio_file.track_tags["KEXPPrimaryGenre"]))
        track.anchor_status = str(audio_file.track_tags["KEXPAnchorStatus"])
        track.obscenity = str(audio_file.track_tags["KEXPFCCOBSCENITYRATING"])
        track.radio_edit = str(audio_file.track_tags["KEXPRadioEdit"])

        # if generating unique item codes, do that
        if not Constants.is_tb:
            if Constants.batch_constants.gen_item_code:
                item_code = str(uuid.uuid4())
            elif audio_file.item_code.value is not None:
                item_code = audio_file.item_code.value
            elif (track.obscenity.casefold() == "kexp clean edit") or (track.radio_edit.casefold() == "kexp radio edit"):
                item_code = str(uuid.uuid4())
            else:
                item_code = track_meta['id']
    
            track.item_code = item_code
            
        track.set_type()
        
        # get the secondary category
        sort_names = []
        for artist in release_meta.artist_sort_names:
            sort_names.append(artist)

        if Constants.batch_constants.source == Resources.Hitters.source:
            track.secondary_category = Resources.Hitters.artist + Constants.batch_constants.rotation + " Hitters"
        elif Constants.batch_constants.rotation:
            cat = release_meta.artist
            cat += " - " + release_meta.title
            cat = self.secondary_category + "/" + Util.string_cleanup(Constants.batch_constants.rotation) + \
                  "/" + Util.string_cleanup(cat)
            track.secondary_category = cat

        sort_names.sort()
        track.artist_dist_rule = Util.distrule_cleanup(sort_names[0][:1])
        track.various_artist_dist_rule = Util.distrule_cleanup(release_meta.title[:1])

        # set the item_code value in the audio file
        if not Constants.is_tb:
            audio_file.item_code.value = item_code
            audio_file.item_code.save()

        return track
        
    def get_track(self, audio_file):
        track = self.process_track(audio_file)
        return track

        
class ArtistProcessor(ExtractMeta.ArtistProcessor):

    def __init__(self, mb_artist):
        super().__init__(mb_artist)
