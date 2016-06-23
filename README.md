# Audio Pipeline
A set of audio processing tools used to process and prepare audio files for ingestion into asset management systems.

To Install
-----------
It is assumed that you already have Python 3.4 or greater installed, and it is in your path.

1. Checkout this repository
2. Install musicbrainzngs  `pip install musicbrainzngs`
3. Install mutagen  `pip install mutagen`
4. Install yattag  `pip install yattag`
4. Install yaml  `pip install pyyaml`
5. Profit!
 
Programs
-----------
### File Walker
Walks a directory structure of audio files and does the following:
 * Pulls out the MusicBrainz Release ID, Track Number, and Disc Number from the file metadata
 * Querys MusicBrainz based on the Release ID, Track Number, and Disc Number, and return the metadata for the Track and Release
 * Querys MusicBrainz based on the Artist ID of all artist's in the album's Artist Credit, and return the metadata for each Artist
 * Writes this information out to the destination directory:
   * File are written to a directory structure of the form:  
     *found*: Backup copy of all succesfully processed audio files  
     *not_found*: Copy of all tracks that filewalker did not process successfully  
     *artist_meta*: Serialized artist metadata files  
     *release_meta*: Serialized release metadata files  
     *track_meta*: Serialized track metadata files  
     *track*: All successfully processed audio files, renamed to match the track ItemCode  
     *session_logs*: Tab separated text files of the form:
      `<Item Type>   <ItemCode>  <Item Name>`  
      Currently log files:  
       * *filewalker_log*: all releases, tracks, artists, and labels
       * *label_log*: all labels
       * *release_log*: all releases
   * Serialized metadata files are named according to their ItemCode. Release filenames are given prefix 'r'; artist filenames are given prefix 'a'.
   * Currently files can only be written as Dalet-compatible XML
   
#####Options:

 

 * *--source, -s*  
    Passes in the source of audio files, to be recorded in XML.
        
    **Allowed values:**
    
    - Melly  
    - CD Library
      
 * *--category, -c*   
    Passes in the category of audio files, to be recorded in XML.
        
    **Allowed values:**

    - EXP - Experimental  
    - HIP - Hip Hop  
    - JAZ - Jazz  
    - LOC - Local  
    - REG - Reggae  
    - ROC - Rock & Pop  
    - ROO - Roots  
    - SOU - Soundtracks  
    - WOR - World  
    - ACQ - Recent Acquisitions  
    - LIV - Live on KEXP
      
 * *--rotation, -r*   
    Passes in the rotation status of audio files, to be recorded in XML.  
        
    **Allowed values:**
    
    - Heavy   
    - Library  
    - Light  
    - Medium  
    - R/N
    
  * *--generate, -g*
    Generate metadata only, without copying audio 
    
  * *--local, -l*
    Use the local KEXP MusicBrainz server instead of musicbrainz.org
    
  * *--i, --gen_item_code*
    Generate a unique item code for all audio files

  * *--anchor, -a*
    Set KEXPAnchorStatus field of all tracks to '1'

  * *--mbhost*
    Set server to retrieve MusicBrainz data from. Default is musicbrainz.org; another server can be manually specified

  * *--no_artist*
    Do not generate artist metadata XMLs.
      
#####To Run

1. Navigate to the top-level audio_pipeline directory
2. run `FileWalker.py source_directory destination_directory options`

IMPORTANT: Audio files must have release MBID, as well as track number and disc number associated with that MBID, for FileWalker to succeed. 

   
### TomatoBanana
A program to assist in reviewing the metadata of ripped audio discs
 * Pulls relevent metadata - release name, artist, and disc number, and track name, artist, number, length, and KEXPFCCOBSCENITYRATING - from the audio file
 * Displays this metadata onscreen in an easily human-readable format for review
 * Current metadata entry options:
   * KEXPFCCOBSCENITYRATING can be set to YELLOW DOT or RED DOT directly

#####To Run
1. Navigate to the top-level audio_pipeline directory
2. Run `TomatoBanana.py`
