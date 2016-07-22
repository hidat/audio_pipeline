import re
import difflib

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

track_num_pattern = re.compile('(((?P<start>(\\d+))\\s*-\\s*(?P<end>(\\d+)))|(?P<single>\\d+)|(?P<all>all))')

#track_meta_pattern = re.compile('(?P<red>r+(ed)?)|(?P<yellow>y+(ellow)?)|(?P<clean>clear|l+)|(?P<clean>c+(lear))')

track_meta_pattern = re.compile('\s*(?P<' + tracknum_acc + '>(\s*' + track_num_pattern.pattern + '\s*)+)(?P<' + meta_acc + '>.+)')

nav_pattern = re.compile("\s*((?P<" + prev + ">\s*p(rev)?)|(?P<" + next + ">\s*n(ext)?))\s*(?P<" + jump + ">(\d+)?)", flags=re.I)
popup_pattern = re.compile("\s*((?P<" + quit + ">\s*(d+(one)?)|(q+(uit)?))|(?P<" + help + ">\s*(\?+)|h(elp)?)|(?P<" + edit + ">\s*((e((nter)|(ntry)|(dit))?)|(m(eta)?))))\s*", flags=re.I)

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


def get_track_numbers(user_input):
    tracks = []
    results = track_num_pattern.search(user_input)
    while results is not None:
        if results.group("start"):
            for i in range(int(results.group("start")), int(results.group("end")) + 1):
                tracks.append(i)
        elif results.group("single"):
            tracks.append(int(results.group("single")))
        else:
            tracks.append("all")
        user_input = user_input[results.end():]
        results = track_num_pattern.search(user_input)
    return tracks
