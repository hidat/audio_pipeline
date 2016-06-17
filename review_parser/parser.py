import re
import unicodedata
import operator
import mammoth
import html
import csv
import os
from .review import Review
from .track import Track


class ReviewParser:
    reTrackSplit = re.compile(r",|&amp;")
    reReviewer = re.compile(r"[-]+([\w\s]+)")

    def __init__(self, filename, rotation):
        self.review = Review()
        self.review.filename = filename
        self.review.rotation = rotation

    @staticmethod
    def isNameString(nameStr):
        if len(nameStr) > 200:
            return False

        # Checks if the string is in the format of [ALBUM] - [ARTIST CREDIT] ([LABEL])
        labelStart = nameStr.rfind('(')
        if labelStart <= 0:
            return False

        s = nameStr[:(labelStart-1)]
        if s.find('- ') > -1:
            return True

        if s.find(' -') > -1:
            return True

        if s.find(': ') > -1:
            return True

        return False

    def parseNameString(self, nameStr):
        # Formatted as [ALBUM] - [ARTIST CREDIT] ([LABEL])
        nameStr = html.unescape(nameStr)
        nameStr = re.sub("<.*?>", "", nameStr)
        #nameStr = nameStr.replace("&amp;", '&')
        labelStart = nameStr.rfind('(')
        if labelStart > 0:
            self.review.label = nameStr[labelStart+1:-1]

        parts = nameStr[:(labelStart-1)].split('- ')
        if len(parts) == 1:
            parts = nameStr[:(labelStart-1)].split(' -')
        if len(parts) == 1:
            parts = nameStr[:(labelStart-1)].split(': ')

        if len(parts) == 1:
            self.review.name = parts[0]
        elif len(parts) > 1:
            self.review.artistCredit = parts[0].strip()
            self.review.name = parts[1].strip()
            if len(parts) > 2:
                self.review.name += ' - ' + parts[2]

    ###
    # Parses a paragraph that we are expecting to be a 'review'
    # This can be called multiple times (because sometimes we get newlines in the middle of a review).  Multiples lines
    # are appended together.
    ###
    def parseReviewString(self, reviewStr):
        if self.review.review is None:
            self.review.review = reviewStr
        else:
            self.review.review += ' ' + reviewStr

        sentences = reviewStr.split('.')
        tl = None
        rb = None
        if len(sentences) > 1:
            rb = sentences[-1].strip()
            if rb.startswith('-'):
                rm = self.reReviewer.findall(rb)
                if len(rm) > 0:
                    self.review.reviewedBy = rm[0]
            elif rb.startswith('Try'):
                parts = rb.split('-')
                if len(parts) > 1:
                    tl = parts[0]
                    rm = self.reReviewer.findall(rb)
                    if len(rm) > 0:
                        self.review.reviewedBy = rm[0]
            else:
                rb = None

        if tl is None and len(sentences) > 2:
            tl = sentences[-2].strip()
        if (not (tl is None)) and tl.startswith('Try'):
            self.review.trackList = tl

            self.review.tracks = []
            rawTracks = self.reTrackSplit.split(self.review.trackList)
            for t in rawTracks:
                track = Track(t)
                self.review.tracks.append(track)
                if track.stars == 3:
                    self.review.threeStarTracks.append(track)
                elif track.stars == 2:
                    self.review.twoStarTracks.append(track)
                else:
                    self.review.oneStarTracks.append(track)

###
# Word document parser
###
class DocParser:
    def __init__(self, filename):
        self.filename = filename
        self.reviews = []

    def process(self):
        DocParser.processFile(self.filename, self.reviews)
        return self.reviews

    def exportAlbums(self, targetFilename):
        file = open(targetFilename, "w", encoding='utf-8')
        sortedAlbums = sorted(self.reviews, key=operator.attrgetter('filename', 'rotation', 'name'))
        for a in sortedAlbums:
            s = a.formatCSV()
            file.write(s)
            file.write('\n')
        file.close()

    @staticmethod
    def processFile(filename, reviews):
        style_map = "u => em"

        with open(filename, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file, style_map=style_map)
            html = result.value # The generated HTML
            paras = html.split('<p>')
            currentRotation = None

            parsedReview = None
            lastParsedReview = None

            for p in paras:
                s = p[:-4].strip()
                #s = s.replace(u'\xa0', ' ').replace(u'\u2013', '-')
                s = unicodedata.normalize('NFKC', s).replace(u'\u2013', '-')
                if len(s) > 0 and s[0] != '<':
                    if len(s) > 0:
                        if len(s) < 10:
                            s = s[:-1].rstrip()
                            if s=='H' or s=='M' or s=='L' or s=='R/N':
                                currentRotation = s
                                albumName = None
                                albumReview = None
                                waitingForAlbum = True
                        else:
                            if parsedReview is None:
                                if ReviewParser.isNameString(s):
                                    parsedReview = ReviewParser(filename, currentRotation)
                                    parsedReview.parseNameString(s)
                                    lastParsedReview = None
                                elif not (lastParsedReview is None):
                                    # did somebody put a newline in the middle of a review? Try to add it to the last parsedReview
                                    lastParsedReview.parseReviewString(s)
                            else:
                                parsedReview.parseReviewString(s)
                                reviews.append(parsedReview.review)
                                lastParsedReview = parsedReview
                                parsedReview = None

class CSVFile:
    @staticmethod
    def parseLine(csvParts):
        review = None
        if csvParts is not None:
            if len(csvParts) > 1:
                review = Review()
                #header = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % ('Current Rotation', 'Review Title', 'Review', 'Dalet Review', 'Reviewed By', 'One Star', 'Two Star', 'Three Star', 'Filename', 'Artist Credit', 'Label')
                review.rotation = csvParts[0]
                review.name = csvParts[1]
                review.review = csvParts[2]
                review.daletReview = csvParts[3]
                review.reviewedBy = csvParts[4]
                review.filename = csvParts[8]
                review.artistCredit = csvParts[9]
                review.label = csvParts[10]
                review.mbID = csvParts[11].strip()
                review.oneStarTracks = csvParts[5].split(',')
                review.twoStarTracks = csvParts[6].split(',')
                review.threeStarTracks = csvParts[7].split(',')

        return review

    @staticmethod
    def readFile(filename):
        reviews = []
        f = open(filename, 'r')
        csvReader = csv.reader(open(filename, newline=''), delimiter='\t', quotechar='"')
        firstLine = True
        for line in csvReader:
            if not firstLine:
                review = CSVFile.parseLine(line)
                if review is not None:
                    reviews.append(review)
            else:
                firstLine = False
    
        return reviews

class DirectoryParser:
    def __init__(self, directoryPath):
        self.directoryPath = directoryPath
        self.reviews = []

    def process(self):
        path_start = len(self.directoryPath) + 1
        for root, dir, files in os.walk(self.directoryPath):
            if len(root) > path_start:
                path = root[path_start:]
            else:
                path = ''
            for src_name in files:
                if src_name[-4:].lower() == 'docx' and src_name[:1] != '~':
                    file_name = os.path.join(root, src_name)
                    print(src_name)
                    DocParser.processFile(file_name, self.reviews)
        return self.reviews