[Project home page](index) > Changelog

------------------------------------------------------------------------

## Changelog

### v2.0.4 Consider inline code

- Remove inline code when exporting.

Based on PyWriter v5.12.5

### v2.0.3 Improved word counting

- Fix word counting considering ellipses.

Based on PyWriter v5.12.4

### v2.0.2 Improved word counting

- Fix word counting considering comments, hyphens, and dashes.

Based on PyWriter v5.12.3

### v2.0.1

- Improve code and documentation quality.

Based on PyWriter v5.0.2

### v2.0.0

- Fix a bug where "To do" chapters cause an exception.
- Fix a regression from v1.6.3 where the example files are unreadable.
- Optionally, specify the HTML templates as yWriter scenes.
- Add $AuthorBio placeholder.
- Improve the overall code quality.

Based on PyWriter v5.0.0

### v1.8.0 Drop the support of the .yw6 file format.

Since yWriter5, yWriter6 and yWriter7 all use .yw7 now, the .yw6 conversion is dispensable.

Based on PyWriter v3.28.2

### v1.6.3 Bugfix release

This release is strongly recommended.
Fix a regression from PyWriter v3.12.5. causing a crash if a scene has an 
hour, but no minute set.

Based on PyWriter v3.16.4

### v1.6.2 Bugfix

- Fix _NOTES_SCENE_TEMPLATE file name.
- Preprocess date/time information before export.
- Add more examples.

Based on PyWriter v3.12.5

### v1.6.1 Fix "chapter end" template processing

Based on PyWriter v3.12.3

### v1.6.0 Add a special template for scenes at the beginning of the chapter

New:
- first_scene_template.html

Based on PyWriter v3.12.0

### v1.4.0 Add alternative chapter count designs

New: 
- $ChNumberEnglish: Chapter number written out in English
- $ChNumberRoman: Chapter number in Roman numbers

Based on PyWriter v3.10.2

### v1.2.2 Optional update

- Major refactoring of the yw7 file processing.

Based on PyWriter v3.8.0

### v1.2.1 Optional update

This update is recommended for Linux users. It makes the "Open" button
work on non-Windows operating systems.

- Make the YwCnvUi.open_newFile() method os-independent.

Based on PyWriter v3.6.7

### v1.2.0 Optional update

- Update the underlying class library with changed API for better maintainability.

Based on PyWriter v3.0.0

### v1.1.2 Bugfix

Fix a bug setting the suffix erroneously to None.

Based on PyWriter v2.17.4 (development version)


### v1.1.0 Make GUI customization easier

The converter is now even more loosely coupled with its user interface. 
This should make it easier for application developers to customize user interaction, 
and use any GUI framework.

Based on PyWriter v2.17.0 (development version)


### v1.0.1 Optional update

Refactor the code
- Move the HtmlExport class to the Pywriter library.
- Replace it by the MyExport subclass.

Based on PyWriter v2.15.1


### v1.0.0 Rename the script and change the user interface

- Change the script's file extension from `.pyw` to `.py` and implement a command line-only UI.

__Please note:__  If you update yw2html, be sure to change the extensions in your existing custom batch files.

Based on PyWriter 2.14.4


### v0.10.0 Improve the processing of comma-separated lists

- Fix incorrectly defined tags during yWriter import.
- Protect the processing of comma-separated lists against wrongly set
  blanks.

Based on PyWriter 2.14.1


### v0.9.0 Underline and strikethrough no longer supported

That is because a real support would require considering nesting and 
multi paragraph formatting. That would make everything too complicated, 
considering that such formatting is not common in a fictional prose text.

Based on PyWriter v2.9.0

### v0.8.0

Process all yWriter formatting tags.
- Convert underline and strikethrough.
- Discard alignment.
- Discard highlighting.

Based on PyWriter v2.8.0

### v0.7.2

- Refactor and update docstrings.
- Work around a yWriter 7.1.1.2 bug.
- Development: Create test execution directory if necessary

### v0.7.1

- Improve screen output.
- Refactor the code for better maintainability.

### v0.6.0
Adapt to modified yw7 file format (yWriter 7.0.7.2+):
- "Info" chapters are replaced by "Notes" chapters (always unused).
- New "Todo" chapter type (always unused). 
- Distinguish between "Notes scene", "Todo scene" and "Unused scene".
- Chapter/scene tag colors in "proofread" export correspond to those of the yWriter chapter list.

### v0.5.2
- Fix import of uncomplete date/time information.
- Add shebang for Linux use.
- Change line breaks to Unix.

### v0.5.1
- Replace "None" entries by nullstrings.
- Add "Timeline" template example.

### v0.5.0 
- New command line user interface (see README.md).
- More sophisticated examples.

### v0.4.0
- More template types and placeholders supported; see README.md.

### v0.3.1
- Optimize code for faster program execution.

### v0.3.0
- Add characters/locations/items export.

### v0.2.1
- Add date/time placeholders.

