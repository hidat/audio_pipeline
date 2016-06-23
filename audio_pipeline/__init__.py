import audio_pipeline.file_walker.Resources
import audio_pipeline.util
import audio_pipeline.file_walker.Process
import audio_pipeline.serializers

import os
import yaml


batch_constants_def = None
batch_constants = None

config_dir = ""
audiofile = None
processor = None
serializer = None

argument_config = None


def load_config(config_directory):
    global config_dir
    config_dir = config_directory
    config_file = os.path.join(config_dir, "default.yml")

    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = yaml.load(f)

        if "default" in config:
            default_file = os.path.join(config_dir, config["default"] + '.yml')
            if os.path.exists(default_file):
                with open(default_file, "r") as f:
                    default_config = yaml.load(f)
                    config.update(default_config)

            if "batch constants" in config:
                global batch_constants_def
                batch_constants_def = config["batch constants"]
            if "audiofile" in config:
                global audiofile
                audiofile = config["audiofile"]
            if "processor" in config:
                global processor
                processor = config["processor"]
            if "serializer" in config:
                global serializer
                serializer = config["serializer"]
            if "argument_config" in config:
                global argument_config
                argument_config = config["argument_config"]


def setup(args, user=None):
    global batch_constants
    if user is not None:
        print(user)
        user_file = os.path.join(config_dir, user + ".yml")
        print(user_file)
        if os.path.exists(user_file):
            with open(user_file, "r") as f:
                user_config = yaml.load(f)
            batch_constants = user_config['user constants']
            batch_constants.set(args)
        else:
            batch_constants = batch_constants_def(args)
            with open(user_file, "w+") as f:
                user_constants = {'user constants': batch_constants}
                yaml.dump(user_constants, f)
    else:
        batch_constants = batch_constants_def(args)




__all__ = ['file_walker', 'serializers', 'tb_ui', 'util', 'FileWalker', 'TomatoBanana']
