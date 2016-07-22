import smartsheet
import unicodedata

####
# Smartsheet Release
# Holds the information for a single row from the smartsheet.
# Knows the column ordering of the smartsheet, so we can copy the values from the 'cells' array into the class
####
class SSRelease:
    def __init__(self, cells):
        self.title = cells[3].value
        self.normalizedTitle = unicodedata.normalize('NFKC', self.title).replace(u'\u2013', '-').casefold()
        self.artist = cells[2].value
        self.normalizedArtist = unicodedata.normalize('NFKC', self.artist).replace(u'\u2013', '-').casefold()
        self.rotation = cells[1].value
        self.obscenityRating = cells[6].value
        self.mbID = cells[9].value
        self.daletGlossaryName = cells[10].value
        self.tracks = None

####
# Very simple wrapper around the Smartsheet SDK used to read the contents of a sheet that is assumed to be our weekly release sheet
####
class SDK:
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.sdk = smartsheet.Smartsheet(apiKey)

    def readWeeklySheet(self, sheetId):
        releases = []
        sheet = self.sdk.Sheets.get_sheet(sheetId)
        for r in sheet.rows:
            releases.append(SSRelease(r.cells))
        return releases
