"""Provide a class for yWriter to HTML conversion.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ff import YwCnvFf
from pywriter.yw.yw7_file import Yw7File

from pywhtml.html_templatefile_export import HtmlTemplatefileExport
from pywhtml.export_any_target_factory import ExportAnyTargetFactory

class HtmlExporter(YwCnvFf):
    """A converter class for html export."""
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [HtmlTemplatefileExport]

    def __init__(self):
        """Extend the superclass constructor.

        Override exportTargetFactory by a project
        specific implementation that accepts all
        suffixes. 
        """
        super().__init__()
        self.exportTargetFactory = ExportAnyTargetFactory(self.EXPORT_TARGET_CLASSES)


