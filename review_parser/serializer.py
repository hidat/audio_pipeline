from yattag import Doc, indent
import os.path as path
import os


class DaletSerializer:

    def __init__(self, output_dir):
        # Set up metadata directories
        self.release_meta_dir = output_dir
        if not path.exists(self.release_meta_dir):
            os.makedirs(self.release_meta_dir)
        print("Release meta: ", self.release_meta_dir)


    def saveRelease(self, release):
        """
        Create an XML file of release metadata that Dalet will be happy with

        :param release: Processed release metadata from MusicBrainz
        """

        output_dir = self.release_meta_dir

        doc, tag, text = Doc().tagtext()

        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('Titles'):
            with tag('GlossaryValue'):
                with tag('GlossaryType'):
                    text('Release')
                with tag('Key1'):
                    text(release.mbID)
                with tag('ItemCode'):
                    text(release.mbID)
                with tag('KEXPReviewRich'):
                    text(release.review)
        formatted_data = indent(doc.getvalue())

        output_file = path.join(output_dir, 'r' + release.mbID + ".xml")
        with open(output_file, "wb") as f:
            f.write(formatted_data.encode("UTF-8"))
