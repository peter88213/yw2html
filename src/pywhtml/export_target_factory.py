"""Provide a project specific factory class for any export target object.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os

from pywriter.converter.file_factory import FileFactory


class ExportTargetFactory(FileFactory):
    """A factory class that instantiates an export target file object."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to any format.

        Return a tuple with three elements:
        - A message string starting with 'SUCCESS' or 'ERROR'
        - sourceFile: None
        - targetFile: a FileExport subclass instance, or None in case of error 
        """
        fileName, fileExtension = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']

        for fileClass in self.fileClasses:

            if suffix is None:
                suffix = ''

            targetFile = fileClass(fileName + suffix + fileClass.EXTENSION, **kwargs)
            return 'SUCCESS', None, targetFile

        return f'ERROR: File type of "{os.path.normpath(sourcePath)}" not supported.', None, None
