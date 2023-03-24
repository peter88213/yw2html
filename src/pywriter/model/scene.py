"""Provide a class for yWriter scene representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
from typing import Pattern
from pywriter.model.basic_element import BasicElement
from pywriter.pywriter_globals import *

#--- Regular expressions for counting words and characters like in LibreOffice.
# See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html

ADDITIONAL_WORD_LIMITS: Pattern = re.compile('--|—|–')
# this is to be replaced by spaces, thus making dashes and dash replacements word limits

NO_WORD_LIMITS: Pattern = re.compile('\[.+?\]|\/\*.+?\*\/|-|^\>', re.MULTILINE)
# this is to be replaced by empty strings, thus excluding markup and comments from
# word counting, and making hyphens join words

NON_LETTERS: Pattern = re.compile('\[.+?\]|\/\*.+?\*\/|\n|\r')
# this is to be replaced by empty strings, thus excluding markup, comments, and linefeeds
# from letter counting


class Scene(BasicElement):
    """yWriter scene representation.
    
    Public instance variables:
        sceneContent: str -- scene content (property with getter and setter).
        wordCount: int -- word count (derived; updated by the sceneContent setter).
        letterCount: int -- letter count (derived; updated by the sceneContent setter).
        scType: int -- Scene type (Normal/Notes/Todo/Unused).
        doNotExport: bool -- True if the scene is not to be exported to RTF.
        status: int -- scene status (Outline/Draft/1st Edit/2nd Edit/Done).
        notes: str -- scene notes in a single string.
        tags -- list of scene tags. 
        field1: int -- scene ratings field 1.
        field2: int -- scene ratings field 2.
        field3: int -- scene ratings field 3.
        field4: int -- scene ratings field 4.
        appendToPrev: bool -- if True, append the scene without a divider to the previous scene.
        isReactionScene: bool -- if True, the scene is "reaction". Otherwise, it's "action". 
        isSubPlot: bool -- if True, the scene belongs to a sub-plot. Otherwise it's main plot.  
        goal: str -- the main actor's scene goal. 
        conflict: str -- what hinders the main actor to achieve his goal.
        outcome: str -- what comes out at the end of the scene.
        characters -- list of character IDs related to this scene.
        locations -- list of location IDs related to this scene. 
        items -- list of item IDs related to this scene.
        date: str -- specific start date in ISO format (yyyy-mm-dd).
        time: str -- specific start time in ISO format (hh:mm).
        minute: str -- unspecific start time: minutes.
        hour: str -- unspecific start time: hour.
        day: str -- unspecific start time: day.
        lastsMinutes: str -- scene duration: minutes.
        lastsHours: str -- scene duration: hours.
        lastsDays: str -- scene duration: days. 
        image: str --  path to an image related to the scene. 
    """
    STATUS: set = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')
    # Emulate an enumeration for the scene status
    # Since the items are used to replace text,
    # they may contain spaces. This is why Enum cannot be used here.

    ACTION_MARKER: str = 'A'
    REACTION_MARKER: str = 'R'
    NULL_DATE: str = '0001-01-01'
    NULL_TIME: str = '00:00:00'

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self._sceneContent: str = None
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.wordCount: int = 0
        # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount: int = 0
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.scType: int = None
        # Scene type (Normal/Notes/Todo/Unused).
        #
        # xml: <Unused>
        # xml: <Fields><Field_SceneType>
        #
        # This is how yWriter 7.1.3.0 reads the scene type:
        #
        # Type   |<Unused>|Field_SceneType>|scType
        #--------+--------+----------------+------
        # Notes  | x      | 1              | 1
        # Todo   | x      | 2              | 2
        # Unused | -1     | N/A            | 3
        # Unused | -1     | 0              | 3
        # Normal | N/A    | N/A            | 0
        # Normal | N/A    | 0              | 0
        #
        # This is how yWriter 7.1.3.0 writes the scene type:
        #
        # Type   |<Unused>|Field_SceneType>|scType
        #--------+--------+----------------+------
        # Normal | N/A    | N/A            | 0
        # Notes  | -1     | 1              | 1
        # Todo   | -1     | 2              | 2
        # Unused | -1     | 0              | 3

        self.doNotExport: bool = None
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status: int = None
        # xml: <Status>
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        # See also the STATUS list for conversion.

        self.notes: str = None
        # xml: <Notes>

        self.tags: list[str] = None
        # xml: <Tags>

        self.field1: str = None
        # xml: <Field1>

        self.field2: str = None
        # xml: <Field2>

        self.field3: str = None
        # xml: <Field3>

        self.field4: str = None
        # xml: <Field4>

        self.appendToPrev: bool = None
        # xml: <AppendToPrev> -1

        self.isReactionScene: bool = None
        # xml: <ReactionScene> -1

        self.isSubPlot: bool = None
        # xml: <SubPlot> -1

        self.goal: str = None
        # xml: <Goal>

        self.conflict: str = None
        # xml: <Conflict>

        self.outcome: str = None
        # xml: <Outcome>

        self.characters: list[str] = None
        # xml: <Characters><CharID>

        self.locations: list[str] = None
        # xml: <Locations><LocID>

        self.items: list[str] = None
        # xml: <Items><ItemID>

        self.date: str = None
        # yyyy-mm-dd
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time: str = None
        # hh:mm:ss
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.day: str = None
        # xml: <Day>

        self.lastsMinutes: str = None
        # xml: <LastsMinutes>

        self.lastsHours: str = None
        # xml: <LastsHours>

        self.lastsDays: str = None
        # xml: <LastsDays>

        self.image: str = None
        # xml: <ImageFile>

        self.scnArcs: str = None
        # xml: <Field_SceneArcs>
        # Semicolon-separated arc titles.
        # Example: 'A' for 'A-Storyline'.
        # If the scene is "Todo" type, an assigned single arc
        # should be defined by it.

        self.scnStyle: str = None
        # xml: <Field_SceneStyle>
        # May be 'explaining', 'descriptive', or 'summarizing'.
        # None is the default, meaning 'staged'.

    @property
    def sceneContent(self) -> str:
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text: str):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = ADDITIONAL_WORD_LIMITS.sub(' ', text)
        text = NO_WORD_LIMITS.sub('', text)
        wordList = text.split()
        self.wordCount = len(wordList)
        text = NON_LETTERS.sub('', self._sceneContent)
        self.letterCount = len(text)
