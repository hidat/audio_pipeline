import review_parser.mb_release as mb

releases = mb.readReleaseLog('releases.json')
if releases is not None:
    print("%d releases read" % len(releases))
else:
    print("No releases read!")

