__author__ = 'cephalopodblue'
import json
import os


class JsonSerializer:
        
    @staticmethod
    def release_json(release):
        """
        Get a dictionary that we like & json also likes
        """
        release_data = {"glossary_title": release.glossary_title, "item_code": release.item_code, \
                        "name": release.title, "artist": release.artist}
        return json.dumps(release_data)
    
    @staticmethod
    def track_json(track):
        track_data = {"track_num": track.track_num, "track_name": track.title, \
                      "item_code": track.item_code}
        return json.dumps(track_data)

    @staticmethod
    def artist_json(artist):
        artist_data = {"name": artist.name, "item_code": artist.item_code}
        return json.dumps(artist_data)

        
class JsonLogger:
    
    def __init__(self, output_dir):
        self.releases = os.path.join(output_dir, "releases.json")
        self.track_dir = os.path.join(output_dir, "tracks")
        
        if not os.path.exists(self.track_dir):
            os.makedirs(self.track_dir)
            
    def log_release(self, release):
        with open(self.releases, "a+") as f:
            f.write(JsonSerializer.release_json(release))
            f.write("\n")
            
    def log_track(self, track):
        track_file = os.path.join(self.track_dir, (track.release_id + ".json"))
        with open(track_file, "a+") as f:
            f.write(JsonSerializer.track_json(track))
            f.write("\n")