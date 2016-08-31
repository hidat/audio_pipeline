import os
import argparse
from review_parser import parser, ssheet, serializer, mb_release
import yaml

###
# Find Release
# Attempts to find the given review in the releases read from Smartsheet
# First looks for an exact match on title.  If no match is found, then looks at artist.  If there is a match on artist,
# and that artist only appears once, then uses that release.
###
def findRelease(review,  releases):
    # First try to find by title
    titleToFind = review.name.casefold()
    for release in releases:
        if release.normalizedTitle == titleToFind:
            return release

    # Not found on title, try to find artist
    artistRelease = None
    artistToFind = review.artistCredit.casefold()
    for release in releases:
        if release.normalizedArtist == artistToFind:
            if artistRelease is None:
                artistRelease = release
            else:
                return None  #Found multiple, bail out with nothing!

    return artistRelease

def mergeReviewsAndReleases(reviews, releases):
    for review in reviews:
        release = findRelease(review, releases)
        if release is not None:
            review.mbID = release.mbID
            review.daletGlossaryName = release.daletGlossaryName
            if release.tracks and review.tracks:
                for track in review.tracks:
                    if track.trackNum is not None:
                        trackNum = int(track.trackNum)
                        if trackNum in release.tracks:
                            releaseTrack = release.tracks[trackNum]
                            track.itemCode = releaseTrack.itemCode
                            track.title = releaseTrack.title

    return reviews

def getMbIdFromUser(review):
    mbID = input("Please enter the MBID for '%s' by %s: " % (review.name, review.artistCredit))
    return mbID

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

def fillInMissingReviews(reviews):
    missingCount = 0
    for review in reviews:
        if review.mbID is None:
            mbID = getMbIdFromUser(review)
            if mbID is not None and mbID > '':
                review.mbID = mbID
            else:
                missingCount += 1
    return missingCount

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
    argParser.add_argument('input_file', help="Word document to process.  Only docx files are supported.")
    argParser.add_argument('-l', '--log_dir', help="JSON Release Log File")
    argParser.add_argument('-k', '--api_key', help="Your Smartsheet API Key")
    argParser.add_argument('-d', '--dalet', help="Directory to put Dalet Impex files in.")
    argParser.add_argument('-w', '--worksheet', help="Smartsheet Worksheet ID that contains the reviews associated MusicBrainz ID's")

    args = argParser.parse_args()
    apiKey = None
    sheetId = None
    jsonLogFile = None
    daletDirectory = 'dalet'
    configFileName = 'review_parser.yml'
    if os.path.isfile(configFileName):
        config = yaml.safe_load(open(configFileName))
    else:
        config = {}

    jsonLogDir = args.log_dir

    if args.worksheet is None:
        if 'worksheet' in config:
            sheetId = config['worksheet']
    else:
        sheetId = args.worksheet

    if args.api_key is None:
        if 'api_key' in config:
            apiKey = config['api_key']
    else:
        apiKey = args.api_key

    if args.dalet is None:
        if 'dalet_directory' in config:
            daletDirectory = config['dalet_directory']
    else:
        daletDirectory = args.dalet

    if jsonLogDir is None:
        if apiKey is None:
            print("No API key provided.  Please specify your Smartsheet API key using the '-k' option, or set it in your 'review_parser.yml' file.")
            return

        if sheetId is None:
            print("No worksheet ID provided.  Please specify the Smartsheet worksheet ID by using the '-w' option, or set it in your 'review_parser.yml' file.")
            return

    reviews= []
    if os.path.isfile(args.input_file):
        fp = parser.DocParser(args.input_file)
        reviews = fp.process()
    elif os.path.isdir(args.input_file):
        fp = parser.DirectoryParser(args.input_file)
        reviews = fp.process()

    if len(reviews) > 0:
        exportCount = 0
        if jsonLogDir is None:
            sdk = ssheet.SDK(apiKey)
            releases = sdk.readWeeklySheet(sheetId)
        else:
            releases = mb_release.readAllLogs(jsonLogDir)

        mergedReviews = mergeReviewsAndReleases(reviews, releases)
        foundCount = printReviews(mergedReviews)
        missingCount = len(mergedReviews) - foundCount
        if missingCount > 0:
            ans = input("Would you like to enter missing MusicBrainz IDs now? [Y]n: ")
            if ans.lower() == 'y' or ans == '':
                missingCount = fillInMissingReviews(reviews)
        doExport = missingCount == 0
        if missingCount > 0:
            ans = input("There are still %s reviews missing MusicBrainz IDs, would you like to export to Dalet amyway? y[N]: "  % (missingCount))
            if ans.lower() == 'y':
                doExport = True
        if doExport:
            exportCount = exportReviews(mergedReviews, daletDirectory)
        print("%s reviews found, %s updated in Dalet" %(len(mergedReviews), exportCount))
    else:
        print(args.input_file + " does not appear to be a valid file.")

if __name__ == "__main__":
    main()
    input("Press the [ENTER] key to finish....")
