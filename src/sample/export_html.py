"""Convert yWriter to html format.

This is a yw2html sample application.

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
SUFFIX = ''

import sys

from pywriter.ui.ui_tk import UiTk
from pywriter.converter.yw_cnv_ui import YwCnvUi

from pywriter.yw.yw6_file import Yw6File
from pywriter.yw.yw7_file import Yw7File
from pywhtml.html_export import HtmlExport


class Exporter(YwCnvUi):
    """A converter class for html export."""
    EXPORT_SOURCE_CLASSES = [Yw7File, Yw6File]
    EXPORT_TARGET_CLASSES = [HtmlExport]


def run(sourcePath, suffix=''):
    ui = UiTk('Export html from yWriter')
    converter = Exporter()
    converter.ui = ui
    kwargs = {'suffix': suffix}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    run(sys.argv[1], SUFFIX)
