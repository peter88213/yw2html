"""Provide the base class for Novel file conversion.

All converters inherit from this class. 

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *


class YwCnv:
    """Base class for Novel file conversion.

    Public methods:
        convert(sourceFile, targetFile) -- Convert sourceFile into targetFile.
    """

    def convert(self, source, target):
        """Convert source into target and return a message.

        Positional arguments:
            source, target -- Novel subclass instances.

        Operation:
        1. Make the source object read the source file.
        2. Make the target object merge the source object's instance variables.
        3. Make the target object write the target file.
        Return a message beginning with the ERROR constant in case of error.

        Error handling:
        - Check if source and target are correctly initialized.
        - Ask for permission to overwrite target.
        - Pass the error messages of the called methods of source and target.
        - The success message comes from target.write(), if called.       
        """
        if source.filePath is None:
            return f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(source.filePath)}".'

        if not os.path.isfile(source.filePath):
            return f'{ERROR}{_("File not found")}: "{os.path.normpath(source.filePath)}".'

        if target.filePath is None:
            return f'{ERROR}{_("File type is not supported")}: "{os.path.normpath(target.filePath)}".'

        if os.path.isfile(target.filePath) and not self._confirm_overwrite(target.filePath):
            return f'{ERROR}{_("Action canceled by user")}.'

        message = source.read()
        if message.startswith(ERROR):
            return message

        message = target.merge(source)
        if message.startswith(ERROR):
            return message

        return target.write()

    def _confirm_overwrite(self, fileName):
        """Return boolean permission to overwrite the target file.
        
        Positional argument:
            fileName -- path to the target file.
        
        This is a stub to be overridden by subclass methods.
        """
        return True
