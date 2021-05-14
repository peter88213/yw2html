#!/usr/bin/env python3
"""Export yWriter project to html. 

Version @release

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse

from pywriter.ui.ui import Ui
from pywriter.ui.ui_cmd import UiCmd
from pywriter.html.html_fop import read_html_file

from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.yw.yw6_file import Yw6File
from pywriter.yw.yw7_file import Yw7File
from pywhtml.export_target_factory import ExportTargetFactory
from pywhtml.html_export import HtmlExport


class MyExport(HtmlExport):
    """Export content or metadata from an yWriter project to a HTML file.
    """

    # Reset default templates.

    fileHeader = ''
    partTemplate = ''
    chapterTemplate = ''
    sceneTemplate = ''
    sceneDivider = ''
    fileFooter = ''

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
    _UNUSED_SCENE_TEMPLATE = '/unused_scene_template.html'
    _NOTES_SCENE_TEMPLATE = '/info_scene_template.html'
    _TODO_SCENE_TEMPLATE = '/todo_scene_template.html'
    _SCENE_DIVIDER = '/scene_divider.html'

    def __init__(self, filePath, **kwargs):
        """Initialize templates.

        Extend the superclass constructor.
        """
        HtmlExport.__init__(self, filePath)

        templatePath = kwargs['templatePath']

        # Project level.

        result = read_html_file(templatePath + self._HTML_HEADER)

        if result[1] is not None:
            self.fileHeader = result[1]

        result = read_html_file(templatePath + self._CHARACTER_TEMPLATE)

        if result[1] is not None:
            self.characterTemplate = result[1]

        result = read_html_file(templatePath + self._LOCATION_TEMPLATE)

        if result[1] is not None:
            self.locationTemplate = result[1]

        result = read_html_file(templatePath + self._ITEM_TEMPLATE)

        if result[1] is not None:
            self.itemTemplate = result[1]

        result = read_html_file(templatePath + self._HTML_FOOTER)

        if result[1] is not None:
            self.fileFooter = result[1]

        # Chapter level.

        result = read_html_file(templatePath + self._PART_TEMPLATE)

        if result[1] is not None:
            self.partTemplate = result[1]

        result = read_html_file(templatePath + self._CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.chapterTemplate = result[1]

        result = read_html_file(templatePath + self._CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.chapterEndTemplate = result[1]

        result = read_html_file(
            templatePath + self._UNUSED_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.unusedChapterTemplate = result[1]

        result = read_html_file(
            templatePath + self._UNUSED_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.unusedChapterEndTemplate = result[1]

        result = read_html_file(
            templatePath + self._NOTES_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.notesChapterTemplate = result[1]

        result = read_html_file(
            templatePath + self._NOTES_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.notesChapterEndTemplate = result[1]

        result = read_html_file(
            templatePath + self._TODO_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.todoChapterTemplate = result[1]

        result = read_html_file(
            templatePath + self._TODO_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.todoChapterEndTemplate = result[1]

        # Scene level.

        result = read_html_file(templatePath + self._SCENE_TEMPLATE)

        if result[1] is not None:
            self.sceneTemplate = result[1]

        result = read_html_file(
            templatePath + self._UNUSED_SCENE_TEMPLATE)

        if result[1] is not None:
            self.unusedSceneTemplate = result[1]

        result = read_html_file(templatePath + self._NOTES_SCENE_TEMPLATE)

        if result[1] is not None:
            self.notesSceneTemplate = result[1]

        result = read_html_file(templatePath + self._TODO_SCENE_TEMPLATE)

        if result[1] is not None:
            self.todoSceneTemplate = result[1]

        result = read_html_file(templatePath + self._SCENE_DIVIDER)

        if result[1] is not None:
            self.sceneDivider = result[1]


class MyExporter(YwCnvUi):
    """A converter class for html export."""
    EXPORT_SOURCE_CLASSES = [Yw7File, Yw6File]
    EXPORT_TARGET_CLASSES = [MyExport]

    def __init__(self):
        """Extend the superclass constructor.

        Override exportTargetFactory by a project
        specific implementation that accepts all
        suffixes. 
        """
        YwCnvUi.__init__(self)
        self.exportTargetFactory = ExportTargetFactory(
            self.EXPORT_TARGET_CLASSES)


def run(sourcePath, templatePath, suffix, silentMode=True):

    if silentMode:
        ui = Ui('')
    else:
        ui = UiCmd('Export html from yWriter')

    converter = MyExporter()
    converter.ui = ui
    kwargs = {'suffix': suffix, 'templatePath': templatePath}
    converter.run(sourcePath, **kwargs)
    ui.start()


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
