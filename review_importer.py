import os
import argparse
import operator
from review_parser import parser
from elasticsearch_dsl.connections import connections
from review_parser.elastic import ElasticReview


def main():
    argParser = argparse.ArgumentParser(description='Processes a directory full of KEXP Weekly Review sheets and puts them into an ElasticSearch index.')
    argParser.add_argument('input_directory', help="Directory or file to process.  Only docx files are will be processed.")

    args = argParser.parse_args()

    # Setup elasticsearch - @TODO: Add to configuration file
    connections.create_connection(hosts=['localhost'], timeout=20)

    # Parse all the raw reviews
    reviews= []
    if os.path.isfile(args.input_directory):
        fp = parser.DocParser(args.input_directory)
        reviews = fp.process()
    elif os.path.isdir(args.input_directory):
        fp = parser.DirectoryParser(args.input_directory)
        reviews = fp.process()

    # And now put them into elastic search
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
            trackList=review.trackList,
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

