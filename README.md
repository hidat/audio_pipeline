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
       Current log files:  
        * *filewalker_log*: all releases, tracks, artists, and labels
        * *label_log*: all labels
        * *release_log*: all releases
   * Serialized metadata files are named according to their ItemCode. Release filenames are given prefix 'r'; artist filenames are given prefix 'a'.
   * Currently files can only be written as Dalet-compatible XML
   
#####Options:

######General:
 
  * *--delete, -d*
    Delete source audio files after processing
 
  * *--generate, -g*
    Generate metadata only, without copying audio 

  * *--mbhost*
    Set server to retrieve MusicBrainz data from. Default is musicbrainz.org; another server can be manually specified

  * *--no_artist*
    Do not generate artist metadata XMLs.
            
  * *--i, --gen_item_code*
    Generate a unique item code for all audio files
        
######KEXP-specific:

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

  * *--anchor, -a*
    Set KEXPAnchorStatus field of all tracks to '1'
      
#####To Run

1. Navigate to the top-level audio_pipeline directory
2. run `FileWalker.py source_directory destination_directory options`

IMPORTANT: Audio files must have release MBID, as well as track number and disc number associated with that MBID, for FileWalker to succeed. 

   
### TomatoBanana
A program to assist in the review and entry of metadata of ripped audio discs
 * Pulls relevent metadata from audio files
 * Displays release metadata onscreen in an easily human-readable format for review
 * Releases are displayed in the same order that they were ripped, for easy processing when returning discs to cases
 * Allows the easy entry of obscenity rating values for individual tracks
 * An interface for complete metadata entry is easily accessed from a release in TB
  
#####To Run
1. Navigate to the top-level audio_pipeline directory
2. Run `TomatoBanana.py`
