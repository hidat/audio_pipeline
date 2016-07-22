from yattag import Doc, indent
import os.path as path
import os

###
# Serializes a content for Dalet updates
###
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

        review = release.review
        # Convert <strong> into <strong><font size=5> and </strong> to </font></strong>
        review = review.replace('<strong>', '<strong><font size=2>').replace('</strong>', '</font></strong>')

        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('Titles'):
            with tag('GlossaryValue'):
                with tag('GlossaryType'):
                    text('Release')
                with tag('Key1'):
                    text(release.mbID)
                with tag('ItemCode'):
                    text(release.mbID)
                with tag('title'):
                    text(release.daletGlossaryName)
                with tag('KEXPReviewRich'):
                    text(review)
        formatted_data = indent(doc.getvalue())

        output_file = path.join(output_dir, 'r' + release.mbID + ".xml")
        with open(output_file, "wb") as f:
            f.write(formatted_data.encode("UTF-8"))

    def save_track(self, track):
        """
        Create an XML file of track metadata that Dalet will be happy with

        :param track: Merged track metadata
        :param output_dir: Output directory to write XML file to
        """
        doc, tag, text = Doc().tagtext()

        output_dir = self.track_meta_dir

        self.logs.log_track(track)

        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('titles'):
            with tag('title'):
                with tag('ItemCode'):
                    text(track.item_code)
                with tag('Key1'):
                    text(track.item_code)
                with tag('KEXPStarRating'):
                    text(track.stars)
                with tag('Title'):
                    text(track.title)

        formatted_data = indent(doc.getvalue())
        output_file = path.join(output_dir, track.item_code + ".xml")
        with open(output_file, "wb") as f:
            f.write(formatted_data.encode("UTF-8"))
