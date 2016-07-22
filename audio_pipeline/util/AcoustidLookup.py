try:
    import acoustid
    have_acoustid = True
except ImportError:
    have_acoustid = False
import random
import difflib
from audio_pipeline import Constants
from . import Process
from . import MBInfo
import os

        
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
        self.can_lookup = False

        # figure out just putting an fpcalc exe in here & then setting the environment variable from there
        # if acoustid.FPCALC_ENVVAR not in os.environ:
        #     os.environ[acoustid.FPCALC_ENVVAR]

        # this is terrible (but not as terrible as just tellin' you to set your FPCALC variable??)
        fpcalc_name = os.path.join("MusicBrainz Picard", "fpcalc.exe")
        fpcalc_path = os.path.join(os.environ["ProgramFiles"], fpcalc_name)
        if os.path.exists(fpcalc_path):
            os.environ[acoustid.FPCALC_ENVVAR] = fpcalc_path
        fpcalc_path = os.path.join(os.environ["ProgramFiles(x86)"], fpcalc_name)
        if os.path.exists(fpcalc_path):
            os.environ[acoustid.FPCALC_ENVVAR] = fpcalc_path
        if os.path.exists(os.environ[acoustid.FPCALC_ENVVAR]):
            self.can_lookup = True

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

        if have_acoustid and self.can_lookup:
            if num_lookups > len(self.tracks):
                num_lookups = len(self.tracks)

            # for now, let's just take ~four releases haha
            for track in random.sample(self.tracks, num_lookups):

                # fingerprint & lookup each track in the AcoustID database
                try:
                    fingerprint = acoustid.fingerprint_file(track.file_name)
                except acoustid.FingerprintGenerationError:
                    print("no way to generate fingerprint")
                    self.can_lookup = False
                    return
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

            print("likely release: " + str(self.likely_release))
            print("max score: " + str(self.max_score))
        
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
                    # need to create new processor w/ no item_code save - for now, just kill it here.
                    track.item_code.value = None
                    track.title.value = track_meta.title
                    if track_meta.artist_phrase:
                        track.artist.value = track_meta.artist_phrase
                    else:
                        track.artist.value = track_meta.artist_credit
                else:
                    track.artist.value = meta.artist
                    track.title.value = ""


                track.save()

    def mbid_comp(self, ignore_mbid=False):
        if not ignore_mbid:
            track = self.tracks[0]
            if track.mbid.value != None:
                return 0
            
        if not self.likely_release:
            self.lookup(3)
        if self.likely_release:
            # get & process MB metadata
            if not self.release:
                self.release = self.processor.get_release(self.likely_release)
            meta = self.release.release

            calc_ratio = self.calc_ratio(None, None)
            ratio = calc_ratio.send(None)
            for track in self.tracks:
                ratio = calc_ratio.send((track.album, meta.title))
                ratio = calc_ratio.send((track.album_artist, meta.artist))
                ratio = calc_ratio.send((track.release_date, meta.date))
                ratio = calc_ratio.send((track.disc_num, meta.disc_count))

                if len(meta.labels) > 0:
                    track.label.value = meta.labels[0].title

                if meta.disc_count is not None and \
                    track.disc_num.value <= meta.disc_count:
                    track_meta = self.release.get_track(track)
                    # need to create new processor w/ no item_code save - for now, just kill it here.
                    track.item_code.value = None
                    track.item_code.save()
                    ratio = calc_ratio.send((track.title, track_meta.title))
                    if track_meta.artist_phrase:
                        ratio = calc_ratio.send((track.artist, track_meta.artist_phrase))
                    else:
                        ratio = calc_ratio.send((track.artist, track_meta.artist_credit))
                else:
                    # this release will not work at all
                    ratio = 0
                    break
            return ratio
                        
    def calc_ratio(self, track_tag, meta_val):
        ratio = 1
        i = 1

        while True:
            if not (track_tag is None or track_tag.value is None):
                self.sequence_matcher.set_seqs(str(track_tag), str(meta_val))
                curr = self.sequence_matcher.quick_ratio()
                ratio = ratio * (i - 1) / i + (1 / i) * self.sequence_matcher.ratio()
                i += 1
            track_tag, meta_val = yield ratio
