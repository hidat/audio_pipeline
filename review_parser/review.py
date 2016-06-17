import re
import html


class Review:

    def __init__(self):
        self.filename = None
        self.rotation = None
        self.mbID = None
        self.name = None
        self.artistCredit = None
        self.label = None
        self.review = None
        self.trackList = None
        self.tracks = None
        self.reviewedBy = ''
        self.oneStarTracks = []
        self.twoStarTracks = []
        self.threeStarTracks = []

    def print(self):
        print("\n%s: %s by [%s] (on %s) - %s" %(self.rotation, self.name, self.artistCredit, self.label, self.review))
        print("Reviewed by: %s.  Tracks to try: %s" % (self.reviewedBy, self.trackList))
        for t in self.tracks:
            print("%s: %d" % (t.trackNum, t.stars))

    def formatCSV(self):
        oneStar = ''
        for t in self.oneStarTracks:
            if not (t.trackNum is None):
                if oneStar > '':
                    oneStar += ', '
                oneStar += str(t.trackNum)

        twoStar = ''
        for t in self.twoStarTracks:
            if not (t.trackNum is None):
                if twoStar > '':
                    twoStar += ', '
                twoStar += str(t.trackNum)

        threeStar = ''
        for t in self.threeStarTracks:
            if not (t.trackNum is None):
                if threeStar > '':
                    threeStar += ', '
                threeStar += str(t.trackNum)

        decodedReview = html.unescape(self.review)
        textReview = re.sub("<.*?>", "", decodedReview)
        decodedReview = decodedReview.replace("em>", "u>").replace("strong>", "b>")
        #Let xml encoder take care of it
        #encodedReview = html.escape(decodedReview, False)
        s = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.rotation, self.name, textReview, decodedReview, self.reviewedBy, oneStar, twoStar, threeStar, self.filename, self.artistCredit, self.label)
        return s
