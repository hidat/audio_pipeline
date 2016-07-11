import re

track = "track"
release = "release"

meta_pattern = re.compile('\s*((?P<' + track + '>(((\d+((,)|(\s))*)+)|(\s*all)))|(?P<' + release + '>(r(elease)?)))\s*')

prev = "prev"
next = "next"
jump = "jump"

quit = "quit"
help = "help"
edit = "edit"

forward = "forward"
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

release_meta_pattern = re.compile('\s*r(elease)?', flags=re.I)

track_meta_pattern = re.compile('\s*(?P<' + tracknum_acc + '>(((\d+((,)|(\s))*)+)|(\s*all)))\s*(?P<' + meta_acc + '>.+)')

tag_pattern = re.compile('\s*(?P<' + artist + '>(a(rtist)?))|(?P<' + album + '>)(album)|(n(ame)?)| \
                          (?P<' + num + '>(track|disc))|(?P<' + mbid + '>(m(bid)?))| \
                          (?P<' + date + '>(d(ate)?))|(?P<' + length + '>(l(ength?)))| \
                          (?P<' + title + '>(t(itle)?))(?P<' + obscenity + '>(o(bscenity)?))', flags=re.I)

nav_pattern = re.compile("\s*(((?P<" + prev + ">\s*p(rev)?))|((?P<" + next + ">\s*n(ext)?)))\s*(?P<" + jump + ">(\d+)?)", flags=re.I)
popup_pattern = re.compile("\s*(((?P<" + quit + ">\s*(d+(one)?)|(q+(uit)?)))|((?P<" + help + ">\s*(\?+)|h(elp)?))|((?P<" + edit + ">\s*((e((nter)|(ntry)|(dit))?)|(m(eta)?)))))\s*", flags=re.I)

# unknown artist input pattern:
unknown_artist = re.compile("unknown artist|^\s*$", flags=re.I)

release_pattern = re.compile("\d+ -.*")

# patterns to choose which track metadata to change

# change obscenity rating pattern
radio_edit = re.compile("\s*r", flags=re.I)
kexp_radio_edit = re.compile("\s*k", flags=re.I)
yellow_dot = re.compile("\s*y(ellow)?\s*(dot)?", flags=re.I)
red_dot = re.compile("\s*r(ed)?\s*(dot)?", flags=re.I)
clean_edit = re.compile("\s*s*c(lean)?\s*(edit)?\s*", flags=re.I)
rm_rating = re.compile("\s*(l|clear)", flags=re.I)

whitespace = re.compile("^\s+$")