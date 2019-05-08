from audio_pipeline import Constants
from . import controller
from . import model
from . import view
import yaml
import re
import urllib
import webbrowser
import tempfile
import os
import time

min_width = 120 * 8
min_height = 85 * 8


tag_command_help = "All tags can be cleared by entering \"<TAG NAME> clear\". Tags with no defined options can be toggled on/off."
separator_pattern = re.compile('(,|\s+)\s*')
span = re.compile("(\d+)(\s*-\s*)(\d+)")
tracknum_pattern = re.compile("(?<=,|\s)\d+|\d+(?=,|\s)")
clear_pattern = "clear"
release_tags = []
track_tags = []
clear_track = []
general_commands = []

__nav_commands = []
open_editor = None
close_command = None

default_release_width = 15
default_track_width = 25

bg_color = "black"
text_color = "light gray"
yellow = "yellow"
red = "red"
blue = "cyan"
heading = ('Helvetica', '10', 'bold')
standard = ('Helvetica', '10')
action = ('Courier New', '10', 'bold')
initial_size = (500, 500)


##########################
#   Utilities for TomatoBanana
##########################

def get_text_color(audio_file):
    color = text_color

    for com in track_tags:
        for option in com.options:
            if option.color and option.command.casefold() == str(audio_file.track_tags[com.command]).casefold():
                color = option.color
    return color

###################
# search and stuff
###################
class WebBrowserAssist:
    mb_release = "http://musicbrainz.org/add"
    albunack_search_terms = {"artistname": "", "musicbrainzartistid": "", "musicbrainzartistdbid": "", "discogsartistid": ""}    
    mb_search_terms = {"type": "", "method": "advanced"}

    @staticmethod
    def prep_query(query):
        prepped_query = []
        for part in query:
            if len(part) > 1:
                q = "%s:\"%s\"" % (part[0], part[1])
            else:
                q = part[0]
            q = urllib.parse.quote_plus(q)
            prepped_query.append(q)

        return " ".join(prepped_query)  
    
    @staticmethod
    def mb_release_seed(release_seed):
        fd, fname = tempfile.mkstemp(suffix = '.html')
        os.close(fd)
        with open(fname, "wb") as f:
            f.write(release_seed.encode('utf-8'))
        webbrowser.open(fname)
        return fname
    
    @staticmethod
    def albunack_search(track, url_base, artist=None):
        """
        Given an audiofile, open an albunack artist search in the browser
        :param self:
        :param track:
        :return:
        """
        search_terms = None
        if artist:
            search_terms = WebBrowserAssist.albunack_search_terms.copy()
            search_terms["artistname"] = artist
        elif track.artist.value:
            search_terms = albunack_search_terms.copy()
            search_terms["artistname"] = track.album_artist.value
        if search_terms:
            search_terms = urllib.parse.urlencode(search_terms)
            search_url = url_base + search_terms
            webbrowser.open(search_url)
    
    @staticmethod
    def mb_barcode_search(track, url_base, barcode_value=None):
        """
        Given an audiofile, open an MB search for the barcode in the browser
        """
        query = []
        search_terms = WebBrowserAssist.mb_search_terms.copy()
        search_terms["type"] = "release"
        
        if barcode_value:
            query.append(("barcode", barcode_value))
            query.append(("catno", barcode_value))
        else:
            if track.barcode.value:
                query.append(("barcode", track.barcode.value))
            if track.catalog_num.value:
                query.append(("catno", track.catalog_num.value))
    
        if search_terms and len(query) > 0:
            query = WebBrowserAssist.prep_query(query)
            search_terms = urllib.parse.urlencode(search_terms)
            search_url = "%s%s&%s" % (url_base, query, search_terms)
            webbrowser.open(search_url)

    @staticmethod
    def mb_search(track, url_base, artist=None):
        """
        Given an audiofile, open an MB search in the browser
    
        search priorities:
            barcode and/or catalog number
            release name and/or artist name
        :param self:
        :param track:
        :return:
        """
        query = []
        if artist:
            search_terms = WebBrowserAssist.mb_search_terms.copy()
            search_terms["type"] = "artist"
    
            query.append((artist,))
        else:
            search_terms = WebBrowserAssist.mb_search_terms.copy()
            if track.album.value:
                search_terms["type"] = "release"
                query.append((track.album.value,))
                if track.album_artist.value:
                    query.append(("artist", track.album_artist.value))
            else:
                search_terms["type"] = "artist"
                if track.album_artist.value:
                    query.append((track.album_artist.value,))
    
        if search_terms and len(query) > 0:
            query = WebBrowserAssist.prep_query(query)
            search_terms = urllib.parse.urlencode(search_terms)
            search_url = "%s%s&%s" % (url_base, query, search_terms)
            webbrowser.open(search_url)
            
#######################
# TB Commands
#######################
class Option:
    def __init__(self, command, aliases=None, color=None, description=None):
        self.command = command
        if aliases:
            self.aliases = aliases
        else:
            self.aliases = []
        self.color = color
        self.description = description
        self.freeform = False
        
        if self.command.startswith("<") and self.command.endswith(">"):
            build_re = '^(' + separator_pattern.pattern + ')*(.+?)(' + separator_pattern.pattern + '|$)'
            self.regex_match = re.compile(build_re)
            self.freeform = True
        elif self.command.startswith("\"<") and self.command.endswith(">\""): 
            build_re = '^(' + separator_pattern.pattern + ')*"(.+?)"(' + separator_pattern.pattern + '|$)'
            self.regex_match = re.compile(build_re)
            self.freeform = True
        else:
            build_re = [alias for alias in self.aliases]
            build_re.append(self.command)
            build_re = '^(' + separator_pattern.pattern + ')*(' + "|".join(build_re) + ')(' + separator_pattern.pattern + '|$)'
            self.regex_match = re.compile(build_re, flags=re.I)
        
    def full_option(self):
        full_command = ", ".join([self.command.casefold()] + [alias.casefold() for alias in self.aliases])
        return full_command
    
    def match(self, input_string):
        match = self.regex_match.match(input_string)
        if match:
            match_string = re.sub(match.group(0), "", input_string)
            if self.freeform:
                return match.group(0), match_string
            else:
                return self.command, match_string
        return None, input_string


class Command:
    def __init__(self, tag=None, command=None, display_name=None, aliases=None, options=None, freeform=False, 
                 description=None, examples=None, track=None, url_base=None, active=True):
        if tag:
            self.command = tag
        elif command:
            self.command = command
        else:
            self.command = None
        self.aliases = []
        if aliases:
            self.aliases = aliases
        self.options = []
        self.freeform = freeform
        self.display_name = display_name
        if not display_name:
            self.display_name = self.command
        self.description = description
        if options:
            for option in options:
                self.options.append(Option(**option))
        self.examples = examples
        self.active = active
        
        if self.freeform and not self.description:
            self.description = "Accepts any input as a valid tag value."
        elif not self.options and not self.description:
            self.description = "This is a true/false tag that is toggled with each command entry."
        
        
    def full_command(self):
        full_command = ", ".join([self.command.casefold()] + [alias.casefold() for alias in self.aliases])
        return full_command
    
    def _match(self, input_string):
        # check if there is a match for this command at start of string
        aliases = [alias for alias in self.aliases]
        aliases.append(self.command)
        if self.display_name:
            aliases.append(self.display_name)
        aliases = '(' + "|".join(aliases) + ')'
        matchee = '^(' + separator_pattern.pattern + ')*' + aliases + '(' + separator_pattern.pattern + '|$)'
        match = re.search(matchee, input_string, flags=re.I)
        
        if match:
            # if there is a command name match, strip command name from string & return what remains
            match_string = re.sub(match.group(0), "", input_string)
            return self.command, match_string
        return None, input_string
        
    def execute(self, input_string, tb_model=None):
        # check if we match this command's name
        command_name, input_string = self._match(input_string)
                
        if not command_name:
            return None, None
                
        # perform the command - base execution is for a release tag
        matchee = '^(' + separator_pattern.pattern + ')*' + clear_pattern + '(' + separator_pattern.pattern + '|$)'
        match = re.search(matchee, input_string, flags=re.I)
        if match:
            tag_value = None
        else:
            # check if we match one of the command's defined options
            tag_value = None
            for option in self.options:
                tag_value, input_string = option.match(input_string)
                if tag_value:
                    break
            if input_string:
                if self.freeform and not tag_value:
                    tag_value = input_string
                else:
                    command_name = None
                    tag_value = False
            elif not self.options:
                tag_value = True
                
        return command_name, tag_value
    
    
class TrackCommand(Command):
    def _match(self, input_string, tb_model=None):
        command_name, input_string = super()._match(input_string)
        
        if self.options:
            command_name = self.command
        
        return command_name, input_string
    
    
class ClearTrack(Command):
    def execute(self, input_string, tb_model=None):
        # check if we match this command's name
        command_name, input_string = self._match(input_string)

        return command_name


class NavigationCommand(Command):
    
    def __init__(self, base_distance=0, **kwargs):
        self.base_distance = base_distance
        
        super().__init__(**kwargs)
    
    def execute(self, input_string, tb_model=None):
        command_name, input_string = self._match(input_string)
        
        if command_name:
            distance = self.base_distance
            jump = re.search(separator_pattern.pattern + '(?P<jump>(\d+))', input_string)
            if jump:
                distance *= int(match.group("jump"))
            return distance
        

class MusicBrainzSeedCommand(Command):
    
    def __init__(self, url_base=None, **kwargs):
        self.seeder_file = set()
        self.url_base = url_base
        super().__init__(**kwargs)
        
    def execute(self, input_string, tb_model=None):
        if not model:
            return
        command_name, input_string = self._match(input_string)
        
        if command_name:
            # generate a release seed HTML file and open the MusicBrainz add release page
            release_seed = tb_model.get_release_seed(self.url_base)
            self.seeder_file.add(WebBrowserAssist.mb_release_seed(release_seed))
            time.sleep(1.5)
            deleted = set()
            for fname in self.seeder_file:
                try:
                    os.remove(fname)
                    deleted.add(fname)
                except PermissionError:
                    print("Can't close this file")
            for fname in deleted:
                self.seeder_file.remove(fname)
            return True
                
        
class GetDiscogsMetaCommand(Command):

    def execute(self, input_string, model):
        match, input_string = self._match(input_string)
        if match:
            matchee = '(' + separator_pattern.pattern + ')*(?P<id>\d+)(' + separator_pattern.pattern + '|$)'
            match = re.search(matchee, input_string, flags=re.I)
        
            if match:
                complete = model.set_discogs(match.group("id"))
                print(complete)
                return complete


class SearchCommand(Command):
    search_executors = {
        
            "albunack_search": WebBrowserAssist.albunack_search,
            "mb_search": WebBrowserAssist.mb_search,
            "mb_barcode": WebBrowserAssist.mb_barcode_search
        }  
    
    def __init__(self, search_type=None, url_base=None, **kwargs):
        self.url_base = url_base
            
        self.search_execution = SearchCommand.search_executors[search_type]
        super().__init__(**kwargs)
        
    def execute(self, input_string, model):
        command_name, input_string = self._match(input_string)
        
        if command_name:
            for option in self.options:
                tag_value, input_string = option.match(input_string)
            self.search_execution(model.current_release[0], self.url_base, tag_value)
            return True
                        

def navigate(input_string):      
    for command in __nav_commands:
        distance = command.execute(input_string)
        if distance is not None:
            return distance
               
            
def set_destination():
    with open(Constants.config_file) as f:
        config = yaml.unsafe_load(f)
        if "destination folder" in config:
            return config["destination folder"]
        
        
def save_setting_changes():
    global release_tags, track_tags
    with open(Constants.config_file) as f:
        config = yaml.unsafe_load(f)
        config.update()


# Build TB commands
def build_commands():
    if 'default' in Constants.config_data:
        __build_commands__(Constants.config_data['default'])
        if 'default' in Constants.config_data['default']:
            __build_commands__(Constants.config_data[Constants.config_data['default']['default']])


# do the actual command creation    
def __build_commands__(config):
    if "tb_meta" in config:
        tb_meta = config["tb_meta"]
        if "release" in tb_meta:
            global release_tags
            for release_command in tb_meta["release"]:
                release_tags.append(Command(track=False, **release_command))
        if "track" in tb_meta:
            global track_tags
            for t_command in tb_meta["track"]:
                track_tags.append(TrackCommand(**t_command, track=True))
        global general_commands
        if "commands" in tb_meta:
            for command in tb_meta["commands"]:
                general_commands.append(Command(**command))
        if "release_seeder" in tb_meta:
            general_commands.append(MusicBrainzSeedCommand(**tb_meta["release_seeder"]))
        if "discogs" in tb_meta:
            general_commands.append(GetDiscogsMetaCommand(**tb_meta["discogs"]))
        if "search" in tb_meta:
            for search_type, command in tb_meta["search"].items():
                general_commands.append(SearchCommand(search_type, **command))
        if "navigation" in tb_meta:
            global __nav_commands
            for direction, command in tb_meta["navigation"].items():
                if direction == 'forward':
                    __nav_commands.append(NavigationCommand(base_distance=1, **command))
                if direction == 'backward':
                    __nav_commands.append(NavigationCommand(base_distance=-1, **command))
        if "close" in tb_meta:
            global close_command
            close_command = Command(**tb_meta["close"])
        if "editor" in tb_meta:
            global open_editor
            open_editor = Command(**tb_meta["editor"])
        if "clear_track" in tb_meta:
            global clear_track
            clear_track.append(ClearTrack(**tb_meta["clear_track"]))


def span_replacement(match):
    start = int(match.group(1))
    end = int(match.group(3)) + 1
    return ",".join([str(i) for i in range(start,end)])


def get_track_nums(input_string):
    # check that input starts with a track number or 'all'
    all = re.search("(^|\s|,)(all)(,|\s|-)", input_string, flags=re.I)
    start = re.match("\s*(\d+|all)(,|\s|-)", input_string, flags=re.I)
    if start:
        start = start.group(1).casefold()
        track_nums = {int(start) if start != "all" else start}

        # replace all "# - #" spans with appropriate #s
        find_tracks = span.sub(span_replacement, input_string)
        # return track numbers
        for i in tracknum_pattern.findall(find_tracks):
            track_nums.add(int(i))
            find_tracks = find_tracks.replace(i, "", 1)
            #find_tracks = separator_pattern.sub("", find_tracks, 1)

        if all:
            track_nums.add(all.group(2))
            find_tracks = find_tracks.replace("all", "", 1)

        return track_nums, find_tracks
    return None, input_string
    

__all__ = ['controller', 'model', 'view']