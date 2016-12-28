from audio_pipeline import Constants
from . import controller
from . import model
from . import view
import yaml
import re
from pip import commands


# track_number_pattern = re.compile()
separator_pattern = re.compile('(,|\s+)\s*')
span = re.compile("(\d+)(\s*-\s*)(\d+)")
tracknum_pattern = re.compile("(?<=,|\s)\d+|\d+(?=,|\s)")
clear_pattern = "clear"
release_tags = []
track_tags = []
general_commands = []

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


def get_text_color(audio_file):
    color = text_color

    for com in track_tags:
        for option in com.options:
            if option.color and option.command.casefold() == str(audio_file.track_tags[com.command]).casefold():
                color = option.color
    return color


# TB Commands
class Option:
    def __init__(self, command, alias="", color=None, description=None):
        self.command = command
        self.alias = alias
        self.color = color
        self.description = description
        
    def full_option(self):
        if self.alias:
            full_option = ", ".join([self.command.casefold(), self.alias.casefold()])
        else:
            full_option = self.command.casefold()
            
        return full_option

class Command:
    def __init__(self, tag=None, command=None, display_name=None, aliases=None, options=None, freeform=False, 
                 description=None, examples=None, track=False):
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
        self.description = description
        if options:
            for option in options:
                self.options.append(Option(**option))
        self.examples = examples
        self.track = track
        
    def full_command(self):
        full_command = ", ".join([self.command.casefold()] + [alias.casefold() for alias in self.aliases])
        return full_command


def set_destination():
    with open(Constants.config_file) as f:
        config = yaml.load(f)
        if "destination folder" in config:
            return config["destination folder"]


# Build TB commands
def build_commands():
    if 'default' in Constants.config_data:
        __build_commands__(Constants.config_data['default'])
        if 'default' in Constants.config_data['default']:
            __build_commands__(Constants.config_data[Constants.config_data['default']['default']])


# do the actual command creation    
def __build_commands__(config):
    if "tb_meta" in config:
        if "release" in config["tb_meta"]:
            global release_tags
            for release_command in config["tb_meta"]["release"]:
                release_tags.append(Command(**release_command))
        if "track" in config["tb_meta"]:
            global track_tags
            for t_command in config["tb_meta"]["track"]:
                track_tags.append(Command(**t_command, track=True))
        if "commands" in config["tb_meta"]:
            global general_commands
            for command in config["tb_meta"]["commands"]:
                general_commands.append(Command(**command))


def check_command(input_string, commands):
    for command in commands:
        command_string = input_string

        tag_name = None
        tag_value = None

        # check if we have a match for this command at start of string
        aliases = [alias for alias in command.aliases]
        aliases.append(command.command)
        aliases = '(' + "|".join(aliases) + ')'
        matchee = '^(' + separator_pattern.pattern + ')*' + aliases + '(' + separator_pattern.pattern + '|$)'
        match = re.search(matchee, command_string, flags=re.I)

        if match:
            # if there is a command name match, strip command name from string
            tag_name = command.command
            command_string = re.sub(match.group(0), "", command_string)

        # if this command has options defined, check if we match one
        # check for clear command
        matchee = '^(' + separator_pattern.pattern + ')*' + clear_pattern + '(' + separator_pattern.pattern + '|$)'
        match = re.search(matchee, command_string, flags=re.I)
        if match:
            command_string = re.sub(match.group(0), "", command_string)
        else:
            # freeform tags
            for option in command.options:
                if option.alias:
                    aliases = '^(' + separator_pattern.pattern + ')*' + '(' + option.command + '|' + option.alias + ')'
                else:
                    aliases = '^(' + separator_pattern.pattern + ')*' + '(' + option.command + ')'
                option = option.command
                matchee = aliases + '(' + separator_pattern.pattern + '|$)'
                match = re.match(matchee, command_string, flags=re.I)
                if match:
                    command_string = re.sub(match.group(0), "", command_string)
                    tag_value = option
            if command_string and not separator_pattern.match(command_string):
                if command.freeform and not tag_value:
                    tag_value = command_string
                else:
                    tag_name = None
            elif not command.options:
                tag_value = True

        if tag_name or (command.track and command.options and tag_value):
            print(command_string)
            return command.command, tag_value
    return None, None


def check_release_tag(input_string):
    return check_command(input_string, release_tags)


def span_replacement(match):
    start = int(match.group(1))
    end = int(match.group(3)) + 1
    return ",".join([str(i) for i in range(start,end)])


def check_track_tag(input_string):
    # check that we're starting with a track number or 'all'
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
            print(all.group(2))
            track_nums.add(all.group(2))
            find_tracks = find_tracks.replace("all", "", 1)

        tag_name, tag_value = check_command(find_tracks, track_tags)
        return track_nums, tag_name, tag_value
    return None, None, None


__all__ = ['controller', 'model', 'view']