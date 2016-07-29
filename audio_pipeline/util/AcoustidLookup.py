try:
    import acoustid
    have_acoustid = True
except ImportError:
    have_acoustid = False
import random
import collections
import os

LOOKUPS = 4
CUTOFF = .85

        
class Release:

    """
    Relevent data - release name, release artist, 
    """

    meta = "recordings releasegroups"
    api_key = "kz7oZf3Wbc"

    def __init__(self, audio_files):
        self.num_tracks = len(audio_files)
        self.tracks = audio_files
        self.releasegroups = collections.Counter()
        self.recordings = dict()
        self.can_lookup = False
        self.best_group = None

        # figure out just putting an fpcalc exe in here & then setting the environment variable from there
        # if acoustid.FPCALC_ENVVAR not in os.environ:
        #     os.environ[acoustid.FPCALC_ENVVAR]

        # this is terrible (but not as terrible as just tellin' you to set your FPCALC variable??)
        if have_acoustid:
            fpcalc_name = os.path.join("MusicBrainz Picard", "fpcalc.exe")
            fpcalc_path = os.path.join(os.environ["ProgramFiles"], fpcalc_name)
            if os.path.exists(fpcalc_path):
                os.environ[acoustid.FPCALC_ENVVAR] = fpcalc_path
            fpcalc_path = os.path.join(os.environ["ProgramFiles(x86)"], fpcalc_name)
            if os.path.exists(fpcalc_path):
                os.environ[acoustid.FPCALC_ENVVAR] = fpcalc_path
            if os.path.exists(os.environ[acoustid.FPCALC_ENVVAR]):
                self.can_lookup = True

    def lookup(self):
        if self.can_lookup:
            num_releases = LOOKUPS if len(self.tracks) > LOOKUPS else len(self.tracks)


            print(len(self.tracks))
            track_nums = [i for i in range(len(self.tracks))]
            random.shuffle(track_nums)
            print(track_nums)
            lookups = 0

            while len(track_nums) > 0:
                track = self.tracks[track_nums.pop()]
                if track.acoustid.value or track.meta_stuffed.value:
                    continue
                try:
                    fingerprint = acoustid.fingerprint_file(track.file_name)
                except acoustid.FingerprintGenerationError:
                    print("no way to generate fingerprint")
                    self.can_lookup = False
                    return

                lookups += 1
                track.acoustid.value = "NOT_FOUND"
                result = acoustid.lookup(self.api_key, fingerprint[1], fingerprint[0], Release.meta)

                for trackId in result["results"]:
                    if "recordings" in trackId:
                        for recording in trackId["recordings"]:
                            recording_id = recording["id"]
                            if recording_id in self.recordings:
                                self.recordings[recording_id] = max([self.recordings[recording_id], recording["score"]])
                            else:
                                self.recordings[recording_id] = trackId['score']
                                if "releasegroups" in recording:
                                    for releasegroup in recording["releasegroups"]:
                                        self.releasegroups[releasegroup['id']] += trackId['score'] * 1

                if lookups > num_releases:
                    if len(self.releasegroups) > 0:
                        group_counts = {count: group for group, count in self.releasegroups.items()}
                        max_count = max(self.releasegroups.values())
                        if max_count / lookups >= CUTOFF:
                            self.best_group = group_counts[max_count]
                            break
