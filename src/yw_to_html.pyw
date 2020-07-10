"""Export yWriter project to html. 

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

from pywriter.converter.yw_cnv_gui import YwCnvGui
from pywriter.html.html_export import HtmlExport


def run(sourcePath, templatePath, silentMode=True):
    fileName, FileExtension = os.path.splitext(sourcePath)

    if FileExtension in ['.yw6', '.yw7']:
        document = HtmlExport('', templatePath)
        extension = 'html'

    else:
        sys.exit('ERROR: File type is not supported.')

    converter = YwCnvGui(sourcePath, document,
                         extension, silentMode, '')


if __name__ == '__main__':

    try:
        sourcePath = sys.argv[1]

    except:
        sourcePath = ''

    try:
        templatePath = sys.argv[2]

    except:
        templatePath = os.path.dirname(sourcePath)

    if templatePath == '':
        templatePath = '.'

    run(sourcePath, templatePath, False)
