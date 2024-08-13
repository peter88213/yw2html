"""Provide a class for yWriter scene representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
from pywriter.model.basic_element import BasicElement
from pywriter.pywriter_globals import *

#--- Regular expressions for counting words and characters like in LibreOffice.
# See: https://help.libreoffice.org/latest/en-GB/text/swriter/guide/words_count.html

ADDITIONAL_WORD_LIMITS = re.compile('--|—|–')
# this is to be replaced by spaces, thus making dashes and dash replacements word limits

NO_WORD_LIMITS = re.compile('\[.+?\]|\/\*.+?\*\/|-|^\>', re.MULTILINE)
# this is to be replaced by empty strings, thus excluding markup and comments from
# word counting, and making hyphens join words

NON_LETTERS = re.compile('\[.+?\]|\/\*.+?\*\/|\n|\r')
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
        scnArcs: str -- Semicolon-separated arc titles.
        scnMode: str -- Mode of discourse (Narration/Dramatic action/Dialogue/Description/Exposition).
    """
    STATUS = [None,
                    'Outline',
                    'Draft',
                    '1st Edit',
                    '2nd Edit',
                    'Done'
                    ]
    # Emulate an enumeration for the scene status
    # Since the items are used to replace text,
    # they may contain spaces. This is why Enum cannot be used here.

    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'
    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self._sceneContent = None
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.wordCount = 0
        # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.scType = None
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

        self.doNotExport = None
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # xml: <Status>
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        # See also the STATUS list for conversion.

        self.notes = None
        # xml: <Notes>

        self.tags = None
        # xml: <Tags>

        self.field1 = None
        # xml: <Field1>

        self.field2 = None
        # xml: <Field2>

        self.field3 = None
        # xml: <Field3>

        self.field4 = None
        # xml: <Field4>

        self.appendToPrev = None
        # xml: <AppendToPrev> -1

        self.isReactionScene = None
        # xml: <ReactionScene> -1

        self.isSubPlot = None
        # xml: <SubPlot> -1

        self.goal = None
        # xml: <Goal>

        self.conflict = None
        # xml: <Conflict>

        self.outcome = None
        # xml: <Outcome>

        self.characters = None
        # xml: <Characters><CharID>

        self.locations = None
        # xml: <Locations><LocID>

        self.items = None
        # xml: <Items><ItemID>

        self.date = None
        # yyyy-mm-dd
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time = None
        # hh:mm:ss
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.day = None
        # xml: <Day>

        self.lastsMinutes = None
        # xml: <LastsMinutes>

        self.lastsHours = None
        # xml: <LastsHours>

        self.lastsDays = None
        # xml: <LastsDays>

        self.image = None
        # xml: <ImageFile>

        self.scnArcs = None
        # xml: <Field_SceneArcs>
        # Semicolon-separated arc titles.
        # Example: 'A' for 'A-Storyline'.
        # If the scene is "Todo" type, an assigned single arc
        # should be defined by it.

        self.scnMode = None
        # xml: <Field_SceneMode>
        # Mode of discourse.

    @property
    def sceneContent(self):
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
