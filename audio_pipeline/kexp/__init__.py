def argument_config(parser):
    parser.add_argument('-c', '--category', type=str.casefold, metavar='',
                        choices=["recent acquisitions", "acq", "electronic", "ele", "experimental",
                        "exp", "hip hop", "hip", "jaz", "jazz", "live on kexp", "liv",
                        "local", "reggae", "reg", "rock", "pop", "rock/pop", "roc", "roots",
                        "roo", "rotation", "rot", "shows around town", "sho", "soundtracks",
                        "sou", "world", "wor"], help="Category or genre of releases being filewalked.")
    parser.add_argument('-s', '--source', type=str.casefold, metavar='',
                        choices=["cd library", "melly", "hitters"],
                        help="KEXPSource value - 'Melly', 'CD Library', or 'Hitters'")
    parser.add_argument('-r', '--rotation', type=str.casefold, metavar='',
                        choices=["heavy", "library", "light", "medium", "r/n"],
                        help="Rotation workflow value: \'heavy\', \'library\', \'light\', \'medium\' or \'r/n\'")
    parser.add_argument('--no_artist', default=False, const=True, nargs='?', help='Do not generate artist metadata XMLs')
    parser.add_argument('--radio_edit', type=str.casefold, choices=["Radio Edit", "KEXP Radio Edit"], help='Add specified radio edit to track XMLs')
    parser.add_argument('-a', '--anchor', default=False, const=True, nargs='?', help='Add anchor status to track XMLs')

    return parser
