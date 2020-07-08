"""Export yWriter project to html. 

Copyright (c) 2020 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""

import sys
import os

from pywriter.converter.yw_cnv_gui import YwCnvGui
from pywriter.html.html_export import HtmlExport


def run(sourcePath, silentMode=True, stripChapterFromTitle=False):
    fileName, FileExtension = os.path.splitext(sourcePath)

    if FileExtension in ['.yw6', '.yw7']:
        document = HtmlExport('')
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
    run(sourcePath, False, True)
