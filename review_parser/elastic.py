from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, String

class ElasticReview(DocType):
    filename = String(index='not_analyzed')
    rotation = String(index='not_analyzed')
    name = String(analyzer='standard')
    artistCredit = String(analyzer='standard')
    review = String(index='not_analyzed')
    reviewedBy = String(index='not_analyzed')
    oneStarTracks = String(index='not_analyzed',multi=True)
    twoStarTracks = String(index='not_analyzed',multi=True)
    threeStarTracks = String(index='not_analyzed',multi=True)

    class Meta:
        index = 'reviews'
    
