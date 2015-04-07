# Audio Pipeline
A set of audio processing tools used to process and prepare audio files for ingestion into a variety of asset management systems.

### To Install
It is assumed that you already have Python 2.7 or greater installed, and it is in your path
1. Checkout this repository
2. Install musicbrainzngs  `pip install musicbrainzngs
3. Install mutagen  `pip install mutagen
4. Profit!
 
### Programs
#### File Walker
This will walk a directory structure full of audio files that have either been ripped with dbPoweramp, or scanned with Picard, and do the following:
 * Pull out the MusicBrainz Release ID from the file 
 * Query MusicBrainz based on the Release ID, Track Number and Disc Number, and return the metadata for the Track and Release
 * Writes this information out to the destination directory
   * Currently the files are written as json
   * The file cotains three top level keys - one for the raw tags as extracted by mutagen, one for the release information, and one for the track information
   * The files are named using their MusicBrainz Recording Track ID
    
To Run   
1. Change to the `file_walker` directory
2. run `file_walker source_directory destination-directory`

