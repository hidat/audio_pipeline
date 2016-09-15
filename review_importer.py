import os
import argparse
import operator
from review_parser import parser
from elasticsearch_dsl.connections import connections
from review_parser.elastic import ElasticReview

####
# Initialize the Elasticsearch Index
# ***** THIS DESTROYS ALL THE DATA IN THE INDEX!!!!!! *****
# Only works if the index is closed or does not already exist.
####
def initialize_index(server=None):
    setup_elastic(server)
    ElasticReview.init()


def setup_elastic(server):
    if server is None:
        server='localhost'
    connections.create_connection(hosts=[server], timeout=20)

def main():
    argParser = argparse.ArgumentParser(description='Processes a directory full of KEXP Weekly Review sheets and puts them into an ElasticSearch index.')
    argParser.add_argument('input_directory', help="Directory or file to process.  Only docx files are will be processed.")
    argParser.add_argument('-s', '--elastic_server', help="Elastic server IP or domain name, including port.")

    args = argParser.parse_args()

    setup_elastic(args.elastic_server)

    print('Parsing reviews from %s.' % (args.input_directory))
    # Parse all the raw reviews
    reviews= []
    if os.path.isfile(args.input_directory):
        fp = parser.DocParser(args.input_directory)
        reviews = fp.process()
    elif os.path.isdir(args.input_directory):
        fp = parser.DirectoryParser(args.input_directory)
        reviews = fp.process()

    # And now put them into elastic search

    print('Indexing %d reviews.' % (len(reviews)))
    c = 0
    for review in reviews:
        s1 = []
        for t in review.oneStarTracks:
            s1.append(t.trackNum)
        s2 = []
        for t in review.twoStarTracks:
            s2.append(t.trackNum)
        s3 = []
        for t in review.threeStarTracks:
            s3.append(t.trackNum)

        elastic_review = ElasticReview(
            filename=review.filename,
            rotation=review.rotation,
            name=review.name,
            artistCredit=review.artistCredit,
            label=review.label,
            review=review.review,
            reviewedBy=review.reviewedBy,
            oneStarTracks=s1,
            twoStarTracks=s2,
            threeStarTracks=s3
        )

        elastic_review.save()
        c+=1

    print('%d reviews indexed.' % c)

if __name__ == "__main__":
    main()

