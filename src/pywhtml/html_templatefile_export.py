"""Provide a class for HTML file representation based on template files.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.html.html_fop import read_html_file
from pywhtml.html_export import HtmlExport

class HtmlTemplatefileExport(HtmlExport):
    """Export content or metadata from a yWriter project to a HTML file.
    
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

    _HTML_HEADER = '/html_header.html'

    _CHARACTER_TEMPLATE = '/character_template.html'
    _LOCATION_TEMPLATE = '/location_template.html'
    _ITEM_TEMPLATE = '/item_template.html'

    _HTML_FOOTER = '/html_footer.html'

    _PART_TEMPLATE = '/part_template.html'

    _CHAPTER_TEMPLATE = '/chapter_template.html'
    _CHAPTER_END_TEMPLATE = '/chapter_end_template.html'

    _UNUSED_CHAPTER_TEMPLATE = '/unused_chapter_template.html'
    _UNUSED_CHAPTER_END_TEMPLATE = '/unused_chapter_end_template.html'

    _NOTES_CHAPTER_TEMPLATE = '/notes_chapter_template.html'
    _NOTES_CHAPTER_END_TEMPLATE = '/notes_chapter_end_template.html'

    _TODO_CHAPTER_TEMPLATE = '/todo_chapter_template.html'
    _TODO_CHAPTER_END_TEMPLATE = '/todo_chapter_end_template.html'

    _SCENE_TEMPLATE = '/scene_template.html'
    _FIRST_SCENE_TEMPLATE = '/first_scene_template.html'
    _UNUSED_SCENE_TEMPLATE = '/unused_scene_template.html'
    _NOTES_SCENE_TEMPLATE = '/notes_scene_template.html'
    _TODO_SCENE_TEMPLATE = '/todo_scene_template.html'
    _SCENE_DIVIDER = '/scene_divider.html'

    def __init__(self, filePath, **kwargs):
        """Read templates from files, if any.

        Extend the superclass constructor.
        """
        super().__init__(filePath)
        templatePath = kwargs['templatePath']

        # Project level.

        __, content = read_html_file(f'{templatePath}{self._HTML_HEADER}')

        if content is not None:
            self._fileHeader = content

        __, content = read_html_file(f'{templatePath}{self._CHARACTER_TEMPLATE}')

        if content is not None:
            self._characterTemplate = content

        __, content = read_html_file(f'{templatePath}{self._LOCATION_TEMPLATE}')

        if content is not None:
            self._locationTemplate = content

        __, content = read_html_file(f'{templatePath}{self._ITEM_TEMPLATE}')

        if content is not None:
            self._itemTemplate = content

        __, content = read_html_file(f'{templatePath}{self._HTML_FOOTER}')

        if content is not None:
            self._fileFooter = content

        # Chapter level.

        __, content = read_html_file(f'{templatePath}{self._PART_TEMPLATE}')

        if content is not None:
            self._partTemplate = content

        __, content = read_html_file(f'{templatePath}{self._CHAPTER_TEMPLATE}')

        if content is not None:
            self._chapterTemplate = content

        __, content = read_html_file(f'{templatePath}{self._CHAPTER_END_TEMPLATE}')

        if content is not None:
            self._chapterEndTemplate = content

        __, content = read_html_file(f'{templatePath}{self._UNUSED_CHAPTER_TEMPLATE}')

        if content is not None:
            self._unusedChapterTemplate = content

        __, content = read_html_file(f'{templatePath}{self._UNUSED_CHAPTER_END_TEMPLATE}')

        if content is not None:
            self._unusedChapterEndTemplate = content

        __, content = read_html_file(f'{templatePath}{self._NOTES_CHAPTER_TEMPLATE}')

        if content is not None:
            self._notesChapterTemplate = content

        __, content = read_html_file(f'{templatePath}{self._NOTES_CHAPTER_END_TEMPLATE}')

        if content is not None:
            self._notesChapterEndTemplate = content

        __, content = read_html_file(f'{templatePath}{self._TODO_CHAPTER_TEMPLATE}')

        if content is not None:
            self._todoChapterTemplate = content

        __, content = read_html_file(f'{templatePath}{self._TODO_CHAPTER_END_TEMPLATE}')

        if content is not None:
            self._todoChapterEndTemplate = content

        # Scene level.

        __, content = read_html_file(f'{templatePath}{self._SCENE_TEMPLATE}')

        if content is not None:
            self._sceneTemplate = content

        __, content = read_html_file(f'{templatePath}{self._FIRST_SCENE_TEMPLATE}')

        if content is not None:
            self._firstSceneTemplate = content

        __, content = read_html_file(f'{templatePath}{self._UNUSED_SCENE_TEMPLATE}')

        if content is not None:
            self._unusedSceneTemplate = content

        __, content = read_html_file(f'{templatePath}{self._NOTES_SCENE_TEMPLATE}')

        if content is not None:
            self._notesSceneTemplate = content

        __, content = read_html_file(f'{templatePath}{self._TODO_SCENE_TEMPLATE}')

        if content is not None:
            self._todoSceneTemplate = content

        __, content = read_html_file(f'{templatePath}{self._SCENE_DIVIDER}')

        if content is not None:
            self._sceneDivider = content

