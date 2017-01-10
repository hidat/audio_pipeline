from .. import Process

class ReleaseProcessor(Process.ReleaseProcessor):
    
    def __init__(self, discogs_release):
        self.discogs_release = discogs_release
        self.media = []
        self.artist_joins = []
        self._release = None
        
    def stuff_audiofile(self, audio_file):
        """
        Stuff the given audiofile (which should already have a track number)
        with the data retrieved from discogs
        """
        
        # leave the mbid alone; they can remove it manually if they'd like to.
        # Sometimes the discogs info will be used supplementally.
#         audio_file.mbid.value = None
        audio_file.album_artist.value = self.release.artist
        audio_file.album.value = self.release.title
        audio_file.release_date.value = self.release.date
        if len(self.release.labels) > 0:
            audio_file.label.value = [label.title for label in self.release.labels]
            audio_file.catalog_num.value = [label.catalog_num for label in self.release.labels]
        audio_file.country.value = self.release.country
        if len(self.release.barcode) > 0:
            audio_file.barcode.value = self.release.barcode
        if len(self.release.release_type) > 0:
            audio_file.release_type.value = self.release.release_type
        if len(self.release.format) > 0:
            audio_file.media_format.value = self.release.format[0]

        track = self.get_track(audio_file)

        audio_file.title.value = track.title
        if track.artist_phrase:
            audio_file.artist.value = track.artist_phrase
        else:
            audio_file.artist.value = track.artist_credit
        audio_file.disc_num.value = track.disc_num
        audio_file.track_num.value = track.track_num
        audio_file.meta_stuffed.value = "yep"
    
    def process_release(self):
        if not self._release:
            meta = self.discogs_release
            
            # automatic item-code setting only happens if we have a musicbrainz id -
            # if there's no MB id, we'll set item code to 'None'
            release = Process.Resources.Release(item_code = None)
        
            # 'id' corresponds to mbid - can't set with only discogs meta
            release.id = None
            release.discogs_id = meta['id']
            release.title = meta["title"]
            
            # release group id is musicbrainz id
#             release.release_group_id = rg['id']
            
            # to get first released, need to get the master release metadata
#             release.first_released = rg['first-release-date']

            # to determine primary type from discogs, will select the 'description' from 'format'
            # that is also one of musicbrainz' primary types
            release_types = []
            for item in meta["formats"]:
                if "descriptions" in item:
                    for desc in item["descriptions"]:
                        if desc.casefold() in Process.primary_types:
                            release_types.append(desc)
                            break
                elif "text" in item:
                    if item["text"].casefold() in Process.primary_types:
                        release_types.append(item["text"])
                        break
                if not release_types:
                    # if we haven't found any primary release type, we're going to guess it's an album
                    release_types.append("Album")
                release.format.append(item["name"])
                    
            release.release_type = " + ".join(release_types)

            # have to determine track lists for discs - discogs flattens tracks from all mediums
            # into one list
            for track in meta["tracklist"]:
                position = track['position'].split("-")
                if len(position) > 1:
                    disc_num, track_num = (int(pos) for pos in position)
                else:
                    disc_num = 1
                    track_num = int(position[0])
                if len(self.media) < disc_num:
                    self.media.append([])
                    
                disc_index = disc_num - 1
                    
                track["track_num"] = track_num
                self.media[disc_index].append(track)
                
            for disc_num in range(len(self.media)):
                release.media.append(Process.Resources.Disc(disc_num, len(self.media[disc_num])))
            
            release.disc_count = len(self.media)
            
            # no 'tag-list' equivalent from discogs
#             if 'tag-list' in rg:
#                 release.tags = rg['tag-list']
            
            # as far as I can tell, w/ discogs the 'artist credit' and 'artist' are going to end up the same
            for artist in meta["artists"]:
                if self.artist_joins != []:
                    release.artist += " " + self.artist_joins[-1] + " "
                release.artist += artist["name"]
                release.artists.append(artist["name"])
                self.artist_joins.append(artist["join"])

#             if 'disambiguation' in meta:
#                 release.disambiguation = meta['disambiguation']
                
            # release identifiers
            for identifier in meta["identifiers"]:
                if identifier["type"] == "Barcode":
                    release.barcode = identifier["value"]
            
            if "labels" in meta:
                for discogs_label in meta["labels"]:
                    label = Process.Resources.Label(None, None, discogs_label["name"])
                    if "catno" in discogs_label:
                        label.catalog_num = discogs_label["catno"]
                    release.labels.append(label)

            if "released" in meta:
                release.date = meta["released"]
            if "country" in meta:
                release.country = meta["country"]
            
            # need to do some more examining of data to see if discogs has asin and packaging
#             if 'asin' in meta:
#                 release.asin = meta['asin']
#             if 'packaging' in meta:
#                 release.packaging = meta['packaging']
                
#             full_name = ''
#             for artist in meta['artist-credit']:
#                 if 'artist' in artist:
#                     a = artist['artist']
#                     full_name = full_name + a['name']
#                     release.artist_ids.append(a['id'])
#                     release.artist_sort_names.append(a['sort-name'])
#                 else:
#                     full_name = full_name + artist

            self._release = release
            
    
    def process_track(self, audio_file):
        """
        Extract the track metadata we care about from the release metadata & AudioFile metadata.
        """
        
        disc_index = audio_file.disc_num.value - 1    # zero-index the disc num
        track_index = audio_file.track_num.value - 1  # zero-index the track num

        # create the track object
        track = Process.Resources.Track()
        
        release_meta = self.release
        
        if disc_index < release_meta.disc_count:
            disc = self.media[disc_index]
        else:
            return track
            
        if track_index < len(disc):
            track_meta = disc[track_index]
        else:
            return track
        
        if 'title' in track_meta:
            track.title = track_meta['title']
        
        track.disc_num = audio_file.disc_num.value
        track.track_num = audio_file.track_num.value
#         track.obscenity = str(audio_file.obscenity)
        
        artist_joins = []
        if 'artists' in track_meta:
            for artist in track_meta['artists']:
                if artist_joins != []:
                    track.artist_credit += " " + artist_joins[-1] + " "
                track.artist_credit += artist["name"]
                artist_joins.append(artist["join"])
                
        if 'extraartists' in track_meta:
            for artist in track_meta['extraartists']:
                track.extra_artists.append((artist["name"], artist["role"]))
                
        if track.artist_credit == '':
            track.artist_credit = release_meta.artist    
            
        return track
    