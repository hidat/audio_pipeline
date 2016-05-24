from yattag import Doc, indent
import os.path as path
import os
from ..file_walker import ProcessLog
from ..file_walker import Resources
from ..file_walker import Util

__author__ = 'hidat'


class DaletSerializer:

    def __init__(self, output_dir):
        # Set up metadata directories
        self.track_meta_dir = path.join(output_dir, 'track_meta')
        if not path.exists(self.track_meta_dir):
            os.makedirs(self.track_meta_dir)
        print("Track meta: ", self.track_meta_dir)
        
        self.artist_meta_dir = path.join(output_dir, 'artist_meta')
        if not path.exists(self.artist_meta_dir):
            os.makedirs(self.artist_meta_dir)
        print("Artist meta: ", self.artist_meta_dir)
        
        self.release_meta_dir = path.join(output_dir, 'release_meta')
        if not path.exists(self.release_meta_dir):
            os.makedirs(self.release_meta_dir)
        print("Release meta: ", self.release_meta_dir)
        
        log_dir = path.join(output_dir, 'session_logs')
        if not path.exists(log_dir):
            os.makedirs(log_dir)
        self.logs = ProcessLog.ProcessLog(log_dir, release=True, label=True)
        print("Logs: ", self.logs.log_dir)

        
    def save_track(self, release, track):
        """
        Create an XML file of track metadata that Dalet will be happy with

        :param release_data: Processed release metadata from MusicBrainz
        :param track_data: Processed track metadata from MusicBrainz
        :param batch_meta: Batch metadata (from command line)
        :param output_dir: Output directory to write XML file to
        """
        doc, tag, text = Doc().tagtext()
        
        output_dir = self.track_meta_dir
        
        self.logs.log_track(track)
        
        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('titles'):
            with tag('title'):
                with tag('KEXPRelease'):
                    text(track.release_id)
                with tag('KEXPMediumNumber'):
                    text(str(track.disc_num))
                with tag('KEXPTotalMediums'):
                    text(str(release.disc_count))
                with tag('KEXPTrackMBID'):
                    text(track.id)
                with tag('ItemCode'):
                    text(track.item_code)
                with tag('Key1'):
                    text(track.item_code)
                with tag('KEXPRecordingMBID'):
                    text(track.recording_id)
                with tag('Title'):
                    text(track.title)
                with tag('KEXPTrackNumber'):
                    text(str(track.track_num))
                with tag('KEXPTotalTracks'):
                    text(str(track.track_count))
                with tag('KEXPPrimaryGenre'):
                    text(track.primary_genre)
                with tag('KEXPFCCObscenityRating'):
                    text(track.obscenity)

                for artist in release.artist_sort_names:
                    with tag('KEXPReleaseArtistSortName'):
                        text(artist)

                for artist in track.artists:
                    with tag('KEXPArtist'):
                        text(artist)
                with tag('KEXPArtistCredit'):
                    text(track.artist_credit)
                
                if track.secondary_category:
                    with tag('secondary_category'):
                        text(track.secondary_category)
                    
                with tag('KEXPReleaseArtistDistributionRule'):
                    text(track.artist_dist_rule)
                with tag('KEXPVariousArtistReleaseTitleDistributionRule'):
                    text(track.various_artist_dist_rule)
                with tag('KEXPContentType'):
                    text(track.content_type)
                
                if Resources.BatchConstants.source:
                    with tag('KEXPSource'):
                        text(Resources.BatchConstants.source)


        formatted_data = indent(doc.getvalue())    
        output_file = path.join(output_dir, track.item_code + ".xml")
        with open(output_file, "wb") as f:
            f.write(formatted_data.encode("UTF-8"))

            
    def save_release(self, release):
        """
        Create an XML file of release metadata that Dalet will be happy with
        
        :param release: Processed release metadata from MusicBrainz
        :param batch_meta: Batch metadata from the command line
        :param output_dir: Output directory to write XML file to
            <KEXPMBID>release-xxxx-xxxx-xxxxx-xxxxxxx</KEXPMBID>
            <KEXPReleaseGroupMBID>releasegroup MBID</KEXPReleaseGroupMBID>

            <KEXPArtist>0923598e-2b97-4527-b984-5feed94c168d</KEXPArtist><!-- multiple cardinality -->
            <KEXPReleaseArtistCredit>artist 1, artist 2, etc..</KEXPReleaseArtistCredit>
            <KEXPLabel>011d1192-6f65-45bd-85c4-0400dd45693e</KEXPLabel><!-- multiple cardinality -->

            <KEXPArea>Area</KEXPArea>
            <KEXPAreaMBID>area MBID</KEXPAreaMBID>
            <KEXPASIN>ASIN dfsdsdf</KEXPASIN>
            <KEXPReleaseBarcode>Barcode</KEXPReleaseBarcode>
            <KEXPReleaseCatalogNumber>2132</KEXPReleaseCatalogNumber> <!-- multiple cardinality -->
            <KEXPCountryCode>US</KEXPCountryCode>
            <KEXPReleasePackaging>DVD</KEXPReleasePackaging> <!-- multiple cardinality -->

            <KEXPDisambiguation>Disambiguation</KEXPDisambiguation>

            <KEXPDateReleased>1999-03-22</KEXPDateReleased> <!--	short text: No specific format required -->
            <KEXPFirstReleaseDate>1999-03-25</KEXPFirstReleaseDate> <!--	short text: No specific format required -->
            <KEXPLength>10:23</KEXPLength>

            <KEXPLink>http://link 1</KEXPLink> <!-- multiple cardinality -->

            <KEXPTag>TAG 1</KEXPTag> <!-- multiple cardinality -->
            <KEXPTag>tag 2</KEXPTag>
        """

        output_dir = self.release_meta_dir

        # write release & labels to the log
        self.logs.log_release(release)
        for label in release.labels:
            self.logs.log_label(label)

        doc, tag, text = Doc().tagtext()
        
        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('Titles'):
            with tag('GlossaryValue'):
                with tag('Key1'):
                    text(release.item_code)
                with tag('ItemCode'):
                    text(release.item_code)
                with tag('KEXPTitle'):
                    text(release.title)
                with tag('title'):
                    text(release.glossary_title)
                with tag('GlossaryType'):
                    text(release.glossary_type)
                with tag('KEXPMBID'):
                    text(release.id)
                with tag('KEXPReleaseGroupMBID'):
                    text(release.release_group_id)
                    
                for artist in release.artist_ids:
                    with tag('KEXPArtist'):
                        text(artist)
                for label in release.labels:
                    with tag('KEXPlabel'):
                        text(label.id)
                
                with tag('KEXPReleaseArtistCredit'):
                    text(release.artist)
                with tag('KEXPDistributionCategory'):
                    text(release.distribution_category)
                with tag('KEXPCountryCode'):
                    text(release.country)
                with tag('KEXPASIN'):
                    text(release.asin)
                with tag('KEXPReleaseBarcode'):
                    text(release.barcode)
                with tag('KEXPReleasePackaging'):
                    text(release.packaging)
                with tag('KEXPDisambiguation'):
                    text(release.disambiguation)
                with tag('KEXPDateReleased'):
                    text(release.date)
                
                if release.first_released:
                    with tag('KEXPFirstReleaseDate'):
                        text(release.first_released)

                for item in release.tags:
                    with tag('KEXPTag'):
                        text(item)
                        
                if Resources.BatchConstants.rotation:
                    r_status = Util.stringCleanup(Resources.BatchConstants.rotation)
                    with tag('KEXPReleaseRotationStatus'):
                        text(r_status)
                if Resources.BatchConstants.category:
                    with tag('KEXPPrimaryGenre'):
                        text(Resources.BatchConstants.category)

        formatted_data = indent(doc.getvalue())
        
        output_file = path.join(output_dir, 'r' + release.item_code + ".xml")
        with open(output_file, "wb") as f:
            f.write(formatted_data.encode("UTF-8"))

            
    def save_artist(self, artist, artist_members):
        """
        Create an XML file of artist metadata that Dalet will be happy with.
        
        If the artist is a group that has multiple members, not an individual, 
        all member metadata (for artists new to this batch) will also be generated.
        
        :param artist: Processed metadata from MusicBrainz for 'main' artist
        :param artist_members: Processed artist metadata from MusicBrainz for any members of 'artist'
        :param output_dir: Output directory to write XML file to
        """

        output_dir = self.artist_meta_dir
        
        # get metadata for artist and, if artist is a group
        # all group members (that have not yet had metadata generated this batch)
        
        self.logs.log_artist(artist, artist_members)
        
        doc, tag, text = Doc().tagtext()

        doc.asis('<?xml version="1.0" encoding="UTF-8"?>')
        with tag('Titles'):
            for member in artist_members:
                with tag('GlossaryValue'):
                    self.save_one_artist(member, tag, text)

            with tag('GlossaryValue'):
                self.save_one_artist(artist, tag, text)

                if artist.group_members:
                    for member in artist.group_members:
                        with tag('KEXPMember'):
                            text(member)

        formatted_data = indent(doc.getvalue())

        output_file = path.join(output_dir, 'a' + artist.item_code + ".xml")
        with open(output_file, "wb") as f:
            f.write(formatted_data.encode("UTF-8"))


    def save_one_artist(self, artist, tag, text):
        """
        Save the metadata for one artist

        :param artist: Processed artist metadata from MusicBrainz
        :param tag: Yattag 'tag' 
        :param text: Yattag 'text'
        """
        # mandatory fields
        with tag('Key1'):
            text(artist.item_code)
        with tag('ItemCode'):
            text(artist.item_code)
        with tag('title'):
            text(artist.title)
        with tag('GlossaryType'):
            text(artist.glossary_type)
        with tag('KEXPName'):
            text(artist.name)
        with tag('KEXPSortName'):
            text(artist.sort_name)
        with tag('KEXPMBID'):
            text(artist.id)
            
        # optional fields

        if len(artist.alias_list) > 0:
            for alias in artist.alias_list:
                with tag('KEXPAlias'):
                    text(alias)

        if artist.annotation > '':
                with tag('KEXPAnnotation'):
                    text(artist.annotation)

        if artist.disambiguation > '':
            with tag('KEXPDisambiguation'):
                text(artist.disambiguation)

        if artist.type > '':
            with tag('KEXPArtistType'):
                text(artist.type)
                
        with tag('KEXPBeginArea'):
            text(artist.begin_area.name)
        with tag('KEXPBeginAreaMBID'):
            text(artist.begin_area.id)

        with tag('KEXPBeginDate'):
            text(artist.begin_date)
        with tag('KEXPEndDate'):
            text(artist.end_date)
        if artist.ended:
            with tag('KEXPEnded'):
                text(artist.ended)

        with tag('KEXPCountry'):
            text(artist.country.name)
        with tag('KEXPCountryMBID'):
            text(artist.country.id)
            
        with tag('KEXPEndArea'):
            text(artist.end_area.name)
        with tag('KEXPEndAreaMBID'):
            text(artist.end_area.id)

        if len(artist.ipi_list) > 0:
            for code in artist.ipi_list:
                with tag('KEXPIPICode'):
                    text(code)

        if len(artist.isni_list) > 0:
            for code in artist.isni_list:
                with tag('KEXPISNICode'):
                    text(code)

        if len(artist.url_relation_list) > 0:
            for link in artist.url_relation_list:
                with tag('KEXPLink'):
                    text(link)