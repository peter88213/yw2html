# yw2html - HTML export with templates from yWriter 6/7

The yw2html Python script runs through all chapters and scenes of a yWriter 6/7 project and fills HTML templates.

![Screenshot: Example](https://raw.githubusercontent.com/peter88213/yw2html/master/docs/Screenshots/manuscript.png)

## Requirements

* [Python 3.4+](https://www.python.org)
* yWriter 6 or [yWriter 7](http://spacejock.com/yWriter7.html)

## Download

The yw2html Software comes as a zipfile `yw2html_<version number>.zip`. 

[Download page](https://github.com/peter88213/yw2html/releases/latest)


## Usage

`yw2html.pyw <yWriter Project> <optional: template directory>`

If no template directory is set, templates are searched for in the yWriter project directory.
If no templates are found, the output file will be empty.

## Conventions

### "HTML header" placeholders

* $Title - Project title
* $Desc - Project description, html-formatted
* $AuthorName - Author's name
* $FieldTitle1 - Rating names: field 1
* $FieldTitle2 - Rating names: field 2
* $FieldTitle3 - Rating names: field 3
* $FieldTitle4 - Rating names: field 4

### "Chapter template" placeholders

* $Title - Chapter title
* $Desc - Chapter description, html-formatted

### "Scene template" placeholders

* $Title - Scene title
* $Desc - Scene description, html-formatted
* $WordCount - Scene word count
* $WordsTotal - Accumulated word count including the current scene
* $LetterCount - Scene letter count
* $LettersTotal - Accumulated letter count including the current scene
* $Status - Scene status (Outline, Draft etc.)
* $SceneContent - Scene content, html-formatted
* $FieldTitle1 - Rating names: field 1
* $FieldTitle2 - Rating names: field 2
* $FieldTitle3 - Rating names: field 3
* $FieldTitle4 - Rating names: field 4
* $Field1 - Scene rating: field 1
* $Field2 - Scene rating: field 2
* $Field3 - Scene rating: field 3
* $Field4 - Scene rating: field 4
* $ReactionScene - A(ction) or R(eaction)
* $Goal - The scene protagonist's goal, html-formatted
* $Conflict - The scene conflict, html-formatted
* $Outcome - The scene outcome, html-formatted
* $Tags - Comma-separated list of scene tags
* $Characters - Comma-separated list of characters assigned to the scene
* $Viewpoint - Viewpoint character
* $Locations - Comma-separated list of locations assigned to the scene
* $Items - Comma-separated list of items assigned to the scene
* $Notes - Scene notes, html-formatted

* $Date - Specific scene date ("None" if not set)
* $Time - Specific scene time ("None" if not set)
* $Day - Time scene begins: day ("None" if not set)
* $Hour - Time scene begins: hour ("None" if not set)
* $Minute - Time scene begins: minute ("None" if not set)
* $LastsDays - Amount of time scene lasts: days ("None" if not set)
* $LastsHours - Amount of time scene lasts: hours ("None" if not set)
* $LastsMinutes - Amount of time scene lasts: minutes ("None" if not set)

