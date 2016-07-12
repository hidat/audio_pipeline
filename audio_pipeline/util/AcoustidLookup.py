import acoustid
import random
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

    def weight(self, track, fingerprint_score, releasegroup):
        base_score = 0
        if "type" in releasegroup:
            for release_type, weight in self.weights["type"].items():
                if releasegroup["type"] == release_type:
                    base_score += weight
                    
        if "releases" in releasegroup:
            for release in releasegroup["releases"]:
                score = base_score
                release_id = release["id"]

                if "mediums" in release:
                    medium = release["mediums"][0]
                    for media_format, weight in self.weights["format"].items():
                        if medium.get("format") == media_format:
                            score += weight
                    if medium.get("position") == track.disc_num.value:
                        score += self.weights["medium"]
                    if medium.get("tracks"):
                        if medium["tracks"][0].get("position") == track.track_num.value:
                            score += self.weights["track_position"]
                    if medium.get("track_count") == self.num_tracks:
                        score += self.weights["track_count"]
                else:
                    if release.get("track_count") == self.num_tracks:
                        score += self.weights["track_count"]
                        
                if release.get("medium_count") == track.disc_num.total:
                    score += self.weights["medium_count"]
                for country, weight in self.weights["country"].items():
                    if release.get("country") == country:
                        score += weight
                        
                score = score if score > 1 else 1
                        
                if release_id in self.common_releases:
                    self.common_releases[release_id] += fingerprint_score * score
                else:
                    self.releases[release_id] = release
                    self.common_releases[release_id] = fingerprint_score * score
        
    def lookup(self):
        # gonna want to look into some actual clever stuff for here, but for now:
        self.releases = dict()
        self.common_releases = dict()
        
        # for now, let's just take ~four releases haha
        for i in range(4):
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
                            
        print(self.common_releases)
        for release, score in self.common_releases.items():
            if score > self.max_score:
                self.likely_release = release
                self.max_score = score
                
        print(self.likely_release)
        print(self.max_score)
        
    def stuff_meta(self):
        self.lookup()
        if self.likely_release:
            processor = Process.Processor(MBInfo.MBInfo(), Constants.processor)
            release = processor.get_release(self.likely_release)

            # stuff audiofiles using values from musicbrainz
            for track in self.tracks:
                meta = release.release
                track.mbid.value = meta.id
                track.album.value = meta.title
                track.album_artist.value = meta.artist
                track.release_date.value = meta.date
                if len(meta.labels) > 0:
                    track.label.value = meta.labels[0].title

                track_meta = release.get_track(track)
                track.title.value = track_meta.title
                if track_meta.artist_phrase:
                    track.artist.value = track_meta.artist_phrase
                else:
                    track.artist.value = track_meta.artist_credit

                track.save()

