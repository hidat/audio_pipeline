from audio_pipeline import Constants
import yaml
import re

# track_number_pattern = re.compile()
separator_pattern = re.compile('(,|\s+)\s*')
commands = []


# TB Commands
class Option:
    def __init__(self, command, alias=None):
        self.command = command
        self.alias = alias


class Command:
    def __init__(self, command, aliases=None, options=None, command_help=None, examples=None):
        self.command = command
        self.aliases = []
        self.aliases = aliases
        self.options = []
        if options:
            for option in options:
                self.options.append(Option(**option))
        self.command_help = command_help
        self.examples = examples


# Build TB commands
def build_commands():
    with open(Constants.config_file) as f:
        config = yaml.load(f)
    if "tb_meta" in config:
        if "release" in config["tb_meta"]:
            global commands
            for release_command in config["tb_meta"]["release"]:
                commands.append(Command(**release_command))


def check_command(input_string):
    for command in commands:
        tag_name = None
        tag_value = None
        for option in command.options:
            if option.alias:
                aliases = '(' + option.command + '|' + option.alias + ')'
            else:
                aliases = '(' + option.command + ')'
            option = option.command
            matchee = '(' + separator_pattern.pattern + ')' + aliases + '(' \
                      + separator_pattern.pattern + '|$)'
            match = re.search(matchee, input_string, flags=re.I)
            if match:
                input_string = re.sub(match.group(0), "", input_string)
                tag_value = option
        aliases = [alias for alias in command.aliases]
        aliases.append(command.command)
        aliases = '(' + "|".join(aliases) + ')'
        matchee = '(' + separator_pattern.pattern + ')*' + aliases + '$'
        if re.search(matchee, input_string, flags=re.I):
            tag_name = command.command

        if tag_name:
            return tag_name, tag_value
    return None, None