# Audio Pipeline [KEXP-specific documentation]
A set of audio processing tools used to process and prepare audio file for ingestion into asset management systems.

### To Install
It is assumed that you already have Python 3.4 or greater installed, and it is in your path.

1. Checkout this repository [Branch: Python 3]
2. Install musicbrainzngs  `pip install musicbrainzngs`
3. Install mutagen  `pip install mutagen`
4. Install yattag  `pip install yattag`
5. Profit!
 
### Programs
#### File Walker
Walks a directory structure full of audio files and does the following:
 * Pulls out the MusicBrainz Release ID, Track Number, and Disc Number from the file metadata
 * Querys MusicBrainz based on the Release ID, Track Number, and Disc Number, and return the metadata for the Track and Release
 * Querys MusicBrainz based on the Artist ID of all artist's in the album's Artist Credit, and return the metadata for each Artist
 * Writes this information out to the destination directory:
   * File are written to a directory structure of the form:
     *found*: Backup copy of all succesfully processed audio files
     *not_found*: Copy of all tracks that filewalker did not process successfully
     *artist_meta*: Dalet-compatible XML files of artist metadata
     *release_meta*: Dalet-compatible XML files of release metadata
     *track_meta*: Dalet-compatible XML files of track metadata
     *track*: All successfully processed audio files, renamed to match the track ItemCode
     *session_logs*: Tab separated text file of all release, track, artist, and labels processed this session
        Log format: <Item Type>   <ItemCode OR Item MBID (labels only)>    <Item Name>
   * XML files are named according to their ItemCode. Release and Artist XML filenames are given prefix 'r'.
   * Currently files can only be written as Dalet-compatible XML

FileWalker accepts the following options:
 * *--source, -s*
  Record original source of files
    Valid options:
      Melly
      CD Library
      
 * *--category, -c*
  Record category of files
    Allowed Values:
      EXP - Experimental
      HIP - Hip Hop
      JAZ - Jazz
      LOC - Local
      REG - Reggae
      ROC - Rock & Pop
      ROO - Roots
      SOU - Soundtracks
      WOR - World
      ACQ - Recent Acquisitions
      LIV - Live on KEXP
      
 * *--rotation, -r*
  Record rotation status of files
    Allowed values:
      Heavy
      Library
      Light
      Medium
      R/N
      
To Run

1. Change to the `file_walker` directory
2. run `FileWalker.py source_directory destination_directory options`

IMPORTANT: Audio files must have release MBID, as well as track number and disc number associated with that MBID, for FileWalker to succeed. 

# Audio Pipeline 