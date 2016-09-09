from ..util import InputPatterns

class Command:
    def __init__(self, command, help, sub_commands=None, examples=[]):
        self.command = command
        self.help = help
        self.sub_commands = sub_commands
        self.examples = examples


class SubCommand:
    def __init__(self, name, commands):
        self.name = name
        self.commands = commands


bg_color = "black"
text_color = "light gray"
yellow = "yellow"
red = "red"
blue = "cyan"
heading = ('Helvetica', '10', 'bold')
standard = ('Helvetica', '10')
command = ('Courier New', '10', 'bold')
initial_size = (500, 500)

active_fg = "black"
active_bg = "white"

obscenity_rating_commands = SubCommand("Valid <meta_command>s:", [Command("red dot, red, r", "RED DOT obscenity rating"),
                             Command("yellow dot, yellow, y", "YELLOW DOT obscenity rating"),
                             Command("clean edit, clean, c", "CLEAN EDIT obscenity rating"),
                             Command("kexp clean, kc", "Set obscenity rating to KEXP CLEAN EDIT"),
                             Command("clear, l", "Remove obscenity rating"),
                             Command("radio edit, d", "Set radio edit value to RADIO EDIT"),
                             Command("kexp radio edit, kd", "Set radio edit value to KEXP RADIO EDIT")])

search_options = [Command("\"<artist_name>\"", "Search for artist by specified artist name instead of artist name in meta"),
                  Command("bar", "Search for release by carcode/catalog number")]
                  
commands = [Command("<track_num>[[,][ ]<track_num>...][ ]<meta_command>", "Add the metadata specified by <meta_command> to track <track_num>.<meta_command> is not case-sensitive.\
              \nMultiple <track_nums> may be specified, separated by \",\" and/or \" \"", sub_commands=obscenity_rating_commands,
              examples = ["7y: Add YELLOW DOT obscenity rating to track 7 of the current album."]),
              Command("quit, q", "Close this application."),
              Command("next, n", "Display metadata of next album"),
              Command("previous, prev, p", "Display metadata of previous album"),
              Command("edit, e", "Edit all metadata categories with the Metadata Input Friend"),
              Command("search, s <option>", "Search for MusicBrainz release in browser.", sub_commands=SubCommand("Options", search_options)),
              Command("bar <barcode or catno>", "Search by barcode/catno. If no barcode or catalog number is entered, will search for "
                                                "barcode / catalog number in metadata."),
              Command("albunack, al <option>", "Search for artist in Albunack (in browser).", sub_commands=SubCommand("Options", search_options[:1])),
              Command("g <genre name>", "Set KEXPSecondaryGenre of current release to <genre name>")]

def get_text_color(audio_file):
    color = text_color
    
    try:
        if audio_file.obscenity.value:
            obscenity = InputPatterns.obscenity_rating.match(audio_file.obscenity.value)
            if obscenity.group(InputPatterns.yellow):
                color = yellow
            elif obscenity.group(InputPatterns.red):
                color = red
            elif obscenity.group(InputPatterns.kexp) or obscenity.group(InputPatterns.standard):
                color = blue
    except AttributeError:
        pass
        
    return color