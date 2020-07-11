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

* $ID - Chapter ID,
* $ChapterNumber - Chapter number (in sort order),


* $Title - Chapter title
* $Desc - Chapter description, html-formatted

### "Scene template" placeholders

* $ID - Scene ID,
* $SceneNumber - Scene number (in sort order),


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


* $Date - Specific scene date ("None" if not set)
* $Time - Specific scene time ("None" if not set)
* $Day - Time scene begins: day ("None" if not set)
* $Hour - Time scene begins: hour ("None" if not set)
* $Minute - Time scene begins: minute ("None" if not set)
* $LastsDays - Amount of time scene lasts: days ("None" if not set)
* $LastsHours - Amount of time scene lasts: hours ("None" if not set)
* $LastsMinutes - Amount of time scene lasts: minutes ("None" if not set)


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


### "Character template" placeholders

* $ID - Character ID


* $Title - Character's name
* $FullName - Character's full name)
* $AKA - Alternative name


* $Status - Major/minor character
* $Tags - Character tags


* $Desc - Character description
* $Bio - The character's biography
* $Goals - The character's goals in the story
* $Notes - Character notes)


### "Location template" placeholders

* $ID - Location ID


* $Title - Location's name
* $AKA - Alternative name
* $Desc - Location description
* $Tags - Location tags


### "Item template" placeholders

* $ID - Item ID


* $Title - Item's name
* $AKA - Alternative name
* $Desc - Item description
* $Tags - Item tags



