import re

track = "track"
release = "release"

meta_pattern = re.compile('\s*((?P<' + track + '>(((\d+((,)|(\s))*)+)|(\s*all)))|(?P<' + release + '>(r(elease)?)))\s*')

tracknum_acc = "track_num"
meta_acc = "meta"

artist = "artist"
album = "album"
num = "num"
mbid = "mbid"
date = "date"
length = "length"
title = "title"
obscenity = "obscenity"


track_meta_pattern = re.compile('\s*(?P<' + tracknum_acc + '>(((\d+((,)|(\s))*)+)|(\s*all)))\s*(?P<' + meta_acc + '>.+)')

prev_pattern = re.compile("\s*p(rev)?.*", flags=re.I)
next_pattern = re.compile("\s*n(ext)?", flags=re.I)
done_pattern = re.compile("\s*d+(one)?", flags=re.I)
help_pattern = re.compile("\s*(\?+)|h(elp)?", flags=re.I)
entry_pattern = re.compile("\s*e((nter)|(ntry)|(dit))|m(eta)?")
rm_rating = re.compile("\s*c(lear)?", flags=re.I)

# patterns to choose which track metadata to change

# change obscenity rating pattern
yellow_dot = re.compile("\s*y(ellow)?\s*(dot)?", flags=re.I)
red_dot = re.compile("\s*r(ed)?\s*(dot)?", flags=re.I)
clean_edit = re.compile("\s*c(lean)?\s*(edit)?", flags=re.I)

whitespace = re.compile("\s+")