import os
import yaml
import copy
import re

class Constants:
    batch_constants_def = None
    batch_constants = None

    config_dir = ""
    audiofile = None
    processor = None
    serializer = None
    custom_tags = None
    load_releases = True
    is_tb = False

    custom_track_tags = []
    custom_release_tags = []
    obscenity_rating = None
    ignore_case = False
    user = None
    
    argument_config = None

    @classmethod
    def load_config(cls, config_directory):
        cls.custom_tags = {"item_code": "ITEMCODE", "obscenity": "OBSCENITYRATING",
                           "category": "CATEGORY"}
        cls.config_dir = config_directory
        config_file = os.path.join(cls.config_dir, "default.yml")

        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config = yaml.load(f)
                cls.load(config)

    @classmethod
    def load(cls, config):
        if "default" in config:
            default_file = os.path.join(cls.config_dir, config["default"] + '.yml')
            if os.path.exists(default_file):
                with open(default_file, "r") as f:
                    default_config = yaml.load(f)
                    config.update(default_config)

        # configuration options for tag reading/writing -
        # custom track tags, custom release tags, and whether to ignore tag casing
        # for AAC & ID3 tags, where case does matter
        if "tags" in config:
            tag_data = config["tags"]
            if "ignore_case" in tag_data:
                cls.ignore_case = tag_data["ignore_case"]
            if "custom_tags" in tag_data:
                if "track" in tag_data["custom_tags"]:
                    cls.custom_track_tags = tag_data["custom_tags"]["track"]
                if "release" in tag_data["custom_tags"]:
                    cls.custom_release_tags = tag_data["custom_tags"]["release"]
            if "obscenity_rating" in tag_data:
                util.AudioFile.CustomTags.obscenity = tag_data["obscenity_rating"]
                cls.obscenity_rating = tag_data['obscenity_rating']
        if "tb_lookup" in config:
            cls.load_releases = config['tb_lookup']
        if "batch constants" in config:
            cls.batch_constants_def = config["batch constants"]
            cls.batch_constants = cls.batch_constants_def(None)
        if "audiofile" in config:
            cls.audiofile = config["audiofile"]
            if "user" in config:
                cls.audiofile.audiofile_type = config["user"]

        if "processor" in config:
            cls.processor = config["processor"]
        if "serializer" in config:
            cls.serializer = config["serializer"]
        if "argument_config" in config:
            cls.argument_config = config["argument_config"]

    @classmethod
    def setup(cls, args, user=None):
        if user is not None:
            user_file = os.path.join(cls.config_dir, user + ".yml")
            if os.path.exists(user_file):
                with open(user_file, "r") as f:
                    user_config = yaml.load(f)
                cls.batch_constants = copy.deepcopy(user_config['user constants'])
                cls.batch_constants.set(args)
            else:
                answer = input("Profile " + str(user) + " not found. Create profile? (y/n) ").casefold()
                while True:
                    if re.match(answer, "yes") or re.match("yes", answer):
                        cls.batch_constants = cls.batch_constants_def(args)
                        with open(user_file, "w+") as f:
                            user_constants = {'user constants': cls.batch_constants}
                            yaml.dump(user_constants, f)
                            break
                    elif re.match(answer, "no") or re.match("no", answer):
                        exit()
                    answer = input("Please enter 'y' or 'n': ")
        else:
            cls.batch_constants.set(args)


default_config = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
Constants.load_config(default_config)

__all__ = ['file_walker', 'serializers', 'tb_ui', 'util', 'FileWalker', 'TomatoBanana']
