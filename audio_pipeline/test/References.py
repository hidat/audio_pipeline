format_testing_audio = "audio_pipeline\\test\\test_files\\audio\\tag_test_files"
write_testing_audio = "audio_pipeline\\test\\test_files\\audio\\write_test_files"
release_mbids = "audio_pipeline/test/test_files/test_mbids/release_mbids.json"
artist_mbids = "audio_pipeline/test/test_files/test_mbids/artist_mbids.json"
mb_dir = "audio_pipeline/test/test_files/mb_lookups"

t1_tags = {'tracktotal': 12, 'album': 'Who Killed...... The Zutons?',
           'encoder settings': '-compression-level-5', 'encoder': '(FLAC 1.2.1)',
           'albumartist': 'The Zutons', 'label': 'Deltasonic', 'date': '2004-04-19',
           'source': 'CD (Lossless)', 'discnumber': 1,
           'accurateripdiscid': '012-0011f4ba-00a8233b-8809700c-4', 'batchid': '50024',
           'encoded by': 'dBpoweramp Release 14.4', 'title': 'Confusion',
           'accurateripresult': 'AccurateRip: Accurate (confidence 62)   [37DEB629]', 
           'artist': 'The Zutons', 'tracknumber': 4, 'disctotal': 1,
           'genre': 'Rock', 'mbid': '5560ffa9-3824-44f4-b2bf-a96ae4864187', 'length': '0:07',
           'item_code': '8b3b7f33-4e8c-4146-90b7-96611863d133', 'obscenity': 'RED DOT'}

 
picard_tags = {'tracknumber': 6, 'totaltracks': 13, 'encoded by': 'dBpoweramp Release 14.4', 
            'media': 'CD', 'source': 'CD (Lossless)', 'releasestatus': 'official', 
            'script': 'Latn', 'accurateripresult': 'AccurateRip: Not in database   7CF59426',
            'musicbrainz_trackid': '89715e73-cfa8-487f-8aa1-18c3b7d965b9', 'releasecountry': 'GB',
            'mbid': '232775fc-277d-46e5-af86-5e01764abe5a', 
            'musicbrainz_releasetrackid': 'fe85af54-9982-34cc-9e0a-8d4d13a12350', 'disctotal': 1, 
            'artist': 'Rudi Zygadlo', 'discnumber': 1, 'artists': 'Rudi Zygadlo', 
            'albumartistsort': 'Zygadlo, Rudi', 
            'musicbrainz_albumartistid': '48f12b43-153e-42c3-b67c-212372cbfe2b', 
            'releasetype': 'album', 'batchid': '50024', 
            'accurateripdiscid': '013-0014462a-00cb7579-bf0a3e0d-6', 'tracktotal': 13, 
            'catalognumber': 'ZIQ320CD', 'artistsort': 'Zygadlo, Rudi', 
            'encoder': '(FLAC 1.2.1)', 'musicbrainz_releasegroupid': '06d97cd5-75a4-4ec8-afe3-1127b688c6ee',
            'musicbrainz_artistid': '48f12b43-153e-42c3-b67c-212372cbfe2b', 'totaldiscs': 1, 
            'album': 'Tragicomedies', 'originaldate': '2012-09-17', 'label': 'Planet Mu', 
            'date': '2012-09-17', 'title': 'The Domino Quivers', 'albumartist': 'Rudi Zygadlo', 
            'encoder settings': '-compression-level-5', 'originalyear': '2012', 'length': '0:07',
            'item_code': '89715e73-cfa8-487f-8aa1-18c3b7d965b9', 'obscenity': 'RED DOT'}
 
unknown_tags = {'accurateripresult': 'AccurateRip: Not in database   7A470C62', 
                'source': 'CD (Lossless) >> Perfect (Lossless) m4a', 
                'artist': 'Unknown Artist', 'disctotal': 1, 'tracktotal': 12,
                'accurateripdiscid': '012-0010ae26-009c5221-8e08ec0c-4',
                'encoded by': 'dBpoweramp Release 14.4', 'encoder': '(FLAC 1.2.1)',
                'title': 'Track04', 'tracknumber': 4, 'discnumber': 1, 'length': '0:07'}

empty_tags = {}