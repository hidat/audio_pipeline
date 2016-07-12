import uuid

from audio_pipeline.util import Resources
from audio_pipeline.util import Util
from ..util import Process


class ReleaseProcessor(Process.ReleaseProcessor):
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
            
            if 'tag-list' in rg:
                release.tags = rg['tag-list']
                
            formats = ''
            for disc in meta['medium-list']:
                if 'format' in disc and formats == '':
                    release.format.append(disc['format'])
                    formats = formats + " " + disc['format']
                    
            release.artist_credit = meta['artist-credit']
            
            if 'disambiguation' in meta:
                release.disambiguation = meta['disambiguation']
                
            labels = ''
            cat_nums = ''
            if 'label-info-list' in meta:
                for l in meta['label-info-list']:
                    if 'label' in l:
                        label = Resources.Label()
                        label.name = l['label']['name']
                        label.id = l['label']['id']
                        labels = labels + " " + label.name
                        if 'catalog-number' in l:
                            label.catalog_num = l['catalog-number']
                            cat_nums = cat_nums + " " + label.catalog_num
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
                
            dist_cat = ''
            full_name = ''
            for artist in meta['artist-credit']:
                if 'artist' in artist:
                    a = artist['artist']
                    full_name = full_name + a['name']
                    release.artist_ids.append(a['id'])
                    release.artist_sort_names.append(a['sort-name'])
                    
                    dist_cat = dist_cat + a['sort-name']
                    if 'disambiguation' in a:
                        dist_cat = dist_cat + ' (' + a['disambiguation'] + ') '
                else:
                    full_name = full_name + artist
                    dist_cat = dist_cat + artist
                    
            release.artist = full_name 
            dist_cat = Util.stringCleanup(dist_cat)
            release.distribution_category = dist_cat
            
            glossary_title = release.title + " " + release.artist + " " + \
                release.date + " " + release.country + labels + formats + cat_nums
            
            release.glossary_title = Util.stringCleanup(glossary_title)
            
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
        
        if not self._release:
            self.process_release()
            
        release_meta = self._release
        track_meta = self.mb_release['medium-list'][disc_index]['track-list'][track_index]
        recording_meta = track_meta['recording']

        # if generating unique item codes, do that
        if Resources.BatchConstants.gen_item_code or \
            (audio_file.obscenity.value is not None and \
             audio_file.obscenity.value.casefold() == "kexp clean edit"):
            item_code = str(uuid.uuid4())
            track_type = "track with filewalker itemcode"
        else:
            item_code = track_meta['id']
            track_type = "track"
                        
        # create the track object
        track = Resources.Track(item_code)
        track.type = track_type
        
        # fields from track_meta
        track.id = track_meta['id']
        
        for artist in track_meta['artist-credit']:
            if 'artist' in artist:
                track.artist_credit = track.artist_credit + artist['artist']['name']
                track.artists.append(artist['artist']['id'])
            else:
                track.artist_credit = track.artist_credit + artist

        # fields from the recording
        track.title = recording_meta['title']
        
        track.recording_id = recording_meta['id']
        if 'length' in recording_meta:
            track.length = recording_meta['length']
        if 'isrc-list' in recording_meta:
            track.isrc_list = recording_meta['isrc-list']

        # fields straight from the AudioFile
        track.disc_num = audio_file.disc_num.value
        track.track_num = audio_file.track_num.value
        track.obscenity = str(audio_file.obscenity)
        track.primary_genre = str(audio_file.category)
        track.anchor_status = str(audio_file.anchor)

        # fields from release_meta
        track.release_id = release_meta.id
        
        track.track_count = len(self.mb_release["medium-list"][disc_index]["track-list"])

        #####################################
        # NEED TO ADD RADIO EDIT INFORMATION
        #####################################
        
        # get the secondary category
        sort_names = []
        for artist in release_meta.artist_sort_names:
           sort_names.append(artist)
       
        if Resources.BatchConstants.source == Resources.Hitters.source:
            track.secondary_category = Resources.Hitters.artist + Resources.BatchConstants.rotation + " Hitters"
        elif Resources.BatchConstants.rotation:
            cat = release_meta.artist
            cat += " - " + release_meta.title
            cat = self.secondary_category + "/" + Util.stringCleanup(Resources.BatchConstants.rotation) + \
                    "/" + Util.stringCleanup(cat)
            track.secondary_category = cat
            
        sort_names.sort()
        track.artist_dist_rule = Util.distRuleCleanup(sort_names[0][:1])
        track.various_artist_dist_rule = Util.distRuleCleanup(release_meta.title[:1])
        
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