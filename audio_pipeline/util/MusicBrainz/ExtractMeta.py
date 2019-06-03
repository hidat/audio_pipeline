from .. import Process


class ReleaseProcessor(Process.ReleaseProcessor):
    def __init__(self, mb_release):
        self.mb_release = mb_release
        self._release = None

    def process_release(self):
        """
        Extract release metadata we care about from the raw MusicBrainz metadata
        """
        if not self._release:
            meta = self.mb_release

            release = Process.Resources.Release(item_code=meta['id'])

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
                release.media.append(Process.Resources.Disc(disc['position'], len(disc['track-list'])))
                if 'format' in disc:
                    release.format.append(disc['format'])
                    formats = formats + " " + disc['format']

            release.artist_credit = meta['artist-credit']

            if 'disambiguation' in meta:
                release.disambiguation = meta['disambiguation']

            if 'label-info-list' in meta:
                for l in meta['label-info-list']:
                    if 'label' in l:
                        label = Process.Resources.Label(l['label']['id'], l['label']['id'], l['label']['name'])
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
        Extract the track metadata we care about from the release metadata (from musicbrainz)
        and the audio file's metadata tags
        """

        disc_index = 0
        if audio_file.disc_num is not None:
            disc_index = audio_file.disc_num.value - 1  # zero-index the disc num
        track_index = 0
        if audio_file.track_num is not None:
            track_index = audio_file.track_num.value - 1  # zero-index the track num

        # create the track object
        track = Process.Resources.Track()

        release_meta = self.release

        if disc_index < release_meta.disc_count:
            disc = self.mb_release['medium-list'][disc_index]
        else:
            # the disc num in the file tags is not compatible with the number of discs
            # in the musicbrainz release we retrived, so it's probably the wrong release
            # and we are not able to properly extract the metadata
            return track

        if track_index < len(disc['track-list']):
            track_meta = disc['track-list'][track_index]
        else:
            # the track number in the file tags is not compatible with the number of tracks
            # in the musicbrainz release we retrived, so it's probably the wrong release
            # and we are not able to properly extract the metadata
            return track

        recording_meta = track_meta['recording']

        ##########################
        # fields from track_meta
        ##########################

        track.id = track_meta['id']

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
            artist = Process.Resources.Artist(meta['id'])

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
