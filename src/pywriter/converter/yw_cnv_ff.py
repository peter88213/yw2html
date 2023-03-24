"""Provide a class for Novel file conversion with file factories.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *
from pywriter.converter.yw_cnv_ui import YwCnvUi
from pywriter.converter.file_factory import FileFactory
from pywriter.converter.export_source_factory import ExportSourceFactory
from pywriter.converter.export_target_factory import ExportTargetFactory
from pywriter.converter.import_source_factory import ImportSourceFactory
from pywriter.converter.import_target_factory import ImportTargetFactory


class YwCnvFf(YwCnvUi):
    """Class for Novel file conversion using factory methods to create target and source classes.

    Public methods:
        run(sourcePath, **kwargs) -- create source and target objects and run conversion.

    Class constants:
        EXPORT_SOURCE_CLASSES -- list of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- list of FileExport subclasses to which export is possible.
        IMPORT_SOURCE_CLASSES -- list of Novel subclasses from which can be imported.
        IMPORT_TARGET_CLASSES -- list of YwFile subclasses to which import is possible.

    All lists are empty and meant to be overridden by subclasses.

    Instance variables:
        exportSourceFactory -- ExportSourceFactory.
        exportTargetFactory -- ExportTargetFactory.
        importSourceFactory -- ImportSourceFactory.
        importTargetFactory -- ImportTargetFactory.
        newProjectFactory -- FileFactory (a stub to be overridden by subclasses).
    """
    EXPORT_SOURCE_CLASSES = []
    EXPORT_TARGET_CLASSES = []
    IMPORT_SOURCE_CLASSES = []
    IMPORT_TARGET_CLASSES = []

    def __init__(self):
        """Create strategy class instances.
        
        Extends the superclass constructor.
        """
        super().__init__()
        self.exportSourceFactory = ExportSourceFactory(self.EXPORT_SOURCE_CLASSES)
        self.exportTargetFactory = ExportTargetFactory(self.EXPORT_TARGET_CLASSES)
        self.importSourceFactory = ImportSourceFactory(self.IMPORT_SOURCE_CLASSES)
        self.importTargetFactory = ImportTargetFactory(self.IMPORT_TARGET_CLASSES)
        self.newProjectFactory = FileFactory()

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath: str -- the source file path.
        
        Required keyword arguments: 
            suffix: str -- target file name suffix.

        This is a template method that calls superclass methods as primitive operations by case.
        """
        self.newFile = None
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'!{_("File not found")}: "{norm_path(sourcePath)}".')
            return

        try:
            source, __ = self.exportSourceFactory.make_file_objects(sourcePath, **kwargs)
        except Error:
            # The source file is not a yWriter project.
            try:
                source, __ = self.importSourceFactory.make_file_objects(sourcePath, **kwargs)
            except Error:
                # A new yWriter project might be required.
                try:
                    source, target = self.newProjectFactory.make_file_objects(sourcePath, **kwargs)
                except Error as ex:
                    self.ui.set_info_how(f'!{str(ex)}')
                else:
                    self.create_yw7(source, target)
            else:
                # Try to update an existing yWriter project.
                kwargs['suffix'] = source.SUFFIX
                try:
                    __, target = self.importTargetFactory.make_file_objects(sourcePath, **kwargs)
                except Error as ex:
                    self.ui.set_info_how(f'!{str(ex)}')
                else:
                    self.import_to_yw(source, target)
        else:
            # The source file is a yWriter project.
            try:
                __, target = self.exportTargetFactory.make_file_objects(sourcePath, **kwargs)
            except Error as ex:
                self.ui.set_info_how(f'!{str(ex)}')
            else:
                self.export_from_yw(source, target)
