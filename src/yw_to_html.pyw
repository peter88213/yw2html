#!/usr/bin/env python3
"""Export yWriter project to html. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
import os
import argparse

from pywriter.converter.yw_cnv_tk import YwCnvTk
from pywriter.file.file_export import FileExport
from pywriter.html.html_fop import read_html_file
from pywriter.converter.file_factory import FileFactory
from pywriter.yw.yw6_file import Yw6File
from pywriter.yw.yw7_file import Yw7File


class HtmlExport(FileExport):
    """Export content or metadata from an yWriter project to a HTML file.
    """

    DESCRIPTION = 'HTML export'
    EXTENSION = '.html'

    # Template files

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
    _UNUSED_SCENE_TEMPLATE = '/unused_scene_template.html'
    _NOTES_SCENE_TEMPLATE = '/info_scene_template.html'
    _TODO_SCENE_TEMPLATE = '/todo_scene_template.html'
    _SCENE_DIVIDER = '/scene_divider.html'

    def __init__(self, filePath, templatePath='.'):
        FileExport.__init__(self, filePath)

        # Initialize templates.

        self.templatePath = templatePath

        # Project level.

        result = read_html_file(self.templatePath + self._HTML_HEADER)

        if result[1] is not None:
            self.fileHeader = result[1]

        result = read_html_file(self.templatePath + self._CHARACTER_TEMPLATE)

        if result[1] is not None:
            self.characterTemplate = result[1]

        result = read_html_file(self.templatePath + self._LOCATION_TEMPLATE)

        if result[1] is not None:
            self.locationTemplate = result[1]

        result = read_html_file(self.templatePath + self._ITEM_TEMPLATE)

        if result[1] is not None:
            self.itemTemplate = result[1]

        result = read_html_file(self.templatePath + self._HTML_FOOTER)

        if result[1] is not None:
            self.fileFooter = result[1]

        # Chapter level.

        result = read_html_file(self.templatePath + self._PART_TEMPLATE)

        if result[1] is not None:
            self.partTemplate = result[1]

        result = read_html_file(self.templatePath + self._CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.chapterTemplate = result[1]

        result = read_html_file(self.templatePath + self._CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.chapterEndTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._UNUSED_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.unusedChapterTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._UNUSED_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.unusedChapterEndTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._NOTES_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.notesChapterTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._NOTES_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.notesChapterEndTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._TODO_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.todoChapterTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._TODO_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.todoChapterEndTemplate = result[1]

        # Scene level.

        result = read_html_file(self.templatePath + self._SCENE_TEMPLATE)

        if result[1] is not None:
            self.sceneTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._UNUSED_SCENE_TEMPLATE)

        if result[1] is not None:
            self.unusedSceneTemplate = result[1]

        result = read_html_file(self.templatePath + self._NOTES_SCENE_TEMPLATE)

        if result[1] is not None:
            self.notesSceneTemplate = result[1]

        result = read_html_file(self.templatePath + self._TODO_SCENE_TEMPLATE)

        if result[1] is not None:
            self.todoSceneTemplate = result[1]

        result = read_html_file(self.templatePath + self._SCENE_DIVIDER)

        if result[1] is not None:
            self.sceneDivider = result[1]

    def convert_from_yw(self, text):
        """Convert yw7 markup to HTML.
        """
        HTML_REPLACEMENTS = [
            ['\n', '</p>\n<p>'],
            ['[i]', '<em>'],
            ['[/i]', '</em>'],
            ['[b]', '<strong>'],
            ['[/b]', '</strong>'],
            ['<p></p>', '<p><br /></p>'],
            ['/*', '<!--'],
            ['*/', '-->'],
        ]

        try:

            for r in HTML_REPLACEMENTS:
                text = text.replace(r[0], r[1])

            # Remove highlighting, alignment,
            # strikethrough, and underline tags.

            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)

        except AttributeError:
            text = ''

        return(text)


class HtmlFileFactory(FileFactory):
    """A factory class that instantiates a source file object
    and a target file object for conversion.
    """

    def __init__(self, templatePath):
        self.templatePath = templatePath

    def get_file_objects(self, sourcePath, suffix=''):
        """Return a tuple with three elements:
        * A message string starting with 'SUCCESS' or 'ERROR'
        * sourceFile: a Novel subclass instance
        * targetFile: a Novel subclass instance
        """
        fileName, fileExtension = os.path.splitext(sourcePath)

        if fileExtension == Yw7File.EXTENSION:
            sourceFile = Yw7File(sourcePath)

        elif fileExtension == Yw6File.EXTENSION:
            sourceFile = Yw6File(sourcePath)

        else:
            return 'ERROR: File type is not supported.', None, None

        targetFile = HtmlExport(fileName + suffix +
                                HtmlExport.EXTENSION, self.templatePath)
        targetFile.SUFFIX = suffix

        return 'SUCCESS', sourceFile, targetFile


class Converter(YwCnvTk):
    """yWriter converter with a simple tkinter GUI. 
    """

    def __init__(self, silentMode, templatePath):
        YwCnvTk.__init__(self, silentMode)
        self.fileFactory = HtmlFileFactory(templatePath)


def run(sourcePath, templatePath, suffix, silentMode=True):
    Converter(silentMode, templatePath).run(sourcePath, suffix)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Export yWriter project to html.',
        epilog='If no template directory is set, templates are searched for in the yWriter project directory. If no templates are found, the output file will be empty.')
    parser.add_argument('sourcePath', metavar='Project',
                        help='yWriter project file')
    parser.add_argument('-t', dest='templatePath', metavar='template-dir',
                        help='path to the directory containing the templates')
    parser.add_argument('-s', dest='suffix', metavar='suffix',
                        help='suffix to the output file name (optional)')
    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()

    if args.templatePath:
        templatePath = args.templatePath

    else:
        templatePath = os.path.dirname(args.sourcePath)

    if args.templatePath is not None:
        templatePath = args.templatePath

    else:
        templatePath = os.path.dirname(args.sourcePath)

    if templatePath == '':
        templatePath = '.'

    if args.suffix is not None:
        suffix = args.suffix

    else:
        suffix = ''

    if args.silent:
        silentMode = True

    else:
        silentMode = False

    run(args.sourcePath, templatePath, suffix, silentMode)
