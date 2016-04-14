from .. import InputPatterns

class Command:
    def __init__(self, command, help, examples=[]):
        self.command = command
        self.help = help
        self.examples = examples


bg_color = "black"
text_color = "light gray"
yellow = "yellow"
red = "red"
blue = "cyan"
heading = ('Helvetica', '10', 'bold')
standard = ('Helvetica', '10')
initial_size = (500, 500)

commands = [Command("<track_num>[[,][ ]<track_num>...][ ]<meta_command>", "Add the metadata specified by <meta_command> to track <track_num>. <meta_command> is not case-sensitive.\
              \nMultiple <track_nums> may be specified, separated by \",\" and/or \" \"\
              \nValid <meta_command>s:\n\tr[ed[ dot]]: RED DOT obscenity rating\
              \n\ty[ellow[ dot]]: YELLOW DOT obscenity rating\n\tc[lear]: Remove obscenity rating", 
              ["<track_num><meta_command>: 7y: Add YELLOW DOT obscenity rating to track 7 of the current album."]),
              Command("d[one]", "Close this application."),
              Command("n[ext]", "Display metadata of next album"),
              Command("p[[rev]ious]", "Display metadata of previous album")]

def get_text_color(audio_file):
    color = text_color
    if audio_file.kexp.obscenity.value:
        if InputPatterns.yellow_dot.match(audio_file.kexp.obscenity.value):
            color = yellow
        elif InputPatterns.red_dot.match(audio_file.kexp.obscenity.value):
            color = red
        elif InputPatterns.clean_edit.match(audio_file.kexp.obscenity.value):
            color = blue
    return color