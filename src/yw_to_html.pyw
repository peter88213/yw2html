"""Export yWriter project to html. 

Version @release

Parameter 1: yWriter Project (full path)
Parameter 2 (optional): template directory

If no template directory is set, templates are searched for in the yWriter project directory.
If no templates are found, the output file will be empty.

Copyright (c) 2020 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""

import sys
import os
import argparse

from pywriter.converter.yw_cnv_gui import YwCnvGui
from pywriter.html.html_export import HtmlExport

from pywriter.file.file_export import FileExport
from pywriter.html.html_fop import read_html_file


class Exporter(HtmlExport):

    # Template files

    _HTML_HEADER = '/html_header.html'

    _CHARACTER_TEMPLATE = '/character_template.html'
    _LOCATION_TEMPLATE = '/location_template.html'
    _ITEM_TEMPLATE = '/item_template.html'

    _HTML_FOOTER = '/html_footer.html'

    _PART_TEMPLATE = '/part_template.html'
    _CHAPTER_TEMPLATE = '/chapter_template.html'
    _UNUSED_CHAPTER_TEMPLATE = '/unused_chapter_template.html'
    _INFO_CHAPTER_TEMPLATE = '/info_chapter_template.html'

    _CHAPTER_END_TEMPLATE = '/chapter_end_template.html'
    _UNUSED_CHAPTER_END_TEMPLATE = '/unused_chapter_end_template.html'
    _INFO_CHAPTER_END_TEMPLATE = '/info_chapter_end_template.html'

    _SCENE_TEMPLATE = '/scene_template.html'
    _UNUSED_SCENE_TEMPLATE = '/unused_scene_template.html'
    _INFO_SCENE_TEMPLATE = '/info_scene_template.html'
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

        result = read_html_file(
            self.templatePath + self._UNUSED_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.unusedChapterTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._INFO_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.infoChapterTemplate = result[1]

        result = read_html_file(self.templatePath + self._CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.chapterEndTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._UNUSED_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.unusedChapterEndTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._INFO_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.infoChapterEndTemplate = result[1]

        # Scene level.

        result = read_html_file(self.templatePath + self._SCENE_TEMPLATE)

        if result[1] is not None:
            self.sceneTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._UNUSED_SCENE_TEMPLATE)

        if result[1] is not None:
            self.unusedSceneTemplate = result[1]

        result = read_html_file(self.templatePath + self._INFO_SCENE_TEMPLATE)

        if result[1] is not None:
            self.infoSceneTemplate = result[1]

        result = read_html_file(self.templatePath + self._SCENE_DIVIDER)

        if result[1] is not None:
            self.sceneDivider = result[1]


def run(sourcePath, templatePath, suffix, silentMode=True):
    fileName, FileExtension = os.path.splitext(sourcePath)

    if FileExtension in ['.yw6', '.yw7']:
        document = Exporter('', templatePath)
        document.SUFFIX = suffix

    else:
        sys.exit('ERROR: File type is not supported.')

    converter = YwCnvGui(sourcePath, document, silentMode)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Export yWriter project to html.')
    parser.add_argument('sourcePath', metavar='Project',
                        help='yWriter project file')
    parser.add_argument('-t', dest='templatePath', metavar='template-dir',
                        help='path to template directory')
    parser.add_argument('-s', dest='suffix', metavar='suffix',
                        help='suffix to output file name')
    args = parser.parse_args()

    if args.templatePath:
        templatePath = args.templatePath

    else:
        templatePath = os.path.dirname(args.sourcePath)

    if templatePath == '':
        templatePath = '.'

    run(args.sourcePath, templatePath, args.suffix, False)
