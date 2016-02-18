__author = 'cephalopodblue'
import unicodedata
import musicbrainzngs as ngs
import uuid as UUID


secondary_category = "CATEGORIES/ROTATION-STAGING"

class Release():

    def __init__(self, item_code):
        """
        Holds release metadata
        """
        
        self.item_code = ""
        
        self.release_id = ""
        self.disc_count = None
        self.title = ""
        self.release_group_id = ""
        self.first_release_date = ""
        self.tags = []
        self.format = []
        self.artist_credit = {}
        self.disambiguation = ""
        self.labels = []
        self.date = ""
        self.country = ""
        self.barcode = ""
        self.asin = ""
        self.packaging = ""
        self.distribution_category = ""
        
class Track():
    
    def __init__(self, item_code):
        """
        Holds track metadata
        """
        
        self.release_id = ""
        self.disc_count = None
        self.artist_credit = []
        self.release_track_id = ""
        self.recording_id = ""
        self.track_id = ""
        self.title = ""
        self.length = Noneself.isrcs = []
        self.secondary_category = ""
        self.artist_dist_rule =""
        self.various_artist_dist_rule = ""
        self.item_code = ""


class ProcessMeta():

    def __init__(self, mb_release, batch_meta):
        """
        Set up a ProcessMeta object - Store raw MusicBrainz metadata & common data
        """
        self.batch_meta = batch_meta
        self.mb_release = mb_release
        self.processed_release = None
        
    def process_release(self):
        """
        Extract the release metadata that we care about from the raw metadata
        """
        if not self.processed_release:
            # get the item code
            release_info = {}
                        
            rg = self.mb_release['release-group']

            release = Release(self.mb_release['id'])
            release.release_id = self.mb_release['id']
            release.disc_count = len(self.mb_release['medium-list'])
            release.title = self.mb_release['title']
            release.release_group_id = rg['id']
            release.first_release_date = rg['first-release-date']
            
            if 'tag-list' in rg:
                release['tags'] = rg['tag-list']
                
            for disc in self.mb_release['medium-list']:
                if 'format' in disc:
                    release.format.append(disc['format'])
                    
            release.artist_credit = self.mb_release['artist-credit']
            
            if ('disambiguation' in self.mb_release):
                release_info['disambiguation'] = self.mb_release['disambiguation']
                
            if 'label-info-list' in self.mb_release:
                release.labels = self.mb_release['label-info-list']
                
            if 'date' in self.mb_release:
                release.date = self.mb_release['date']
                
            if 'country' in self.mb_release:
                release.country = self.mb_release['coutry']
                
            if 'barcode' in self.mb_release:
                release.barcode = self.mb_release['barcode']
                
            if 'asin' in self.mb_release:
                release.asin = self.mb_release['asin']
                
            if 'packaging' in self.mb_release:
                release.packaging = self.mb_release['packaging']
                
            dist_cat = ''
            for artist in self.mb_release["artist-credit"]:
                if 'artist' in artist:
                    dist_cat = dist_cat + artist['artist']['sort-name']
                    if 'disambiguation' in artist['artist']:
                        dist_cat = dist_cat + ' (' + artist['artist']['disambiguation'] + ') '
                else:
                    dist_cat = dist_cat + artist
                
            dist_cat = stringCleanup(dist_cat)
            release.distribution_category = dist_cat

            release_info["item_code"] = self.mb_release['id']
            release_info["release_id"] = self.mb_release['id']
            release_info["disc_count"] = len(self.mb_release["medium-list"])
            release_info["release_title"] = self.mb_release['title']
            release_info["release_group_id"] = rg['id']
            release_info["first_release_date"] = rg['first-release-date']
            
            if 'tag-list' in rg:
                release_info['tags'] = rg['tag-list']
            else:
                release_info['tags'] = []
            
            release_info['format'] = set([])
            for disc in self.mb_release["medium-list"]:
                if 'format' in disc:
                    release_info['format'].add(disc['format'])
                            
            release_info["artist-credit"] = self.mb_release['artist-credit']
            if ("disambiguation" in self.mb_release):
                release_info["disambiguation"] = self.mb_release['disambiguation']
            else:
                release_info["disambiguation"] = ''
            if ("label-info-list" in self.mb_release):
                release_info["labels"] = self.mb_release["label-info-list"]
            if ("date" in self.mb_release):
                release_info["date"] = self.mb_release['date']
            else:
                release_info["date"] = ""
            if ("country" in self.mb_release):
                release_info["country"] = self.mb_release['country']
            else:
                release_info["country"] = ""
            if ("barcode" in self.mb_release):
                release_info["barcode"] = self.mb_release['barcode']
            else:
                release_info["barcode"] = ""
            if ("asin" in self.mb_release):
                release_info["asin"] = self.mb_release['asin']
            else:
                release_info["asin"] = ""
            if ("packaging" in self.mb_release):
                release_info["packaging"] = self.mb_release['packaging']
            else:
                release_info["packaging"] = ""
            
            release_info['distribution_category'] = dist_cat
            
            # Log text will be removed from release and processed in a separate object
            log_text = "release\t" + release_info['item_code'] + "\t" + release_info["release_title"] + "\r\n"
            release_info["log_text"] = log_text

            self.processed_release = release_info

    def get_release(self):
        """
        Get the metadata of the release stored in this ProcessMeta object
        """
        if self.processed_release:
            meta = self.processed_release
        else:
            self.process_release()
            meta = self.processed_release
            
        return meta
        
    def process_track(self, disc_num, track_num):
        """
        Extract the track metadata that we care about from the raw metadata
        """
        
        disc_index = disc_num - 1
        track_index = track_num - 1
        
        track = self.mb_release["medium-list"][disc_index]["track-list"][track_index]
        track_info = {}
        
        track_info["release_id"] = self.mb_release['id']
        track_info["disc_count"] = len(self.mb_release["medium-list"])
        track_info["artist_credit"] = self.mb_release["artist-credit"]
        track_info["release_track_id"] = track["id"]
        track_info["track_id"] = track["recording"]["id"]    
        track_info["track_count"] = len(self.mb_release["medium-list"][disc_index]["track-list"])
        track_info["title"] = track["recording"]["title"]
        if "length" in track["recording"]:
            track_info["length"] = track["recording"]["length"]
        if ("isrc-list" in track["recording"]):
            track_info["isrcs"] = track["recording"]["isrc-list"]
        track_info["artist-credit"] = track["artist-credit"]

        cat = None
        if "rotation" in self.batch_meta:
            cat = ""
        
        for artist in self.mb_release['artist-credit']:
            if 'artist' in artist:
                track_info['sort_name'] = artist['artist']['sort-name']
                if cat is not None:
                    cat += artist['artist']['name']
            elif cat is not None:
                cat += artist

        if cat:
            cat += " - " + self.mb_release['title']
            
            cat = stringCleanup(cat)
            
            cat = secondary_category + "/" + stringCleanup(self.batch_meta["rotation"]) + "/" + cat
            track_info["secondary_category"] = cat
        
        track_info["artist_dist_rule"] = distRuleCleanup(track_info['sort_name'][:1])
        track_info["various_artist_dist_rule"] = distRuleCleanup(self.mb_release['title'][:1])
        
        track_info.update(mutagen_meta)
        
        # Get item code - if this track is a radio edit, 
        # assign a unique track id so that we can also have a non-radio edit version w/ MBID as item code
        if track_info['kexp_obscenity_rating'].upper() == 'RADIO EDIT':
            item_code = str(UUID.uuid4())
            track_type = str("track-with-filewalker-GUID")
        else:
            item_code = track_info['release_track_id']
            track_type = str("track")
            
        track_info['item_code'] = item_code

        track_log = track_type + "\t" + str(track_info["item_code"]) + "\t" + str(track_info["title"]) + "\r\n"

        track_info['log'] = track_log
        
        return track_info
        
    def get_track(self, mutagen_meta):
        track_info = self.process_track(mutagen_meta)
        return track_info

    
#####
# == Process Artist
# Pulls out the artist metadata that we are interested in from the raw MusicBrainz artist meta
# NOT CURRENTLY IN USE
#####
def process_artist(mb_artist):
    artist_info = {}
    artist_info['item_code'] = mb_artist['id']
    title = mb_artist['name']
    artist_info['disambiguation'] = ''
    if 'disambiguation' in mb_artist:
        title = title + " (" + mb_artist['disambiguation'] + ") "
        artist_info['disambiguation'] = mb_artist['disambiguation']
    artist_info['title'] = title
    log_text = "artist\t" + str(mb_artist["item_code"]) + "\t" + str(title) + "\r\n"
    artist_info["log_text"] = log_text
    artist_info['name'] = mb_artist['name']
    artist_info['sort_name'] = mb_artist['sort-name']
    artist_info['artist_id'] = mb_artist['id']
    
    artist_info['alias_list'] = []
    if 'alias-list' in mb_artist:
        for alias in mb_artist['alias-list']:
            if 'alias' in alias:
                artist_info['alias_list'].append(mb_artist['alias'])
    
    artist_info['annotation'] = ''
    if 'annotation' in mb_artist:
        if 'annotation' in mb_artist['annotation']:
            artist_info['annotation'] = mb_info[annotation][text]

    artist_info['type'] = ''
    if 'type' in mb_artist:
        artist_info['type'] = mb_artist['type']
    
    artist_info['begin_area_name'] = ''
    artist_info['begin_area_mbid'] = ''
    if 'begin-area' in mb_artist:
        artist_info['begin_area_name'] = mb_artist['begin-area']['name']
        artist_info['begin_area_mbid'] = mb_artist['begin-area']['id']
    
    artist_info['begin_date'] = ''
    artist_info['end_date'] = ''
    artist_info['ended'] = ''
    if 'life-span' in mb_artist:
        if 'begin' in mb_artist["life-span"]:
            artist_info['begin_date'] = mb_artist['life-span']['begin']
        if 'end' in mb_artist['life-span']:
            artist_info['end_date'] = mb_artist['life-span']['end']
        if 'ended' in mb_artist['life-span']:
            artist_info['ended'] = 1 if mb_artist['life-span']['ended'].lower() == 'true' else 0
    
    artist_info['area_name'] = ''
    artist_info['area_mbid'] = ''
    if 'country' in mb_artist:
        artist_info['area_name'] = mb_artist['area']['name']
        artist_info['area_mbid'] = mb_artist['area']['id']
    
    artist_info['end_area_name'] = ''
    artist_info['end_area_mbid'] = ''
    if 'end-area' in mb_artist:
        artist_info['end_area_name'] = mb_artist['end-area']['name']
        artist_info['end_area_mbid'] = mb_artist['area']['id']
        
    artist_info['ipi_list'] = []
    if 'ipi-list' in mb_artist:
        artist_info['ipi_list'] = mb_artist['ipi-list']
    
    artist_info['isni_list'] = []
    if 'isni-list' in mb_artist:
        artist_info['isni_list'] = mb_artist['isni-list']
    
    artist_info['url_list'] = []
    if 'url-relation-list' in mb_artist:
        for link in mb_artist['url-relation-list']:
            if 'target' in link:
                artist_info['url_list'].append(link['target'])
    return artist_info
    
def distRuleCleanup(rule):
    cleanRule = rule
    if not rule.isalpha():
        cleanRule = '#'
    else:
        rule = unicodedata.normalize('NFKD', rule).encode('ascii', 'ignore').decode()
        if len(rule) > 0:
            cleanRule = rule
    return cleanRule
    
def stringCleanup(text):
    clean = {'\\': '-', '/': '-', '\"': '\''}
    for character, replacement in clean.items():
        text = text.replace(character, replacement)
    return text