"""Provide a class for a novel representation.

All classes representing specific file formats inherit from this class.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import locale
import re
from typing import Iterator, Pattern
from pywriter.pywriter_globals import *
from pywriter.model.basic_element import BasicElement
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene
from pywriter.model.world_element import WorldElement
from pywriter.model.character import Character

LANGUAGE_TAG: Pattern = re.compile('\[lang=(.*?)\]')


class Novel(BasicElement):
    """Novel representation.

    This class represents a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        get_languages() -- Determine the languages used in the document.
        check_locale() -- Check the document's locale (language code and country code).

    Public instance variables:
        authorName: str -- author's name.
        author bio: str -- information about the author.
        fieldTitle1: str -- scene rating field title 1.
        fieldTitle2: str -- scene rating field title 2.
        fieldTitle3: str -- scene rating field title 3.
        fieldTitle4: str -- scene rating field title 4.
        chapters: dict -- (key: ID; value: chapter instance).
        scenes: dict -- (key: ID, value: scene instance).
        srtChapters: list -- the novel's sorted chapter IDs.
        locations: dict -- (key: ID, value: WorldElement instance).
        srtLocations: list -- the novel's sorted location IDs.
        items: dict -- (key: ID, value: WorldElement instance).
        srtItems: list -- the novel's sorted item IDs.
        characters: dict -- (key: ID, value: character instance).
        srtCharacters: list -- the novel's sorted character IDs.
        projectNotes: dict --  (key: ID, value: projectNote instance).
        srtPrjNotes: list -- the novel's sorted project notes.
    """

    def __init__(self):
        """Initialize instance variables.
            
        Extends the superclass constructor.          
        """
        super().__init__()

        self.authorName: str = None
        # xml: <PROJECT><AuthorName>

        self.authorBio: str = None
        # xml: <PROJECT><Bio>

        self.fieldTitle1: str = None
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2: str = None
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3: str = None
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4: str = None
        # xml: <PROJECT><FieldTitle4>

        self.wordTarget: int = None
        # xml: <PROJECT><wordTarget>

        self.wordCountStart: int = None
        # xml: <PROJECT><wordCountStart>

        self.wordTarget: int = None
        # xml: <PROJECT><wordCountStart>

        self.chapters: dict[str, Chapter] = {}
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter instance.
        # The order of the elements does not matter (the novel's order of the chapters is defined by srtChapters)

        self.scenes: dict[str, Scene] = {}
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's order of the scenes is defined by
        # the order of the chapters and the order of the scenes within the chapters)

        self.languages: list[str] = None
        # List of non-document languages occurring as scene markup.
        # Format: ll-CC, where ll is the language code, and CC is the country code.

        self.srtChapters: list[str] = []
        # The novel's chapter IDs. The order of its elements corresponds to the novel's order of the chapters.

        self.locations: dict[str, WorldElement] = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtLocations: list[str] = []
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items: dict[str, WorldElement] = {}
        # xml: <ITEMS>
        # key = item ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtItems: list[str] = []
        # The novel's item IDs. The order of its elements corresponds to the XML project file.

        self.characters: dict[str, Character] = {}
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters: list[str] = []
        # The novel's character IDs. The order of its elements corresponds to the XML project file.

        self.projectNotes: dict[str, BasicElement] = {}
        # xml: <PROJECTNOTES>
        # key = note ID, value = note instance.
        # The order of the elements does not matter.

        self.srtPrjNotes: list[str] = []
        # The novel's projectNote IDs. The order of its elements corresponds to the XML project file.

        self.languageCode: str = None
        # Language code acc. to ISO 639-1.

        self.countryCode: str = None
        # Country code acc. to ISO 3166-2.

    def get_languages(self):
        """Determine the languages used in the document.
        
        Populate the self.languages list with all language codes found in the scene contents.        
        Example:
        - language markup: 'Standard text [lang=en-AU]Australian text[/lang=en-AU].'
        - language code: 'en-AU'
        """

        def languages(text: str) -> Iterator[str]:
            """Return the language codes appearing in text.
            
            Example:
            - language markup: 'Standard text [lang=en-AU]Australian text[/lang=en-AU].'
            - language code: 'en-AU'
            """
            if text:
                m = LANGUAGE_TAG.search(text)
                while m:
                    text = text[m.span()[1]:]
                    yield m.group(1)
                    m = LANGUAGE_TAG.search(text)

        self.languages = []
        for scId in self.scenes:
            text = self.scenes[scId].sceneContent
            if text:
                for language in languages(text):
                    if not language in self.languages:
                        self.languages.append(language)

    def check_locale(self):
        """Check the document's locale (language code and country code).
        
        If the locale is missing, set the system locale.  
        If the locale doesn't look plausible, set "no language".        
        """
        if not self.languageCode:
            # Language isn't set.
            try:
                sysLng, sysCtr = locale.getlocale()[0].split('_')
            except:
                # Fallback for old Windows versions.
                sysLng, sysCtr = locale.getdefaultlocale()[0].split('_')
            self.languageCode = sysLng
            self.countryCode = sysCtr
            return

        try:
            # Plausibility check: code must have two characters.
            if len(self.languageCode) == 2:
                if len(self.countryCode) == 2:
                    return
                    # keep the setting
        except:
            # code isn't a string
            pass
        # Existing language or country field looks not plausible
        self.languageCode = 'zxx'
        self.countryCode = 'none'

