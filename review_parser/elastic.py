from elasticsearch import Elasticsearch
from elasticsearch_dsl import DocType, String, analyzer, tokenizer

####
# Custom Name Analyzer
# This requires the ICU Analysis Plugin
# To install, on the elasticsearch server, execute the following in you elasticsearch directory.
# sudo bin/plugin install analysis-icu
####
name_analyzer = analyzer('name_analyzer',
    tokenizer = "standard",
    #filter = ['standard', 'icu_folding', 'lowercase']
    filter = ['standard', 'lowercase']
)

class ElasticReview(DocType):

    filename = String(index='not_analyzed')
    rotation = String(index='not_analyzed')
    name = String(analyzer=name_analyzer)
    artistCredit = String(analyzer=name_analyzer)
    review = String(index='not_analyzed')
    reviewedBy = String(index='not_analyzed')
    oneStarTracks = String(index='not_analyzed',multi=True)
    twoStarTracks = String(index='not_analyzed',multi=True)
    threeStarTracks = String(index='not_analyzed',multi=True)

    class Meta:
        index = 'reviews'
    
