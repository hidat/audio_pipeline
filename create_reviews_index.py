import argparse
from review_parser import elastic

def main():
    argParser = argparse.ArgumentParser(description='Creates the "reviews" index and mappings in ElasticSearch.')
    argParser.add_argument('-s', '--elastic_server', help="Elastic server IP or domain name, including port.")

    args = argParser.parse_args()

    elastic.setup_elastic(args.elastic_server)

    print('Creating Reviews Index and Mappings')
    elastic.create_review_index()

if __name__ == "__main__":
    main()