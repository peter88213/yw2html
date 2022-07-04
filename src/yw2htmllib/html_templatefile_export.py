"""Provide a class for HTML file representation based on template files.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.html.html_fop import read_html_file
from yw2htmllib.html_export import HtmlExport


class HtmlTemplatefileExport(HtmlExport):
    """Export content or metadata from a yWriter project to a HTML file.
    
    Public methods:
        write() -- write instance variables to the export file.
    
    Read the templates from external HTML flies.
    """

    # Reset default templates.
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _sceneTemplate = ''
    _sceneDivider = ''
    _fileFooter = ''

    # Define template files.
    _HTML_HEADER = 'html_header'
    _CHARACTER_TEMPLATE = 'character_template'
    _LOCATION_TEMPLATE = 'location_template'
    _ITEM_TEMPLATE = 'item_template'
    _HTML_FOOTER = 'html_footer'
    _PART_TEMPLATE = 'part_template'
    _CHAPTER_TEMPLATE = 'chapter_template'
    _CHAPTER_END_TEMPLATE = 'chapter_end_template'
    _UNUSED_CHAPTER_TEMPLATE = 'unused_chapter_template'
    _UNUSED_CHAPTER_END_TEMPLATE = 'unused_chapter_end_template'
    _NOTES_CHAPTER_TEMPLATE = 'notes_chapter_template'
    _NOTES_CHAPTER_END_TEMPLATE = 'notes_chapter_end_template'
    _TODO_CHAPTER_TEMPLATE = 'todo_chapter_template'
    _TODO_CHAPTER_END_TEMPLATE = 'todo_chapter_end_template'
    _SCENE_TEMPLATE = 'scene_template'
    _FIRST_SCENE_TEMPLATE = 'first_scene_template'
    _UNUSED_SCENE_TEMPLATE = 'unused_scene_template'
    _NOTES_SCENE_TEMPLATE = 'notes_scene_template'
    _TODO_SCENE_TEMPLATE = 'todo_scene_template'
    _SCENE_DIVIDER = 'scene_divider'
    _TEMPLATE_CHAPTER_TITLE = 'html templates'

    def __init__(self, filePath, **kwargs):
        """Read templates from files, if any.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            template_path -- str: template directory path.
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        templatePath = kwargs['template_path']

        # Project level.
        __, content = read_html_file(f'{templatePath}/{self._HTML_HEADER}{self.EXTENSION}')
        if content is not None:
            self._fileHeader = content
        __, content = read_html_file(f'{templatePath}/{self._CHARACTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._characterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._LOCATION_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._locationTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._ITEM_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._itemTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._HTML_FOOTER}{self.EXTENSION}')
        if content is not None:
            self._fileFooter = content

        # Chapter level.
        __, content = read_html_file(f'{templatePath}/{self._PART_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._partTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._CHAPTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._chapterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._CHAPTER_END_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._chapterEndTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._UNUSED_CHAPTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._unusedChapterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._UNUSED_CHAPTER_END_TEMPLATE}{self.EXTENSION}')

        if content is not None:
            self._unusedChapterEndTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._NOTES_CHAPTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._notesChapterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._NOTES_CHAPTER_END_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._notesChapterEndTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._TODO_CHAPTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._todoChapterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._TODO_CHAPTER_END_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._todoChapterEndTemplate = content

        # Scene level.
        __, content = read_html_file(f'{templatePath}/{self._SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._sceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._FIRST_SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._firstSceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._UNUSED_SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._unusedSceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._NOTES_SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._notesSceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._TODO_SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._todoSceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._SCENE_DIVIDER}{self.EXTENSION}')
        if content is not None:
            self._sceneDivider = content

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 

        Positional arguments:
            chId -- str: chapter ID.
            chapterNumber -- int: chapter number.

        Extends the superclass method.
        """
        ROMAN = [
            (1000, "M"),
            (900, "CM"),
            (500, "D"),
            (400, "CD"),
            (100, "C"),
            (90, "XC"),
            (50, "L"),
            (40, "XL"),
            (10, "X"),
            (9, "IX"),
            (5, "V"),
            (4, "IV"),
            (1, "I"),
        ]

        def number_to_roman(n):
            """Return n as a Roman number.
            
            Credit goes to the user 'Aristide' on stack overflow.
            https://stackoverflow.com/a/47713392
            """
            result = []
            for (arabic, roman) in ROMAN:
                (factor, n) = divmod(n, arabic)
                result.append(roman * factor)
                if n == 0:
                    break

            return "".join(result)

        TENS = {30: 'thirty', 40: 'forty', 50: 'fifty',
                60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninety'}
        ZERO_TO_TWENTY = (
            'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty'
        )

        def number_to_english(n):
            """Return n as a number written out in English.

            Credit goes to the user 'Hunter_71' on stack overflow.
            https://stackoverflow.com/a/51849443
            """
            if any(not x.isdigit() for x in str(n)):
                return ''

            if n <= 20:
                return ZERO_TO_TWENTY[n]

            elif n < 100 and n % 10 == 0:
                return TENS[n]

            elif n < 100:
                return f'{number_to_english(n - (n % 10))} {number_to_english(n % 10)}'

            elif n < 1000 and n % 100 == 0:
                return f'{number_to_english(n / 100)} hundred'

            elif n < 1000:
                return f'{number_to_english(n / 100)} hundred {number_to_english(n % 100)}'

            elif n < 1000000:
                return f'{number_to_english(n / 1000)} thousand {number_to_english(n % 1000)}'

            return ''

        chapterMapping = super()._get_chapterMapping(chId, chapterNumber)
        if chapterNumber:
            chapterMapping['ChNumberEnglish'] = number_to_english(chapterNumber).capitalize()
            chapterMapping['ChNumberRoman'] = number_to_roman(chapterNumber)
        else:
            chapterMapping['ChNumberEnglish'] = ''
            chapterMapping['ChNumberRoman'] = ''
        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''
        return chapterMapping

    def write(self):
        """Read templates from the source file, if any.

        Extends the superclass constructor.
        """

        def get_template(scId, title):
            """Retrieve a template from a yWriter scene.
            
            Return scene content if title matches. Otherwise return None.
            """
            if self.scenes[scId].title == title:
                content = self.scenes[scId].sceneContent
            else:
                content = None
            return content

        # Find template chapter.
        for chId in self.chapters:
            if not self.chapters[chId].isUnused:
                continue

            if self.chapters[chId].title != self._TEMPLATE_CHAPTER_TITLE:
                continue

            for scId in self.chapters[chId].srtScenes:

                # Project level.
                content = get_template(scId, self._HTML_HEADER)
                if content is not None:
                    self._fileHeader = content
                content = get_template(scId, self._CHARACTER_TEMPLATE)
                if content is not None:
                    self._characterTemplate = content
                content = get_template(scId, self._LOCATION_TEMPLATE)
                if content is not None:
                    self._locationTemplate = content
                content = get_template(scId, self._ITEM_TEMPLATE)
                if content is not None:
                    self._itemTemplate = content
                content = get_template(scId, self._HTML_FOOTER)
                if content is not None:
                    self._fileFooter = content

                # Chapter level.

                content = get_template(scId, self._PART_TEMPLATE)
                if content is not None:
                    self._partTemplate = content
                content = get_template(scId, self._CHAPTER_TEMPLATE)
                if content is not None:
                    self._chapterTemplate = content
                content = get_template(scId, self._CHAPTER_END_TEMPLATE)
                if content is not None:
                    self._chapterEndTemplate = content
                content = get_template(scId, self._UNUSED_CHAPTER_TEMPLATE)
                if content is not None:
                    self._unusedChapterTemplate = content
                content = get_template(scId, self._UNUSED_CHAPTER_END_TEMPLATE)
                if content is not None:
                    self._unusedChapterEndTemplate = content
                content = get_template(scId, self._NOTES_CHAPTER_TEMPLATE)
                if content is not None:
                    self._notesChapterTemplate = content
                content = get_template(scId, self._NOTES_CHAPTER_END_TEMPLATE)
                if content is not None:
                    self._notesChapterEndTemplate = content
                content = get_template(scId, self._TODO_CHAPTER_TEMPLATE)
                if content is not None:
                    self._todoChapterTemplate = content
                content = get_template(scId, self._TODO_CHAPTER_END_TEMPLATE)
                if content is not None:
                    self._todoChapterEndTemplate = content

                # Scene level.
                content = get_template(scId, self._SCENE_TEMPLATE)
                if content is not None:
                    self._sceneTemplate = content
                content = get_template(scId, self._FIRST_SCENE_TEMPLATE)
                if content is not None:
                    self._firstSceneTemplate = content
                content = get_template(scId, self._UNUSED_SCENE_TEMPLATE)
                if content is not None:
                    self._unusedSceneTemplate = content
                content = get_template(scId, self._NOTES_SCENE_TEMPLATE)
                if content is not None:
                    self._notesSceneTemplate = content
                content = get_template(scId, self._TODO_SCENE_TEMPLATE)
                if content is not None:
                    self._todoSceneTemplate = content
                content = get_template(scId, self._SCENE_DIVIDER)
                if content is not None:
                    self._sceneDivider = content
        return (super().write())
