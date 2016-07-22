import re

###
# Review Track
###
class ReviewTrack:
    reNumberExtract = re.compile(r"(\d+)")

    def __init__(self, rawTrack):
        self.rawTrack = rawTrack
        self.stars = 1
        self.title = None
        self.itemCode = None
        self.title = None

        m = self.reNumberExtract.search(rawTrack)

        if m:
            self.trackNum = m.group(0)
        else:
            self.trackNum = None

        if "<em>" in rawTrack:
            self.stars +=1
        if "<strong>" in rawTrack:
            self.stars += 1
