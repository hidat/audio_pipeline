from . import Tag
    
class VorbisMetadata(Tag.MetadataFormat):

    """
    A static class used to extract and save Vorbis-formated metadata tags.
    """
    # release-level serialization names
    _album_serialization = "album"
    _album_artist_serialization = "albumartist"
    _release_date_serialization = "date"
    _label_serialization = "label"
    
    # track-level serialization names
    _title_serialization = "title"
    _artist_serialization = "artist"
    _disc_num_serialization = "discnumber"
    _track_num_serialization = "tracknumber"
    _length_serialization = "Length"