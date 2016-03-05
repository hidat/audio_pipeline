import audio_pipeline.util.MBInfo as MBInfo
import audio_pipeline.file_walker.Resources as Resources
import audio_pipeline.file_walker.Util as Util

class Process(object):
    releases = {}   # dictionary of release mbid -> instantiated process objects
    artists = {}    # dictionary of artist mbid -> instantiated artist objects (Artist is defined in Resources.py file)
    mb = None       # MBInfo object shared between Process objects
    secondary_category = "CATEGORIES/ROTATION-STAGING"

    def __init__(self, mbid, mbinfo=None):
        if not self.mb:
            if mbinfo:
                self.mb = mbinfo
            else:
                # how do you make initialization return a None??
                self = None
        elif mbinfo:
            self.mb = mbinfo
                
        if mbid in releases:
            self = releases[mbid]
        else:
            releases[mbid] = self
            
            self.mb_release = self.mb.get_release(mbid)
            if not self.mb_release:
                # error getting musicbrainz data for this release - remove mbid from cache
                releases.pop(mbid)
                self = None
            else:
                self.release = None

    def process_release(self):
        """
        Extract release metadata we care about from the raw metadata
        """
        if not self.release:
            meta = self.mb_release
            
            release = Resources.Release(item_code = meta[id])
        
            rg = meta['release-group']
            
            release.id = meta['id']
            release.disc_count = len(meta['medium-list'])
            release.title = meta['title']
            release.release_group_id = rg['id']
            release.first_release_date = rg['first-release-date']
            
            if 'tag-list' in rg:
                release.tags = rg['tag-list']
                
            formats = ''
            for disc in meta['medium-list']:
                if 'format' in disc:
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
            
            if 'first-release-date' in meta:
                release.first_released = meta['first-release-date']
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
                    release.artist_sort_names.append(a['sort_name'])
                    
                    dist_cat = dist_cat + a['sort_name']
                    if 'disambiguation' in a:
                        dist_cat = dist_cat + ' (' + a['disambiguation'] + ') '
                else:
                    full_name = full_name + artist
                    dist_cat = dist_cat + artist
                    
            release.artist = full_name 
            dist_cat = Util.stringCleanup(dist_cat)
            release.distribution_category = dist_cat
            
            glossary_title = release.title + " " + release.artist + " " +
                release.date + " " + release.country + labels + formats + cat_nums
            
            release.glossary_title = Util.stringCleanup(glossary_title)
            
            self.release = release
        
        
    def get_release(self):
        """
        Get release metadata, processed for serialization.
        """
        if self.release:
            release = self.release
        else:
            self.process_release()
            release = self.release
            
        return release
        

    def process_track(self, audio_file):
        """
        Extract the track metadata we care about from the release metadata & AudioFile metadata.
        """
        
        disc_index = audio_file.disc_num - 1    # zero-index the disc num
        track_index = audio_file.track_num - 1  # zero-index the track num
        
        if not self.release:
            self.process_release()
            
        release_meta = self.release
        track_meta = release_meta['medium-list'][disc_index]['track-list'][track-index]
        recording_meta = track_meta['recording']
        
        
        # get the track item_code
        if audio_file.kexp.obscenity.upper() == 'RADIO EDIT':
            item_code = str(UUID.uuid4())
        else:
            item_code = track_meta['id']
            
        # create the track object
        track = Resources.Track(item_code)
        
        # fields from track_meta
        track.id = track_meta['id']
        track.title = track_meta['title']
        
        for artist in track_meta['artist-credit']:
            if 'artist' in artist:
                track.artist_credit = track.artist_credit + artist['artist']['name']
                track.artists.append(artist['artist']['id'])
            else:
                track.artist_credit = track.artist_credit + artist

        # fields from the recording
        track.recording_id = recording_meta['id']
        if 'length' in recording_meta:
            track.length = recording_meta['length']
        if 'isrc-list' in recording_meta:
            track.isrc_list = recording_meta['isrc-list']

        # fields from release_meta
        track.release_id = release_meta.release_id
        
        # fields straight from the AudioFile
        track.disc_num = audio_file.disc_num
        track.track_num = audio_file.track_num
        track.obscenity = audio_file.kexp.obscenity
        track.primary_genre = audio_file.kexp.primary_genre
        
        # get the secondary category
        cat = None
        sort_names = []
        if Resources.BatchConstants.rotation:
            cat = ""
            
        for artist in release_meta.artist_sort_names:
            sort_name.append(artist)
                
        if Resources.BatchConstants.rotation:
            cat = release_meta.artist
            cat += " - " + release_meta.title
            cat = secondary_category + "/" + stringCleanup(Resources.BatchConstants.rotation) + "/" + stringCleanup(cat)
            track.secondary_category = cat
            
        sort_name.sort()
        track.artist_dist_rule = Util.distRuleCleanup(sort[0][:1])
        track.various_artist_dist_rule = Util.distRuleCleanup(release_meta.title[:1])
        
        return track
        
    def get_track(self, audio_file):
        track = self.process_track(audio_file)
        return track

        
    @classmethod
    def process_artist(cls, mbid):
        # make sure we haven't already processed this artist:
        if mbid in cls.artists.keys():
            artist = cls.artists[mbid]
        else:
            # get MusicBrainz metadata
            meta = cls.mb.get_artist(mbid)
            
            # extract relevent metadata into an Artist object
            # (at this point, the artist item code is always the artist mbid)
            artist = Resources.Artist(mbid)
            
            artist.name = artist['name']
            
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
        
    @classmethod
    def get_artist(cls, mbid):
        if mbid in cls.artists.keys():
            # already have info about this artist; don't need to do anything
            artist = cls.artists[mbid]
        else:
            # process this artist
            artist = cls.process_artist(mbid)
            return artist