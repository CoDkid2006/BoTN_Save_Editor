# BoTN Save Editor
Save Editor for Breeders of the Nephelym. Current Build 0.754.3

Requires python 3.7+

Place editor in save directory or change files paths to save directory.

To execute run 'python NephelymSaveEditor.py'

Modify Logic in Main to preform desired edits.
Main function provides examples of most program functions. Functions starting with _ are ment to be internal and should only be used inside class.

# DISCLAIMER!
Make backups of saves before modifing them. Program should be able to make working saves, but there is no 100% guarantee. Invalid options should throw an exception during runtime. 

# BUGS and ISSUES
If you encounter a bug in the program or it creates corrupted saves. Create a new Issue on the Issues page, with the following and it will maybe get fixed
- Explination of bug/issue that is occuring
- Game version

If applicable to the bug/issue any of the following
- Original save
- New Save (useful for comparing what happened, and testing recreatablity or issue)
- list of functions executed
- preset files

## TODO
Lower level parsing and editing for the following classes

- Class for appearance.

- Class for playerobtainedvariants

- Class for playerseenvariants

- Class for gameflags

- Class for worldstate

- Class for breederstatprogress

- GUI. OMEGALUL
