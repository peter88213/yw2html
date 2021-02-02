Download `yw2html_<version>.zip`.
Unzip the file and read README.md.

## Changelog

### v0.8.0

Process all yWriter formatting tags.
* Convert underline and strikethrough.
* Discard alignment.
* Discard highlighting.

Based on PyWriter v2.8.0

### v0.7.2

* Refactor and update docstrings.
* Work around a yWriter 7.1.1.2 bug.
* Development: Create test execution directory if necessary

### v0.7.1

* Improve screen output.
* Refactor the code for better maintainability.

### v0.6.0
Adapt to modified yw7 file format (yWriter 7.0.7.2+):
* "Info" chapters are replaced by "Notes" chapters (always unused).
* New "Todo" chapter type (always unused). 
* Distinguish between "Notes scene", "Todo scene" and "Unused scene".
* Chapter/scene tag colors in "proofread" export correspond to those of the yWriter chapter list.

### v0.5.2
* Fix import of uncomplete date/time information.
* Add shebang for Linux use.
* Change line breaks to Unix.

### v0.5.1
* Replace "None" entries by nullstrings.
* Add "Timeline" template example.

### v0.5.0 
* New command line user interface (see README.md).
* More sophisticated examples.

### v0.4.0
* More template types and placeholders supported; see README.md.

### v0.3.1
* Optimize code for faster program execution.

### v0.3.0
* Add characters/locations/items export.

### v0.2.1
* Add date/time placeholders.

