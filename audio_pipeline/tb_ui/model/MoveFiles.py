import shutil
import os
import subprocess
from ..util import Resources
from .. import set_destination

class MoveFiles:

    def __init__(self, rule, copy, dest_folder=None):
        """
        Move audiofiles to the appropriate destination directories,
        as determined by the 'rule' function passed to rule
        :param rule:
        :return:
        """
        self.rule = rule
        self.dest_folder = set_destination()
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
        
        while files.has_next():
            command = [self.command]
            tracks = files.next()
            for i in range(len(tracks)):
                dest = self.rule.get_dest(tracks[i])
                if dest:
                    dest = os.path.join(self.dest_folder, self.rule.get_dest(tracks[i]))
                    if not os.path.exists(dest):
                        os.makedirs(dest)

                    if i != 0:
                        command += self.join
                    command.append(tracks[i].file_name)
                    command.append(dest)
                
            directory = os.path.split(tracks[0].file_name)[0]
            print("Moving " + ascii(directory))
            subprocess.run(command, shell=True)

            if not Resources.is_release(directory):
                shutil.rmtree(directory)
