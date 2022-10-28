"""Provide a class for Novel file conversion with user interface.

All converters with a user interface inherit from this class. 

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
from pywriter.pywriter_globals import *
from pywriter.file.doc_open import open_document
from pywriter.ui.ui import Ui
from pywriter.converter.yw_cnv import YwCnv


class YwCnvUi(YwCnv):
    """Base class for Novel file conversion with user interface.

    Public methods:
        export_from_yw(sourceFile, targetFile) -- Convert from yWriter project to other file format.
        create_yw(sourceFile, targetFile) -- Create target from source.
        import_to_yw(sourceFile, targetFile) -- Convert from any file format to yWriter project.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        newFile -- str: path to the target file in case of success.   
    """

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.
        self.newFile = None
        # Also indicates successful conversion.

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, os.path.normpath(source.filePath), target.DESCRIPTION, os.path.normpath(target.filePath)))
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath

    def create_yw7(self, source, target):
        """Create target from source.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf target already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Create a yWriter project file from {0}\nNew project: "{1}"').format(source.DESCRIPTION, os.path.normpath(target.filePath)))
        if os.path.isfile(target.filePath):
            self.ui.set_info_how(f'{ERROR}{_("File already exists")}: "{os.path.normpath(target.filePath)}".')
        else:
            message = self.convert(source, target)
            self.ui.set_info_how(message)
            self._delete_tempfile(source.filePath)
            if message.startswith(ERROR):
                self.newFile = None
            else:
                self.newFile = target.filePath

    def import_to_yw(self, source, target):
        """Convert from any file format to yWriter project.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            _('Input: {0} "{1}"\nOutput: {2} "{3}"').format(source.DESCRIPTION, os.path.normpath(source.filePath), target.DESCRIPTION, os.path.normpath(target.filePath)))
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        self._delete_tempfile(source.filePath)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath
            if target.scenesSplit:
                self.ui.show_warning(_('New scenes created during conversion.'))

    def _confirm_overwrite(self, filePath):
        """Return boolean permission to overwrite the target file.
        
        Positional arguments:
            fileName -- path to the target file.
        
        Overrides the superclass method.
        """
        return self.ui.ask_yes_no(_('Overwrite existing file "{}"?').format(os.path.normpath(filePath)))

    def _delete_tempfile(self, filePath):
        """Delete filePath if it is a temporary file no longer needed."""
        if filePath.endswith('.html'):
            # Might it be a temporary text document?
            if os.path.isfile(filePath.replace('.html', '.odt')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass
        elif filePath.endswith('.csv'):
            # Might it be a temporary spreadsheet document?
            if os.path.isfile(filePath.replace('.csv', '.ods')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass

    def _open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        open_document(self.newFile)
        sys.exit(0)
