[Project homepage](https://peter88213.github.io/yw2html)


The yw2html Python script runs through all chapters and scenes of a yWriter 7 project and fills HTML templates.

## Usage
usage: `yw_to_html.py [-h] [-t template-dir] [-s suffix] [--silent] Project`

#### positional arguments:
 `Project`     yWriter project file

#### optional arguments:
 `-h, --help`    show a help message and exit
 
 `-t template-dir` template directory
 
 `-s suffix`    suffix to output file name
 
 `--silent`     suppress error messages and the request to confirm overwriting

If no template directory is set, templates are searched for in the yWriter project directory.

If no templates are found, the output file will be empty.

## Define templates "internally" in yWriter (optional)

yw2html looks for a unused chapter named **html templates**. HTML templates can be placed there as scenes.
The title of the scene is the same as the name of the template file would be, but without the *.html* extension.
External HTML templates are overridden by internally defined templates, if any.

In the release zipfile, you find a yWriter sample project with internally defined HTML templates in the `examples\add-on` subdirectory.

## Examples
The downloaded zip file includes a directory named *examples* containing a *template* directory with example templates for different purposes and some example batch files showing the correct commands. You can launch the batch files by dragging and dropping your yWriter project on the icons. The results will be written to the yWriter project directory.


## List of templates

### Project level templates

- **html_header.html** 

- **character_template.html** (applied to characters)
- **location_template.html** (applied to locations)
- **item_template.html** (applied to items)

- **html_footer.html** 

### Chapter level templates

- **part_template.html** (chapter header; applied to chapters marked "section beginning")
- **chapter_template.html** (chapter header; applied to all "used" and "normal" chapters unless a "part template" exists)
- **unused_chapter_template.html** (chapter header; applied to chapters marked "unused" or "do not export")
- **notes_chapter_template.html** (chapter header; applied to chapters marked "notes")
- **todo_chapter_template.html** (chapter header; applied to chapters marked "todo")

- **chapter_end_template.html** (chapter footer; applied to all "used" and "normal" chapters)
- **unused_chapter_end_template.html** (chapter footer; applied to chapters marked "unused" or "do not export")
- **notes_chapter_end_template.html** (chapter footer; applied to chapters marked "notes")
- **todo_chapter_end_template.html** (chapter footer; applied to chapters marked "todo")


### Scene level templates

- **scene_template.html** (applied to "used" scenes within "normal" chapters)
- **first_scene_template.html** (applied  to scenes at the beginning of the chapter)
- **unused_scene_template.html** (applied to "unused" scenes)
- **notes_scene_template.html** (applied to scenes marked "notes")
- **todo_scene_template.html** (applied to scenes marked "todo")
- **scene_divider.html** (lead scenes, beginning from the second in chapter)




## Placeholders

### Syntax

There are two options:

1. $Placeholder
2. ${Placeholder}


### "HTML header" placeholders

- **$Title** - Project title
- **$Desc** - Project description, html-formatted
- **$AuthorName** - Author's name
- **$AuthorBio** - Author's biography

- **$FieldTitle1** - Rating names: field 1
- **$FieldTitle2** - Rating names: field 2
- **$FieldTitle3** - Rating names: field 3
- **$FieldTitle4** - Rating names: field 4

### "Chapter template" placeholders

- **$ID** - Chapter ID,
- **$ChapterNumber** - Chapter number (in sort order),
- **$ChNumberEnglish** - Chapter number written out in English (capitalized),
- **$ChNumberRoman** - Chapter number in Roman numbers (uppercase),

- **$Title** - Chapter title
- **$Desc** - Chapter description, html-formatted

### "Scene template" placeholders

- **$ID** - Scene ID,
- **$SceneNumber** - Scene number (in sort order),

- **$Title** - Scene title
- **$Desc** - Scene description, html-formatted

- **$WordCount** - Scene word count
- **$WordsTotal** - Accumulated word count including the current scene
- **$LetterCount** - Scene letter count
- **$LettersTotal** - Accumulated letter count including the current scene

- **$Status** - Scene status (Outline, Draft etc.)
- **$SceneContent** - Scene content, html-formatted

- **$FieldTitle1** - Rating names: field 1
- **$FieldTitle2** - Rating names: field 2
- **$FieldTitle3** - Rating names: field 3
- **$FieldTitle4** - Rating names: field 4
- **$Field1** - Scene rating: field 1
- **$Field2** - Scene rating: field 2
- **$Field3** - Scene rating: field 3
- **$Field4** - Scene rating: field 4

- **$Date** - Specific scene date
- **$Time** - Specific scene time
- **$Day** - Time scene begins: day
- **$Hour** - Time scene begins: hour
- **$Minute** - Time scene begins: minute
- **$LastsDays** - Amount of time scene lasts: days
- **$LastsHours** - Amount of time scene lasts: hours
- **$LastsMinutes** - Amount of time scene lasts: minutes

- **$ReactionScene** - A(ction) or R(eaction)
- **$Goal** - The scene protagonist's goal, html-formatted
- **$Conflict** - The scene conflict, html-formatted
- **$Outcome** - The scene outcome, html-formatted
- **$Tags** - Comma-separated list of scene tags

- **$Characters** - Comma-separated list of characters assigned to the scene
- **$Viewpoint** - Viewpoint character
- **$Locations** - Comma-separated list of locations assigned to the scene
- **$Items** - Comma-separated list of items assigned to the scene

- **$Notes** - Scene notes, html-formatted


### "Character template" placeholders

- **$ID** - Character ID

- **$Title** - Character's name
- **$FullName** - Character's full name)
- **$AKA** - Alternative name

- **$Status** - Major/minor character
- **$Tags** - Character tags

- **$Desc** - Character description
- **$Bio** - The character's biography
- **$Goals** - The character's goals in the story
- **$Notes** - Character notes)


### "Location template" placeholders

- **$ID** - Location ID

- **$Title** - Location's name
- **$AKA** - Alternative name
- **$Desc** - Location description
- **$Tags** - Location tags


### "Item template" placeholders

- **$ID** - Item ID

- **$Title** - Item's name
- **$AKA** - Alternative name
- **$Desc** - Item description
- **$Tags** - Item tags

