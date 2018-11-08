# Directory-Cleaner
This tool helps clean up the SD cards used by 3D printers 
by removing files that are older than a specified period of
time. It can be made to automatically run with Windows.

# DirectoryCleanerConfig.txt
The configuration has the followng options included:
* SD_CARD_CLEAR_TIME - the time in WEEKS and DAYS is kept.
* DIRECTORIES_TO_SCAN - additional directories to scan.
	* Keep in mind copying files doesn't change the last modified time.
* DRIVES_TO_SCAN - the drives to scan by name.
* DIRECTORY_NAMES_TO_IGNORE - directories that are ignored.
* FILES_TO_IGNORE - the blacklist for files to remove.
	* Adding NEGATE turns it into a whitelist