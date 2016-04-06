import re


tracknum_acc = "track_num"
meta_acc = "meta"

track_meta_pattern = re.compile('\s*(?P<' + tracknum_acc + '>(((\d+((,)|(\s))*)+)|(\s*all)))\s*(?P<' + meta_acc + '>.+)')

prev_pattern = re.compile("\s*p(rev)?.*", flags=re.I)
next_pattern = re.compile("\s*n(ext)?", flags=re.I)
done_pattern = re.compile("\s*d+(one)?", flags=re.I)
help_pattern = re.compile("\s*(\?+)|h(elp)?", flags=re.I)
entry_pattern = re.compile("\s*e((nter)|(ntry)|(dit))|m(eta)?")
yellow_dot = re.compile("\s*y(ellow)?\s*(dot)?", flags=re.I)
red_dot = re.compile("\s*r(ed)?\s*(dot)?", flags=re.I)
rm_rating = re.compile("\s*c(lear)?", flags=re.I)

clean_edit = re.compile("\s*c(lean)?\s*(edit)?", flags=re.I)

whitespace = re.compile("\s+")