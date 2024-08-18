[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

### Version 2.1.7

- Strip illegal characters before parsing yw7 input.

Based on PyWriter version 12.19.6

### Version 2.1.6

- Refactor for future Python versions.

Based on PyWriter 12.19.4

### Version 2.1.5

- Reading .yw7 files created with the iOS yWriter version.

Based on PyWriter 12.19.0

### Version 2.1.4

- Library update.

Based on PyWriter 12.1.3

### Version 2.1.3

- Make it run with old Windows versions.

Based on PyWriter 8.0.11

### Version 2.1.2

- Modify "shebang" line to make the script run with Python 3.11 under
Windows.

Based on PyWriter 8.0.8

### Version 2.1.1

- Add placeholders for country code and language code.
- Library upgrade.
- Fix a bug where attempting to save a write-protected file raises an
uncaught exception.
- Revise error handling: Throw exceptions instead of returning error messages.

Based on PyWriter 8.0.8

### Version 2.0.7

- Update the PyWriter library for future Python versions.
- Count words like in LibreOffice. See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html.

Based on PyWriter 7.14.2

### Version 2.0.6 Optional release

- Code refactoring and library update.

Based on PyWriter 7.2.1

### Version 2.0.5 Bugfix release

- Fix and refactor inline code removal.

Based on PyWriter 5.16.1

### Version 2.0.4 Consider inline code

- Remove inline code when exporting.

Based on PyWriter 5.12.5

### Version 2.0.3 Improved word counting

- Fix word counting considering ellipses.

Based on PyWriter 5.12.4

### Version 2.0.2 Improved word counting

- Fix word counting considering comments, hyphens, and dashes.

Based on PyWriter 5.12.3

### Version 2.0.1

- Improve code and documentation quality.

Based on PyWriter 5.0.2

### Version 2.0.0

- Fix a bug where "To do" chapters cause an exception.
- Fix a regression from v1.6.3 where the example files are unreadable.
- Optionally, specify the HTML templates as yWriter scenes.
- Add $AuthorBio placeholder.
- Improve the overall code quality.

Based on PyWriter 5.0.0

### Version 1.8.0 Drop the support of the .yw6 file format.

Since yWriter5, yWriter6 and yWriter7 all use .yw7 now, the .yw6 conversion is dispensable.

Based on PyWriter 3.28.2

### Version 1.6.3 Bugfix release

This release is strongly recommended.
Fix a regression from PyWriter v3.12.5. causing a crash if a scene has an 
hour, but no minute set.

Based on PyWriter 3.16.4

### Version 1.6.2 Bugfix

- Fix _NOTES_SCENE_TEMPLATE file name.
- Preprocess date/time information before export.
- Add more examples.

Based on PyWriter 3.12.5

### Version 1.6.1 Fix "chapter end" template processing

Based on PyWriter 3.12.3

### Version 1.6.0 Add a special template for scenes at the beginning of the chapter

New:
- first_scene_template.html

Based on PyWriter 3.12.0

### Version 1.4.0 Add alternative chapter count designs

New: 
- $ChNumberEnglish: Chapter number written out in English
- $ChNumberRoman: Chapter number in Roman numbers

Based on PyWriter 3.10.2

### Version 1.2.2 Optional update

- Major refactoring of the yw7 file processing.

Based on PyWriter 3.8.0

### Version 1.2.1 Optional update

This update is recommended for Linux users. It makes the "Open" button
work on non-Windows operating systems.

- Make the YwCnvUi.open_newFile() method os-independent.

Based on PyWriter 3.6.7

### Version 1.2.0 Optional update

- Update the underlying class library with changed API for better maintainability.

Based on PyWriter 3.0.0

### Version 1.1.2 Bugfix

Fix a bug setting the suffix erroneously to None.

Based on PyWriter 2.17.4 (development version)


### Version 1.1.0 Make GUI customization easier

The converter is now even more loosely coupled with its user interface. 
This should make it easier for application developers to customize user interaction, 
and use any GUI framework.

Based on PyWriter 2.17.0 (development version)


### Version 1.0.1 Optional update

Refactor the code
- Move the HtmlExport class to the Pywriter library.
- Replace it by the MyExport subclass.

Based on PyWriter 2.15.1


### Version 1.0.0 Rename the script and change the user interface

- Change the script's file extension from `.pyw` to `.py` and implement a command line-only UI.

__Please note:__  If you update yw2html, be sure to change the extensions in your existing custom batch files.

Based on PyWriter 2.14.4


### Version 0.10.0 Improve the processing of comma-separated lists

- Fix incorrectly defined tags during yWriter import.
- Protect the processing of comma-separated lists against wrongly set
  blanks.

Based on PyWriter 2.14.1


### Version 0.9.0 Underline and strikethrough no longer supported

That is because a real support would require considering nesting and 
multi paragraph formatting. That would make everything too complicated, 
considering that such formatting is not common in a fictional prose text.

Based on PyWriter 2.9.0

### Version 0.8.0

Process all yWriter formatting tags.
- Convert underline and strikethrough.
- Discard alignment.
- Discard highlighting.

Based on PyWriter 2.8.0

### Version 0.7.2

- Refactor and update docstrings.
- Work around a yWriter 7.1.1.2 bug.
- Development: Create test execution directory if necessary

### Version 0.7.1

- Improve screen output.
- Refactor the code for better maintainability.

### Version 0.6.0
Adapt to modified yw7 file format (yWriter 7.0.7.2+):
- "Info" chapters are replaced by "Notes" chapters (always unused).
- New "Todo" chapter type (always unused). 
- Distinguish between "Notes scene", "Todo scene" and "Unused scene".
- Chapter/scene tag colors in "proofread" export correspond to those of the yWriter chapter list.

### Version 0.5.2
- Fix import of uncomplete date/time information.
- Add shebang for Linux use.
- Change line breaks to Unix.

### Version 0.5.1
- Replace "None" entries by nullstrings.
- Add "Timeline" template example.

### Version 0.5.0 
- New command line user interface (see README.md).
- More sophisticated examples.

### Version 0.4.0
- More template types and placeholders supported; see README.md.

### Version 0.3.1
- Optimize code for faster program execution.

### Version 0.3.0
- Add characters/locations/items export.

### Version 0.2.1
- Add date/time placeholders.

