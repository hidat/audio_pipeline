import acoustid
import random
import difflib
from audio_pipeline import Constants
from . import Process
from . import MBInfo

class ReleaseLookup:
    
    api_key = "kz7oZf3Wbc"
    
    def __init__(self, client_key):
        self.client_key = client_key
        
class Release:

    """
    Relevent data - release name, release artist, 
    """
    
    sequence_matcher = difflib.SequenceMatcher(None, None, None)
    api_key = "kz7oZf3Wbc"

    meta = "releasegroups recordings releases tracks compress"
    
    weights = {"type": {"Album": .5}, "medium_count": .5, "medium": .4, "track_count": .7, 
               "track_position": .7, "country": {"US": .6}, "format": {"CD": .4}}
               
    features = ["track_num", "disc_num", "release_artist", "release", "country", "format", "type"]
    
    def __init__(self, audio_files):
        self.num_tracks = len(audio_files)
        self.tracks = audio_files
        self.results = list()
        self.releases = dict()
        self.common_releases = dict()
        self.max_score = 0
        self.likely_release = None
        self.processor = Process.Processor(MBInfo.MBInfo(), Constants.processor)
        self.release = None
        
    def weight(self, track, fingerprint_score, releasegroup):
        base_score = 0
        
        if "type" in releasegroup:
            for release_type, weight in self.weights["type"].items():
                if releasegroup["type"] == release_type:
                    base_score += weight
                    
        if "releases" in releasegroup:
            for release in releasegroup["releases"]:
                calc_ratio = self.calc_ratio(None, None)
                ratio = 0
                calc_ratio.send(None)
                
                score = base_score
                release_id = release["id"]

                if "mediums" in release:
                    medium = release["mediums"][0]
                    for media_format, weight in self.weights["format"].items():
                        if medium.get("format") == media_format:
                            score += weight
                    if medium.get("tracks"):
                        if medium["tracks"][0].get("position") == track.track_num.value:
                            score += self.weights["track_position"]
                    if medium.get("track_count") == self.num_tracks:
                        score += self.weights["track_count"]
                else:
                    if release.get("track_count") == self.num_tracks:
                        score += self.weights["track_count"]
                        
                for country, weight in self.weights["country"].items():
                    if release.get("country") == country:
                        score += weight
                        
                if track.album.value is not None:
                    if "title" in releasegroup:
                        ratio = calc_ratio.send((track.album, releasegroup.get("title")))
                    if "mediums" in release:
                        medium = release["mediums"][0]
                        ratio = calc_ratio.send((track.disc_num, medium.get("position")))
                    # ratio = calc_ratio.send((track.total_discs, release.get("medium_count")))
                        
                score = score if score > 1 else 1
                score *= ratio + 1
                        
                if release_id in self.common_releases:
                    self.common_releases[release_id] += fingerprint_score * score
                else:
                    self.releases[release_id] = release
                    self.common_releases[release_id] = fingerprint_score * score
        
    def lookup(self, num_lookups=4):
        # gonna want to look into some actual clever stuff for here, but for now:
        self.releases = dict()
        self.common_releases = dict()
        
        # for now, let's just take ~four releases haha
        for i in range(num_lookups):
            track = random.choice(self.tracks)
        
        #for track in self.tracks:
            # fingerprint & lookup each track in the AcoustID database
            fingerprint = acoustid.fingerprint_file(track.file_name)
            result = acoustid.lookup(self.api_key, fingerprint[1], fingerprint[0], self.meta)
            self.results.append(result)

            for trackId in result["results"]:
                if "recordings" in trackId:
                    for recording in trackId["recordings"]:
                        # start out just keeping track of all common releases
                        if "releasegroups" in recording:
                            for releasegroup in recording["releasegroups"]:
                                self.weight(track, trackId["score"], releasegroup)
                            
        for release, score in self.common_releases.items():
            if score > self.max_score:
                self.likely_release = release
                self.max_score = score
                
        print(self.likely_release)
        print(self.max_score)
        
    def stuff_meta(self):
        if not self.likely_release:
            self.lookup()
        if self.likely_release:
            if not self.release:
                self.release = self.processor.get_release(self.likely_release)
            meta = self.release.release

            # stuff audiofiles using values from musicbrainz
            for track in self.tracks:
                track.mbid.value = meta.id
                track.album.value = meta.title
                track.album_artist.value = meta.artist
                track.release_date.value = meta.date
                if len(meta.labels) > 0:
                    track.label.value = meta.labels[0].title

                if meta.disc_count is None:
                    pass
                elif track.disc_num.value <= meta.disc_count:
                    track_meta = self.release.get_track(track)
                    track.title.value = track_meta.title
                    if track_meta.artist_phrase:
                        track.artist.value = track_meta.artist_phrase
                    else:
                        track.artist.value = track_meta.artist_credit
                else:
                    track.artist.value = meta.artist

                track.save()

    def mbid_comp(self, ignore_mbid=False):
        if not ignore_mbid:
            track = self.tracks[0]
            if track.mbid.value != None:
                return 0
            
        if not self.likely_release:
            self.lookup()
        if self.likely_release:
            # get & process MB metadata
            if not self.release:
                self.release = self.processor.get_release(self.likely_release)
            meta = self.release.release

            calc_ratio = self.calc_ratio(None, None)
            calc_ratio.send(None)
            for track in self.tracks:
                calc_ratio.send((track.album, meta.title))
                calc_ratio.send((track.album_artist, meta.artist))
                calc_ratio.send((track.release_date, meta.date))
                if len(meta.labels) > 0:
                    track.label.value = meta.labels[0].title
                    
                if meta.disc_count is not None and \
                    track.disc_num.value <= meta.disc_count:
                    track_meta = self.release.get_track(track)
                    calc_ratio.send((track.title, track_meta.title))
                    if track_meta.artist_phrase:
                        calc_ratio.send((track.artist, track_meta.artist_phrase))
                    else:
                        calc_ratio.send((track.artist, track_meta.artist_credit))
            ratio = calc_ratio.send((None, None))
            return(ratio)
                        
    def calc_ratio(self, track_tag, meta_val):
        ratio = 1
        i = 1

        while True:
            if track_tag != None and track_tag.value != None:
                self.sequence_matcher.set_seqs(str(track_tag), str(meta_val))
                curr = self.sequence_matcher.ratio()
                if (curr < .7):
                    print("current tag: " + str(track_tag.name) + " with value " + str(track_tag))
                    print("acquired meta: " + str(meta_val))
                ratio = ratio * (i - 1) / i + (1 / i) * self.sequence_matcher.ratio()
                i += 1
            track_tag, meta_val = yield ratio
