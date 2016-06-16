from audio_pipeline.tb_ui.controller import MetaControl
import argparse
import configparser
import os
from audio_pipeline import util


config_defaults = {"audiofile": ""}

def main():
    parser = argparse.ArgumentParser(description="Tag audio files with metadata")
    parser.add_argument('-d', '--release_directory', default=None, help="Directory containing release directories to be processed")
    parser.add_argument('-c', '--copy', default=None, help="Specify a directory to copy files to.")
    args = parser.parse_args()
 
    config_file = os.path.join(os.path.split(__file__)[0], "TBConfiguration.ini") 
    config(config_file)
    
    controller = MetaControl.MetaController(args.release_directory, args.copy)
    
    controller.app.mainloop()

    
def config(config_file):
    config = configparser.ConfigParser(allow_no_value=True)
    
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        # create / write new config file
        config['DEFAULT'] = config_defaults
        
    if "USER" not in config:
        config["USER"] = {}
                     
    # write configuration
    with open(config_file, 'w+') as c_file:
        config.write(c_file)
            
    # set batch constants from config file
    settings = config["USER"]
        
    # set AudioFile from config file
    util.AudioFileFactory.AudioFileFactory.set(settings.get("audiofile"))

if __name__ == "__main__":
    main()