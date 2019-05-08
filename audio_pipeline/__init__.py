import os
import yaml
import copy
import re

class Constants:
    config_data = {}

    batch_constants_def = None
    batch_constants = None

    config_dir = ""
    processor = None
    discogs_processor = None
    serializer = None
    custom_tags = None
    tb_lookup = True
    acoustid_lookup = True
    is_tb = False
    move_files = ""
    wait_for_close = False

    custom_track_tags = []
    custom_release_tags = []
    tb_track_tags = []
    tb_release_tags = []
    ignore_case = False
    user = None
    tb_meta_commands = None

    argument_config = None

    @classmethod
    def load_config(cls, config_directory):
        cls.custom_tags = {"item_code": "ITEMCODE", "obscenity": "OBSCENITYRATING",
                           "category": "CATEGORY"}
        cls.config_dir = config_directory
        config_file = os.path.join(cls.config_dir, "default.yml")

        if os.path.exists(config_file):
            cls.config_file = config_file
            with open(config_file, "r") as f:
                config = yaml.full_load(f)
                cls.load(config)

    @classmethod
    def load(cls, config):
        config_name = os.path.split(os.path.splitext(cls.config_file)[0])[1]
        cls.config_data[config_name] = config.copy()

        if "default" in config:
            default_file = os.path.join(cls.config_dir, config["default"] + '.yml')
            if os.path.exists(default_file):
                cls.config_file = default_file
                with open(default_file, "r") as f:
                    default_config = yaml.full_load(f)
                    config.update(default_config)

        config_name = os.path.split(os.path.splitext(cls.config_file)[0])[1]
        cls.config_data[config_name] = config.copy()

        # configuration options for tag reading/writing -
        # custom track tags, custom release tags, and whether to ignore tag casing
        # for AAC & ID3 tags, where case does matter
        if "tb_meta" in config:
            cls.tb_meta_commands = config["tb_meta"]
            if "release" in config["tb_meta"]:
                cls.tb_release_tags = [t['tag'] for t in config["tb_meta"]["release"]]
            if "track" in config["tb_meta"]:
                cls.tb_track_tags = [t['tag'] for t in config["tb_meta"]["track"]]
        if "tb_lookup" in config:
            cls.tb_lookup = config['tb_lookup']
        if "acoustid_lookup" in config:
            cls.acoustid_lookup = config["acoustid_lookup"]
        if "batch constants" in config:
            cls.batch_constants_def = config["batch constants"]
            cls.batch_constants = cls.batch_constants_def(None)
        if "processor" in config:
            cls.processor = config["processor"]
        if "discogs_processor" in config:
            cls.discogs_processor = config["discogs_processor"]
        if "serializer" in config:
            cls.serializer = config["serializer"]
        if "argument_config" in config:
            cls.argument_config = config["argument_config"]
        if "tags" in config:
            tag_data = config["tags"]
            if "ignore_case" in tag_data:
                cls.ignore_case = tag_data["ignore_case"]
            if "custom_tags" in tag_data:
                if "track" in tag_data["custom_tags"]:
                    cls.custom_track_tags = tag_data["custom_tags"]["track"]
                if "release" in tag_data["custom_tags"]:
                    cls.custom_release_tags = tag_data["custom_tags"]["release"]
        if "post_process" in config:
            post_process = config["post_process"]
            if "move_files" in post_process:
                cls.move_files = post_process["move_files"]
                if "wait_for_close" in post_process:
                    cls.wait_for_close = post_process["wait_for_close"]

    @classmethod
    def setup(cls, args, user=None):
        if user is not None:
            user_file = os.path.join(cls.config_dir, user + ".yml")
            if os.path.exists(user_file):
                with open(user_file, "r") as f:
                    user_config = yaml.full_load(f)
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
