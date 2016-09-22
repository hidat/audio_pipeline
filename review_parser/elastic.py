from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import Index, Mapping, DocType, String, Integer, analyzer, tokenizer

####
# Custom Name Analyzer
# This requires the ICU Analysis Plugin
# To install, on the elasticsearch server, execute the following in you elasticsearch directory.
# sudo bin/plugin install analysis-icu
####
name_analyzer = analyzer('name_analyzer',
    tokenizer = "standard",
    filter = ['standard', 'icu_folding', 'lowercase']
    #filter = ['standard', 'lowercase']
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
    
