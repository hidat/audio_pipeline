import os
import subprocess

class MoveFiles:

    def __init__(self, rule, copy):
        """
        Move audiofiles to the appropriate destination directories,
        as determined by the 'rule' function passed to rule
        :param rule:
        :return:
        """
        self.rule = rule
        if copy:
            self.command = "COPY"
            self.join = ["&", "COPY"]
        else:
            self.command = "MOVE"
            self.join = ["&", "MOVE"]

    def move_files(self, files):
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
                    
                if i != 0:
                    command += self.join
                command.append(tracks[i].file_name)
                command.append(dest)
                
            subprocess.run(command, shell=True)