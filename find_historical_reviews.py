import os
import argparse
from review_parser import serializer, mb_release, elastic
import yaml
import unicodedata

def printReviews(reviews):
    foundCount = 0
    missingCount = 0
    missing = []
    for review in reviews:
        mbID = review.mbID
        if mbID is None:
            missingCount += 1
            missing.append(review)
        else:
            foundCount += 1
            if review.tracks is None or len(review.tracks) == 0:
                trackCount = 'NO TRACKS'
            else:
                trackCount = str(len(review.tracks)) + " Tracks"
            print("'%s' by %s: %s - %s" % (review.name, review.artistCredit, mbID, trackCount))

    if missingCount > 0:
        print('\nReviews missing MusicBrainz IDs:')
        for review in missing:
            print("    '%s' by %s" % (review.name, review.artistCredit))

    return foundCount

def exportReviews(reviews, outputDirectory):
    exportCount = 0
    fp = serializer.DaletSerializer(outputDirectory)
    for review in reviews:
        if review.mbID is not None and review.mbID > '':
            fp.saveRelease(review)
            if review.tracks:
                for track in review.tracks:
                    if track.itemCode is not None:
                        fp.saveTrack(track)
            else:
                debug='me'
            exportCount += 1

    return exportCount


def main():
    argParser = argparse.ArgumentParser(description='Processes a KEXP weekly review documents and generate Dalet review import.')
    argParser.add_argument('log_dir', help="JSON Release Log Directory")
    argParser.add_argument('-d', '--dalet', help="Directory to put Dalet Impex files in.")
    argParser.add_argument('-s', '--elastic_server', help="Elastic server IP or domain name, including port.")

    args = argParser.parse_args()
    daletDirectory = 'dalet'
    configFileName = 'review_parser.yml'
    if os.path.isfile(configFileName):
        config = yaml.safe_load(open(configFileName))
    else:
        config = {}

    jsonLogDir = args.log_dir

    if args.dalet is None:
        if 'dalet_directory' in config:
            daletDirectory = config['dalet_directory']
    else:
        daletDirectory = args.dalet

    if args.elastic_server is None:
        if 'elastic_server' in config:
            elastic_server = config['elastic_server']
    else:
        elastic_server = args.elastic_server

    if  elastic_server is None:
        print("No Elastic Server given in arguments or configuration file, we be stopping now!")
        return

    elastic.setup_elastic(elastic_server)
    releases = mb_release.readAllLogs(jsonLogDir)
    mergedReviews = []
    for release in releases:
        # Attempt to find review in Elastic Search
        review = elastic.ElasticReview.find_review_exact(release)
        if review is None:
            maybe = elastic.ElasticReview.find_review_loose(release)
            if maybe is not None:
                #print("MAYBE: %s by %s (%s by %s)" % (release.title, release.artist, maybe.name, maybe.artistCredit))
                msg = "FOUND '%s by %s' FOR '%s by %s'.  Use? Y[n]: "  % (release.title, release.artist, maybe.name, maybe.artistCredit)
                msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii')
                ans = input(msg)
                if ans.lower() == 'y':
                    review = maybe

        if review is not None:
            msg = "FOUND: %s by %s (%s by %s)" % (release.title, release.artist, review.name, review.artistCredit)
            msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii')
            print(msg)
            review.merge_release(release)
            mergedReviews.append(review)
        #else:
        #    print("Not found: %s by %s" % (release.title, release.artist))

    foundCount = len(mergedReviews)
    doExport = False
    exportCount = 0
    if foundCount > 0:
        doExport = True
        ans = input("We found %d reviews for the %d processed releases!  Would you like to export these reviews to Dalet? Y[n]: "  % (foundCount, len(releases)))
        if ans.lower() == 'n':
            doExport = False
    else:
        print("No reviews found for the %d processed releases." % (len(releases)))
    if doExport:
        exportCount = exportReviews(mergedReviews, daletDirectory)
        #for review in mergedReviews:
        #    review.save()

    print("%s reviews found, %s updated in Dalet" %(len(mergedReviews), exportCount))

if __name__ == "__main__":
    main()
    input("Press the [ENTER] key to finish....")
