import shutil
import os
import sys
import subprocess

from ..util import Resources
from .. import set_destination

class MoveFiles:

    def __init__(self, rule, copy, wait_for_close=False, dest_folder=None):
        """
        Move audiofiles to the appropriate destination directories,
        as determined by the 'rule' function passed to rule
        :param rule:
        :return:
        """
        self.rule = rule
        self.dest_folder = set_destination()
        self.wait_for_close = wait_for_close

        if not self.dest_folder:
            self.dest_folder = dest_folder

        if copy:
            self.command = "COPY"
            self.join = ["&", "COPY"]
        else:
            self.command = "MOVE"
            self.join = ["&", "MOVE"]

    def move_files(self, files, src_dir=None):
        """
        Iterate over the elements of a ProcessDirectory object, and move them to the correct directory,
        using python subprocess

        :param files:
        :return:
        """
        files.first()
        valid_count = 0
        invalid_count = 0

        while files.has_next():
            command = [self.command]
            tracks = files.next()
            cd_valid = True
            for i in range(len(tracks)):
                if self.rule.is_valid(tracks[i]):
                    repo_path = self.rule.get_dest(tracks[i])
                    if repo_path is not None:
                        full_path = os.path.join(self.dest_folder, repo_path)
                        if not os.path.exists(full_path):
                            os.makedirs(full_path)

                        if i != 0:
                            command += self.join
                        command.append(tracks[i].file_name)
                        dest = full_path
                        dest_filename = self.rule.get_filename(tracks[i])
                        if dest_filename:
                            dest = os.path.join(dest, dest_filename)
                        command.append(dest)
                else:
                    cd_valid = False

            directory = os.path.split(tracks[0].file_name)[0]
            if cd_valid:
                valid_count += 1
                print("Moving " + ascii(directory))
                subprocess.run(command, shell=True)

                if not Resources.is_release(directory):
                    shutil.rmtree(directory)
            else:
                invalid_count += 1
                print("Invalid content found in " + directory + ", not copying.")

        if self.wait_for_close and (valid_count > 0 or invalid_count > 0) :
            print("\n{0} CDs moved, {1} failed.".format(valid_count, invalid_count))
            print("Press the [Enter] key to finish...")
            sys.stdin.read(1)

        return valid_count