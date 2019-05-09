import re

track = "track"
release = "release"
artist = "artist"
barcode = "barcode"

meta_pattern = re.compile('\s*((?P<' + track + '>(((\d+((,)|(\s))*)+)|(\s*all)))|(?P<' + release + '>(r(elease)?)))\s*')

kexp = "kexp"
standard = "standard"

yellow = "yellow"
red = "red"
clean = "clean"

prev = "prev"
next = "next"
jump = "jump"

quit = "quit"
help = "help"
edit = "edit"

mb_add = "add release"

mb = "mb"
albunack = "albunack"

tracknum_acc = "track_num"
meta_acc = "meta"

mb_add_pattern = re.compile('add release')

secondary_genre_pattern = re.compile('g|genre\s+(?P<' + meta_acc + '>.+)')
track_num_pattern = re.compile('((((?P<start>(\\d+))\\s*-\\s*(?P<end>(\\d+)))|(?P<single>\\d+))\s*,*\s*|(?P<all>all))')
track_meta_pattern = re.compile('\s*(?P<' + tracknum_acc + '>(\s*' + track_num_pattern.pattern + '\s*)+)(?P<' + meta_acc + '>.+)')

nav_pattern = re.compile("\s*((?P<" + prev + ">\s*p(rev)?)|(?P<" + next + ">\s*n(ext)?))\s*(?P<" + jump + ">(\d+)?)", flags=re.I)
popup_pattern = re.compile("\s*((?P<" + quit + ">\s*(q+(uit)?))|(?P<" + help + ">\s*(\?+)|h(elp)?)|(?P<" + edit + ">\s*(e((nter)|(ntry)|(dit))?)))\s*", flags=re.I)

# unknown artist input pattern:
unknown_artist = re.compile("unknown artist|^\s*$", flags=re.I)

release_pattern = re.compile("\d+ -.*")

# patterns to choose which track metadata to change

# change obscenity rating pattern
radio_edit = re.compile("\s*((?P<" + kexp + ">(kd)|(kexp radio( edit?)))|(?P<" + standard + ">(d+)|(radio( edit)?)))", flags=re.I)
obscenity_rating = re.compile("\s*((?P<" + yellow + ">y+)|(?P<" + red + ">r+)|(?P<" + kexp + ">(kc|kexp clean( edit)?))|(?P<" + standard + ">(c+|clean( edit)?)))", flags=re.I)
rm_rating = re.compile("\s*(l|clear)", flags=re.I)
mb_search_pattern = re.compile("\s*((?P<" + mb + ">s+(earch)?)|(?P<" + albunack + ">((albunack|al)(\s|$))))(\s*(?P<" + barcode + ">bar)?(\"(?P<" + artist + ">.+)\")?)", flags=re.I)
barcode_search_pattern = re.compile("\s*bar\s*(?P<" + barcode + ">.+)?")
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
