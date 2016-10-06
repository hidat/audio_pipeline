from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Index, Mapping, DocType, String, Integer, analyzer, tokenizer, token_filter
from elasticsearch_dsl.query import Match, Bool
from review_parser.reviewtrack import ReviewTrack

####
# Custom Name Analyzer
# This requires the ICU Analysis Plugin
# To install, on the elasticsearch server, execute the following in you elasticsearch directory.
# sudo bin/plugin install analysis-icu
####
stopword_filter = token_filter({"type": "stop", "stopwords":"_english_"})
name_analyzer = analyzer('name_analyzer',
    tokenizer = "standard",
    filter = ['standard', 'lowercase', "stop", 'icu_folding']
)

def setup_elastic(server):
    if server is None:
        server='localhost'
    connections.create_connection(hosts=[server], timeout=20)

reviews_index_name = 'reviews'

def create_review_index():
    reviews = Index(reviews_index_name)
    reviews.delete(ignore=404)

    reviews.settings(number_of_shards=2, number_of_replicas=0)
    reviews.doc_type(ElasticReview)
    reviews.create()
    reviews.close()

    #reviews.analyzer(name_analyzer)

    m = Mapping('elastic_review')
    m.field('filename', 'string', index='not_analyzed')
    m.field('name', 'string', analyzer = name_analyzer)
    m.field('artistCredit', 'string', analyzer = name_analyzer)
    m.field('review', 'string', index='not_analyzed')
    m.field('reviewedBy', 'string', index='not_analyzed')
    m.field('oneStarTracks', 'integer', index='not_analyzed',multi=True)
    m.field('twoStarTracks', 'integer', index='not_analyzed',multi=True)
    m.field('threeStarTracks', 'integer', index='not_analyzed',multi=True)
    m.save(reviews_index_name)

    reviews.open()
    return reviews

class ElasticReview(DocType):

    filename = String(index='not_analyzed')
    rotation = String(index='not_analyzed')
    name = String(analyzer=name_analyzer)
    artistCredit = String(analyzer=name_analyzer)
    review = String(index='not_analyzed')
    reviewedBy = String(index='not_analyzed')
    oneStarTracks = Integer(index='not_analyzed',multi=True)
    twoStarTracks = Integer(index='not_analyzed',multi=True)
    threeStarTracks = Integer(index='not_analyzed',multi=True)

    class Meta:
        index = reviews_index_name

    def merge_release(self, release):
        self.mbID = release.mbID
        self.daletGlossaryName = release.daletGlossaryName
        self.tracks = []
        for trackNumS in self.oneStarTracks:
            if trackNumS is not None:
                try:
                    trackNum = int(trackNumS)
                except:
                    debug = 'me'
                track = ReviewTrack(None)
                track.trackNum = trackNum
                track.stars = 1
                if trackNum in release.tracks:
                    releaseTrack = release.tracks[trackNum]
                    track.itemCode = releaseTrack.itemCode
                    track.title = releaseTrack.title
                self.tracks.append(track)

        for trackNumS in self.twoStarTracks:
            if trackNumS is not None:
                trackNum = int(trackNumS)
                track = ReviewTrack(None)
                track.trackNum = trackNum
                track.stars = 2
                if trackNum in release.tracks:
                    releaseTrack = release.tracks[trackNum]
                    track.itemCode = releaseTrack.itemCode
                    track.title = releaseTrack.title
                self.tracks.append(track)

        for trackNumS in self.threeStarTracks:
            if trackNumS is not None:
                trackNum = int(trackNumS)
                track = ReviewTrack(None)
                track.trackNum = trackNum
                track.stars = 3
                if trackNum in release.tracks:
                    releaseTrack = release.tracks[trackNum]
                    track.itemCode = releaseTrack.itemCode
                    track.title = releaseTrack.title
                self.tracks.append(track)


    @staticmethod
    def find_review_exact(release):
        review = None
        s = ElasticReview.search()
        #q = Match(name={"query": release.title, "type": "phrase"})
        q = Bool(must = [Match(name={"query": release.title, "operator": "or"}), Match(artistCredit={"query": release.artist})])
        s = s.query(q)
        resp = s.execute()
        if resp.hits.total > 0:
          review = resp.hits[0]

        return review

    def find_review_loose(release):
        review = None
        s = ElasticReview.search()
        q = Match(name={"query": release.title, "type": "phrase"})
        #q = Bool(must = [Match(name={"query": release.title, "operator": "and"}), Match(artistCredit={"query": release.artist, "operator": "and"})])
        s = s.query(q)
        resp = s.execute()
        if resp.hits.total == 1:
            review = resp.hits[0]
        elif resp.hits.total > 1:
            review = resp.hits[0]

        return review
