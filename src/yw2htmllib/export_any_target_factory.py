"""Provide a project specific factory class for any export target object.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *
from pywriter.converter.file_factory import FileFactory


class ExportAnyTargetFactory(FileFactory):
    """A factory class that instantiates an export target file object."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to any format.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Optional arguments:
            suffix -- str: an indicator for the target file type.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with two elements:
        - sourceFile: None
        - targetFile: a FileExport subclass instance

        Raise the "Error" exception in case of error.          
        """
        fileName, __ = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']
        for fileClass in self._fileClasses:
            if suffix is None:
                suffix = ''
            targetFile = fileClass(f'{fileName}{suffix}{fileClass.EXTENSION}', **kwargs)
            return None, targetFile

        raise Error(f'File type of "{os.path.normpath(sourcePath)}" not supported.')
