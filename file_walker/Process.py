import audio_pipeline.util.MBInfo as MBInfo
import audio_pipeline.file_walker.Resources as Resources
import audio_pipeline.file_walker.Util as Util

class Process(object):
    releases = {}
    artists = {}
    mb = None
    
    def __init__(self, mbid, mbinfo=None):
        if not self.mb:
            if mbinfo:
                self.mb = mbinfo
            else:
                # how do you make initialization return a None??
                self = None
                
        if mbid in releases:
            self = releases[mbid]
        else:
            releases[mbid] = self
            
            self.mb_release = mb.get_release(mbid)
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
            
            release = Resources.Release(item_code = meta[)
        
            rg = meta['release-group']
            
            release.release_id = meta['id']
            release.disc_count = len(meta['medium-list'])
            release.title = meta['title']
            release.release_group_id = rg['id']
            release.first_release_date = rg['first-release-date']
            
            if 'tag-list' in rg:
                release.tags = rg['tag-list']
                
            for disc in meta['medium-list']:
                if 'format' in disc:
                    release.format.append(disc['format'])
                    
            release.artist_credit = meta['artist-credit']
            
            if 'disambiguation' in meta:
                release.disambiguation = meta['disambiguation']
                
            if 'label-info-list' in meta:
                release.labels = meta['label-info-list']
                
            if 'date' in meta:
                release.date = meta['date']
                
            if 'country' in meta:
                release.country = meta['country']
                
            if 'barcode' in meta:
                release.barcode = meta['barcode']
                
            if 'asin' in meta:
                release.asin = meta['asin']
                
            if 'packagin' in meta:
                release.packaging = meta['packaging']
                
            dist_cat = ''
            for artist in release.artist_credit:
                if 'artist' in artist:
                    dist_cat = dist_cat + artist['artist']['sort_name']
                    if 'disambiguation' in artist['artist']
                        dist_cat = dist_cat + ' (' + artist['artist']['disambiguation'] + ') '
                else:
                    dist_cat = dist_cat + artist
                    
            dist_cat = Util.stringCleanup(dist_cat)
            release.distribution_category = dist_cat
            
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
        track.track_id = track_meta['id']
        track.title = track_meta['title']
        track.artist_credit = track_meta['artist-credit']

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
            
        for artist in release_meta.artist_credit:
            if 'artist' in artist:
                sort_name.append(artist['artist']['sort-name'])
                if cat:
                    cat += artist['artist']['name']
            elif cat:
                cat += artist
                
        if cat:
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
        
    
        