# BoTN Save Editor
Save Editor for Breeders of the Nephelym. Current Build 0.756.9. Check releases for older versions

Requires python 3.7+

# DISCLAIMER!
Make backups of saves before modifing them. Program should be able to make working saves, but there is no 100% guarantee.

# GUIDE
Place editor in save directory or change files paths to save directory.

MODIFY LOGIC IN MAIN TO PREFORM DESIRED EDITS. Default logic is a bit identity check for the editor.

To execute run 'python NephelymSaveEditor.py'

# Notable Features
Here is a list of some of the functions that are already implimented in the program.
- Duplication of Nephelyms
- Add and Removal of Nephelyms
- Cloning of Nephelyms in all possible sizes
- Generation of Nephelyms from presets
- EXPORTING Nephelyms to presets
- Changing of Nephelym stats, rarity
- Add and Removal of Nephelym traits
- Changing of Nephelym Race, Sex, and name
- Transfering Appearance to another Nephelym

Saves should be fully parsed so other sub-values can be changes like individual colors in appearance, but they dont have a direct interface function.


## Brief
Mostly started this because of not wanting to spend hours breeding perfect nehpelyms but it morphed into curiosity of how UE serializes it saves. Figuring out how to parse save game file data structures down to a simple form and recreating them back into a working save has been an interesting challenge. This is more of a tech exploration than a 'Proper' save editor, but included are functions to help facilitate bulk editing of a save. More ganular editing is possible but will require more logical thinking on the users end to achieve the desired changes. The main function provides examples of most higher level program functions. Functions starting with _ are ment to be internal and should only be used inside class or if debugging.

# BUGS and ISSUES
If you encounter a bug in the program or it creates corrupted saves. Create a new Issue on the Issues page, with the following and it will maybe get fixed
- Explination of bug/issue that is occuring
- Game version

If applicable to the bug/issue any of the following
- Original save
- New Save (useful for comparing what happened, and testing recreatablity of issue)
- list of functions executed
- preset files

## Known Issues
- Presets for Exotics do not save/load properly, will be converted to hominal. This will NOT be addressed.

## TODO
Lower level parsing and editing for the following classes

- Better Understanding of text, array struct, and map properties for better generic parsing

- Interface functions for lower level variables like appearance and game flags

- Macros for remaining sub-classes values. I.e. list of all possible gamestate flag

- GUI. OMEGALUL