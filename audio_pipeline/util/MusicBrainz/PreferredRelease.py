import difflib

from audio_pipeline.util import Util
from audio_pipeline.util import Process


class BestRelease:
    sequence_matcher = difflib.SequenceMatcher(None, None, None)


    weights = {"type": {"Album": .5}, "medium_count": .5, "medium": .4, "track_count": .7,
               "track_position": .7, "country": {"US": .6}, "format": {"CD": .4}}

    features = ["track_num", "disc_num", "release_artist", "release", "country", "format", "type"]

    def __init__(self, results):
        self.results = results
        self.best_release = None
        self.all_releases = dict()
        self.process = Process.Processor()

    def choose_release(self):

        for group, count in self.results.releasegroups.items():
            releases = self.process.get_releases(group)

            for release_processor in releases:
                release = release_processor.release
                score = 0
                for release_type, weight in self.weights["type"].items():
                    if release_type == release.release_type:
                        score += weight

                for media_format, weight in self.weights["format"].items():
                    if release.format == media_format:
                        score += weight
                for disc in release.media:
                    if disc.tracks == len(self.results.tracks):
                        score += self.weights["track_count"]
                        break

                for country, weight in self.weights["country"].items():
                    if release.country == country:
                        score += weight

                if release.id in self.all_releases:
                    self.all_releases[release.id] += score * count
                else:
                    self.all_releases[release.id] = score * count

        if len(self.all_releases) > 0:
            max_score = max(self.all_releases.values())
            for mb, score in self.all_releases.items():
                if score == max_score:
                    self.best_release = mb

    def mb_comparison(self, ignore_mbid=False):
        max_ratio = 0
        if not ignore_mbid:
            track = self.results.track[0]
            if Util.has_mbid(track):
                return max_ratio

        # get & process MB metadata
        if len(self.results.releasegoups) > 0:
            ratios = dict()
            for group in self.results.releasegroups:
                releases = self.process.get_releases(group)
                for release in releases:
                    meta = release.release

                    calc_ratio = self.calc_ratio(None, None)
                    ratios[meta.id] = calc_ratio.send(None)
                    for track in self.results.tracks:
                        ratios[meta.id] = calc_ratio.send((track.album, meta.title))
                        ratios[meta.id] = calc_ratio.send((track.album_artist, meta.artist))
                        ratios[meta.id] = calc_ratio.send((track.release_date, meta.date))
                        ratios[meta.id] = calc_ratio.send((track.disc_num, meta.disc_count))

                        if len(meta.labels) > 0:
                            track.label.value = meta.labels[0].title

                        if meta.disc_count is not None and \
                            track.disc_num.value <= meta.disc_count:
                            track_meta = release.get_track(track)
                            # need to create new processor w/ no item_code save - for now, just kill it here.
                            track.item_code.value = None
                            track.item_code.save()
                            ratios[meta.id] = calc_ratio.send((track.title, track_meta.title))
                            if track_meta.artist_phrase:
                                ratios[meta.id] = calc_ratio.send((track.artist, track_meta.artist_phrase))
                            else:
                                ratios[meta.id] = calc_ratio.send((track.artist, track_meta.artist_credit))
                        else:
                            # this release will not work at all
                            ratios[meta.id] = 0
                            break
            max_ratio = max(ratios.values())
            for release, ratio in ratios.items():
                if ratio == max_ratio:
                    self.best_release = release
        return max_ratio

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

    def set_mbid(self, release_id):
        print("Setting MBIDs")
        for track in self.results.tracks:
            track.mbid.value = release_id
            