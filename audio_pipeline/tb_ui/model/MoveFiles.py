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
        self.copy = copy

    def move_files(self, files):
        """
        Iterate over the elements of a ProcessDirectory object, and move them to the correct directory,
        using python subprocess

        :param files:
        :return:
        """
        args = list()
        files.first()
        if self.copy:
            args.append("copy")
        else:
            args.append("move")

        for f in files:


                self.model.first()

        if self.copy_dir:
            move = shutil.copy
        else:
            move = shutil.move

        while self.model.has_next():
            release = self.model.next()

            # get path to has-mbid and no-mbid folders once per release
            release_path = os.path.split(release[0].file_name)[0]
            picard = release[0].picard
            mb = release[0].mb

            if not os.path.exists(picard):
                os.mkdir(picard)
            if not os.path.exists(mb):
                os.mkdir(mb)

            for track in release:
                # move to correct folder
                move(track.file_name, track.dest_dir)
                print("moving " + ascii(track.file_name) + " to " + ascii(track.dest_dir))


            try:
                os.rmdir(picard)
            except OSError as e:
                pass

            try:
                os.rmdir(mb)
            except OSError as e:
                pass

            try:
                os.rmdir(release_path)
            except OSError as e:
                # release directory is not empty
                continue
