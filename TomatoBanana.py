from audio_pipeline import Constants
from audio_pipeline.tb_ui.controller import TBController

import argparse
import os

config_defaults = {"audiofile": ""}

def main():
    parser = argparse.ArgumentParser(description="Tag audio files with metadata")
    parser.add_argument('-d', '--release_directory', default=None, help="Directory containing release directories to be processed")
    parser.add_argument('-c', '--copy', default=None, help="Specify a directory to copy files to.")
    args = parser.parse_args()

    config_dir = os.path.split(os.path.abspath(__file__))[0]

    Constants.load_config(config_dir)
    Constants.is_tb = True

    controller = TBController.TBController(args.release_directory, args.copy)
    
    controller.app.mainloop()


if __name__ == "__main__":
    main()