"""Provide a class for yWriter to HTML conversion.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.converter.yw_cnv_ff import YwCnvFf
from pywriter.yw.yw7_file import Yw7File

from yw2htmllib.html_templatefile_export import HtmlTemplatefileExport
from yw2htmllib.export_any_target_factory import ExportAnyTargetFactory

class HtmlExporter(YwCnvFf):
    """A converter class for html export.

    Class constants:
        EXPORT_SOURCE_CLASSES -- List of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- List of FileExport subclasses to which export is possible.
    """
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [HtmlTemplatefileExport]

    def __init__(self):
        """Extends the superclass constructor.

        Delegate the exportTargetFactory to a project
        specific class that accepts all suffixes.
        Extends the superclass constructor.
        """
        super().__init__()
        self.exportTargetFactory = ExportAnyTargetFactory(self.EXPORT_TARGET_CLASSES)


