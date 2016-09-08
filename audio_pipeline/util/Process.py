import uuid

from audio_pipeline import Constants
from audio_pipeline.util import Exceptions
from audio_pipeline.util import Util, Resources


class Processor:

    release_groups = dict()
    releases = dict()
    artists = dict()
    mbinfo = None
    processor = None

    def __init__(self, *args):
        Processor.mbinfo = Constants.batch_constants.mb
        Processor.processor = Constants.processor

    @classmethod
    def get_releases(cls, mbid):
        if cls.mbinfo is None:
            raise Exceptions.NoMusicBrainzError("No MBInfo object when processing release group " + str(mbid))

        if mbid in cls.release_groups:
            results = [cls.releases[release_id] for release_id in cls.release_groups[mbid]]
            return results
        else:
            mb_releases = cls.mbinfo.get_group_releases(mbid)
            cls.release_groups[mbid] = list()
            results = list()
            if not mb_releases:
                raise Exceptions.NoMusicBrainzError("Problem getting release info from musicbrainz for id " + str(mbid))

            for mb_release in mb_releases:
                release = cls.processor.ReleaseProcessor(mb_release)
                release_id = release.release.id
                cls.release_groups[mbid].append(release_id)
                results.append(release)
                cls.releases[release_id] = release
            return results

    @classmethod
    def get_release(cls, mbid):
        if cls.mbinfo is None:
            raise Exceptions.NoMusicBrainzError("No MBInfo object when processing release " + str(mbid))

        if mbid in cls.releases:
            return cls.releases[mbid]
        else:
            mb_release = cls.mbinfo.get_release(mbid)
            if not mb_release:
                raise Exceptions.NoMusicBrainzError("Problem getting release info from musicbrainz for id " + str(mbid))

            release = cls.processor.ReleaseProcessor(mb_release)
            cls.releases[mbid] = release
            return release

    @classmethod
    def get_artist(cls, mbid):
        if cls.mbinfo is None:
            raise Exceptions.NoMusicBrainzError("No MBInfo object when processing artist " + str(mbid))

        if mbid in cls.artists:
            return cls.artists[mbid]
        else:
            mb_artist = cls.mbinfo.get_artist(mbid)
            if not mb_artist:
                raise Exceptions.NoMusicBrainzError("Problem getting artist info from musicbrainz for id " + str(mbid))

            artist = cls.processor.ArtistProcessor(mb_artist)
            cls.artists[mbid] = artist
            return artist


class ReleaseProcessor:
    secondary_category = "CATEGORIES/ROTATION-STAGING"

    def __init__(self, mb_release):
        self.mb_release = mb_release
        self._release = None

    def process_release(self):
        """
        Extract release metadata we care about from the raw metadata
        """
        if not self._release:
            meta = self.mb_release
            
            release = Resources.Release(item_code = meta['id'])
        
            rg = meta['release-group']
            
            release.id = meta['id']
            release.disc_count = len(meta['medium-list'])
            release.title = meta['title']
            release.release_group_id = rg['id']
            release.first_released = rg['first-release-date']

            if 'primary-type' in rg:
                release.release_type = rg['primary-type']
            
            if 'tag-list' in rg:
                release.tags = rg['tag-list']
                
            formats = ''
            for disc in meta['medium-list']:
                release.media.append(Resources.Disc(disc['position'], len(disc['track-list'])))
                if 'format' in disc:
                    release.format.append(disc['format'])
                    formats = formats + " " + disc['format']

            release.artist_credit = meta['artist-credit']
            
            if 'disambiguation' in meta:
                release.disambiguation = meta['disambiguation']
                
            if 'label-info-list' in meta:
                for l in meta['label-info-list']:
                    if 'label' in l:
                        label = Resources.Label(l['label']['id'], l['label']['id'], l['label']['name'])
                        if 'catalog-number' in l:
                            label.catalog_num = l['catalog-number']
                        release.labels.append(label)

            if 'date' in meta:
                release.date = meta['date']
            if 'country' in meta:
                release.country = meta['country']
            if 'barcode' in meta:
                release.barcode = meta['barcode']
            if 'asin' in meta:
                release.asin = meta['asin']
            if 'packaging' in meta:
                release.packaging = meta['packaging']
                
            full_name = ''
            for artist in meta['artist-credit']:
                if 'artist' in artist:
                    a = artist['artist']
                    full_name = full_name + a['name']
                    release.artist_ids.append(a['id'])
                    release.artist_sort_names.append(a['sort-name'])
                else:
                    full_name = full_name + artist

            release.artist = full_name 

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
        
        disc_index = audio_file.disc_num.value - 1    # zero-index the disc num
        track_index = audio_file.track_num.value - 1  # zero-index the track num

        # create the track object
        track = Resources.Track()
        
        release_meta = self.release
        
        if disc_index < release_meta.disc_count:
            disc = self.mb_release['medium-list'][disc_index]
        else:
            return track
            
        if track_index < len(disc['track-list']):
            track_meta = disc['track-list'][track_index]
        else:
            return track
            
        # if generating unique item codes, do that
        if Constants.batch_constants.gen_item_code:
            item_code = str(uuid.uuid4())
        elif audio_file.item_code.value is not None:
            item_code = audio_file.item_code.value
        elif (audio_file.obscenity.value is not None and \
             audio_file.obscenity.value.casefold() == "kexp clean edit") or \
             (audio_file.radio_edit.value is not None and \
             audio_file.radio_edit.value.casefold() == "kexp radio edit"):
            item_code = str(uuid.uuid4())
        else:
            item_code = track_meta['id']
        
        track.item_code = item_code
                        
        recording_meta = track_meta['recording']
        
        # fields from track_meta
        track.id = track_meta['id']
        
        track.set_type()

        if "artist-credit-phrase" in track_meta:
            track.artist_phrase = track_meta["artist-credit-phrase"]

        for artist in track_meta['artist-credit']:
            if 'artist' in artist:
                track.artist_credit = track.artist_credit + artist['artist']['name']
                track.artists.append(artist['artist']['id'])
            else:
                track.artist_credit = track.artist_credit + artist

        # get the track title
        if 'title' in track_meta:
            track.title = track_meta['title']
        else:
            track.title = recording_meta['title']
        
        # fields from the recording
        track.recording_id = recording_meta['id']
        if 'length' in recording_meta:
            track.length = recording_meta['length']
        if 'isrc-list' in recording_meta:
            track.isrc_list = recording_meta['isrc-list']

        # fields from release_meta
        track.release_id = release_meta.id
        
        track.track_count = len(self.mb_release["medium-list"][disc_index]["track-list"])
        
        # fields straight from the AudioFile
        track.disc_num = audio_file.disc_num.value
        track.track_num = audio_file.track_num.value
        track.obscenity = str(audio_file.obscenity)
        track.primary_genre = Resources.Genres.get(str(audio_file.category))
        track.anchor_status = str(audio_file.anchor)

        #####################################
        # NEED TO ADD RADIO EDIT INFORMATION
        #####################################
        
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
        audio_file.item_code.value = item_code

        audio_file.item_code.save()
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

            if 'artist-relation-list' in meta and artist.type == 'Group':
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