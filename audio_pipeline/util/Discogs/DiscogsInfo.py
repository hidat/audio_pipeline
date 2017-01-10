import discogs_client
import time
import copy

useragent=("hidat_audio_pipeline", "0.1")
RETRY = 5

class DiscogsInfo:
    
    discogs = discogs_client.Client(useragent[0] + "/" + useragent[1])

    @classmethod
    def authorize_client(cls, useragent, user_token):
        cls.discogs = discogs_client.Client(useragent, user_token)
        
    @classmethod
    def get_release(cls, release_id):
        discogs_meta = None
        
        for i in range(RETRY):
            try:
                discogs_meta = cls.discogs.release(release_id)
                master = discogs_meta.master
                break
            except:
                time.sleep(.4)

        return discogs_meta.data
