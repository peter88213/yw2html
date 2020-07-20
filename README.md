# yw2html__  - HTML export with templates from yWriter 6/7

The yw2html Python script runs through all chapters and scenes of a yWriter 6/7 project and fills HTML templates.

![Screenshot: Example](https://raw.githubusercontent.com/peter88213/yw2html/master/docs/Screenshots/manuscript.png)

## Requirements

* [Python 3.4+](https://www.python.org)
* yWriter 6 or [yWriter 7](http://spacejock.com/yWriter7.html)

## Download

The yw2html Software comes as a zipfile `yw2html_<version number>.zip`. 

[Download page](https://github.com/peter88213/yw2html/releases/latest)


## Usage
usage: `yw_to_html.pyw [-h] [-t template-dir] [-s suffix] Project`

#### positional arguments:
  `Project`          yWriter project file

#### optional arguments:
  `-h, --help`       show a help message and exit
  
  `-t template-dir`  template directory
  
  `-s suffix`        suffix to output file name
  
  `--silent`         suppress error messages and the request to confirm overwriting

If no template directory is set, templates are searched for in the yWriter project directory.

If no templates are found, the output file will be empty.

## Examples
The downloaded zip file includes a directory named  _examples_  containing a  _template_  directory with example templates for different purposes and some example batch files showing the correct commands. You can launch the batch files by dragging and dropping your yWriter project on the icons. The results will be written to the yWriter project directory.


## List of templates

### Project level templates

* __html_header.html__  

* __character_template.html__  (applied to characters)
* __location_template.html__  (applied to locations)
* __item_template.html__  (applied to items)

* __html_footer.html__ 

### Chapter level templates

* __part_template.html__  (chapter header; applied to chapters marked "section beginning")
* __chapter_template.html__  (chapter header; applied to all "used" and "normal" chapters unless a "part template" exists)
* __unused_chapter_template.html__  (chapter header; applied to chapters marked "unused" or "do not export")
* __info_chapter_template.html__  (chapter header; applied to chapters marked "other")

* __chapter_end_template.html__  (chapter footer; applied to all "used" and "normal" chapters)
* __unused_chapter_end_template.html__  (chapter footer; applied to chapters marked "unused" or "do not export")
* __info_chapter_end_template.html__  (chapter footer; applied to chapters marked "other")


### Scene level templates

* __scene_template.html__  (applied to "used" scenes within "normal" chapters)
* __unused_scene_template.html__  (applied to "unused" scenes)
* __info_scene_template.html__  (applied to scenes within chapters marked "other")
* __scene_divider.html__  (lead scenes, beginning from the second in chapter)




## Placeholders

### Syntax

There are two options:

1. $Placeholder
2. ${Placeholder}


### "HTML header" placeholders

*  __$Title__  - Project title
*  __$Desc__  - Project description, html-formatted
*  __$AuthorName__  - Author's name


*  __$FieldTitle1__  - Rating names: field 1
*  __$FieldTitle2__  - Rating names: field 2
*  __$FieldTitle3__  - Rating names: field 3
*  __$FieldTitle4__  - Rating names: field 4

### "Chapter template" placeholders

*  __$ID__  - Chapter ID,
*  __$ChapterNumber__  - Chapter number (in sort order),

*  __$Title__  - Chapter title
*  __$Desc__  - Chapter description, html-formatted

### "Scene template" placeholders

*  __$ID__  - Scene ID,
*  __$SceneNumber__  - Scene number (in sort order),

*  __$Title__  - Scene title
*  __$Desc__  - Scene description, html-formatted

*  __$WordCount__  - Scene word count
*  __$WordsTotal__  - Accumulated word count including the current scene
*  __$LetterCount__  - Scene letter count
*  __$LettersTotal__  - Accumulated letter count including the current scene

*  __$Status__  - Scene status (Outline, Draft etc.)
*  __$SceneContent__  - Scene content, html-formatted

*  __$FieldTitle1__  - Rating names: field 1
*  __$FieldTitle2__  - Rating names: field 2
*  __$FieldTitle3__  - Rating names: field 3
*  __$FieldTitle4__  - Rating names: field 4
*  __$Field1__  - Scene rating: field 1
*  __$Field2__  - Scene rating: field 2
*  __$Field3__  - Scene rating: field 3
*  __$Field4__  - Scene rating: field 4

*  __$Date__  - Specific scene date ("None" if not set)
*  __$Time__  - Specific scene time ("None" if not set)
*  __$Day__  - Time scene begins: day ("None" if not set)
*  __$Hour__  - Time scene begins: hour ("None" if not set)
*  __$Minute__  - Time scene begins: minute ("None" if not set)
*  __$LastsDays__  - Amount of time scene lasts: days ("None" if not set)
*  __$LastsHours__  - Amount of time scene lasts: hours ("None" if not set)
*  __$LastsMinutes__  - Amount of time scene lasts: minutes ("None" if not set)

*  __$ReactionScene__  - A(ction) or R(eaction)
*  __$Goal__  - The scene protagonist's goal, html-formatted
*  __$Conflict__  - The scene conflict, html-formatted
*  __$Outcome__  - The scene outcome, html-formatted
*  __$Tags__  - Comma-separated list of scene tags

*  __$Characters__  - Comma-separated list of characters assigned to the scene
*  __$Viewpoint__  - Viewpoint character
*  __$Locations__  - Comma-separated list of locations assigned to the scene
*  __$Items__  - Comma-separated list of items assigned to the scene

*  __$Notes__  - Scene notes, html-formatted


### "Character template" placeholders

*  __$ID__  - Character ID

*  __$Title__  - Character's name
*  __$FullName__  - Character's full name)
*  __$AKA__  - Alternative name

*  __$Status__  - Major/minor character
*  __$Tags__  - Character tags

*  __$Desc__  - Character description
*  __$Bio__  - The character's biography
*  __$Goals__  - The character's goals in the story
*  __$Notes__  - Character notes)


### "Location template" placeholders

*  __$ID__  - Location ID

*  __$Title__  - Location's name
*  __$AKA__  - Alternative name
*  __$Desc__  - Location description
*  __$Tags__  - Location tags


### "Item template" placeholders

*  __$ID__  - Item ID

*  __$Title__  - Item's name
*  __$AKA__  - Alternative name
*  __$Desc__  - Item description
*  __$Tags__  - Item tags

