import os


class Rule:
    def __init__(self, dest_dir):
        self.dest_dir = dest_dir
        self.forbidden = ["\\", "/", ":", "?", "*", "[", "]", ">", "<", "|", "\""]

    def clean_filename(self, name):
        for f in self.forbidden:
            name = name.replace(f, "")
        return name

    def get_dest(self, audiofile):
        pass


class RulePool(object):

    def __init__(self):
        self.rules = {}

    def register(self, rule):
        """
        Register the given rule
        Do some sanity checks
        Used to clean up .... things
        A design pattern absolutely aped from Django
        """
        if not issubclass(rule, Rule):
            raise IllegalArgumentException()
        rule_name = rule.name.casefold()
        if rule_name in self.rules:
            raise IllegalArgumentException()

        self.rules[rule_name] = rule

    def __getitem__(self, item):
        if item.casefold() in self.rules:
            print(self.rules[item.casefold()])
            return self.rules[item.casefold()]
        else:
            return None

rules = RulePool()

class FileUnderRule(Rule):
    name = "File Under"

    def get_dest(self, audiofile):
        if audiofile.file_under.value:
            # we're going to ignore casing
            layer_one = audiofile.file_under.value[:1].upper()
            layer_two = os.path.join(layer_one, audiofile.file_under.value.upper())
            directory = str(audiofile.album_artist) + " - " + self.clean_filename(str(audiofile.album))
            dest = os.path.join(layer_two, directory)
            return dest


class HasMBIDRule(Rule):
    name = "Has MBID"

    def __init__(self, dest_dir):
        super().__init__(dest_dir)
        self.picard_dir = "Picard Me"
        self.mbid_dir = "Has Necessary Metadata"

    def get_dest(self, audiofile):
        # get the name of the release directory
        directory = os.path.split(os.path.dirname(audiofile.file_name))[1]

        if audiofile.has_mbid():
            dest = os.path.join(self.mbid_dir, directory)
        else:
            dest = os.path.join(self.picard_dir, directory)

        return dest

rules.register(FileUnderRule)
rules.register(HasMBIDRule)
