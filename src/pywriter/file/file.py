"""Provide an abstract class for file representation.

All classes representing specific file formats inherit from this class.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from abc import ABC
from urllib.parse import quote
import os
from pywriter.pywriter_globals import *


class File(ABC):
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        read() -- Parse the file and get the instance variables.
        write() -- Write instance variables to the file.

    Public instance variables:
        projectName: str -- URL-coded file name without suffix and extension. 
        projectPath: str -- URL-coded path to the project directory. 
        scenesSplit: bool -- True, if a scene or chapter is split during merging.
        filePath: str -- path to the file (property with getter and setter). 

    Public class constants:
        PRJ_KWVAR -- List of the names of the project keyword variables.
        CHP_KWVAR -- List of the names of the chapter keyword variables.
        SCN_KWVAR -- List of the names of the scene keyword variables.
        CRT_KWVAR -- List of the names of the character keyword variables.
        LOC_KWVAR -- List of the names of the location keyword variables.
        ITM_KWVAR -- List of the names of the item keyword variables.
        PNT_KWVAR -- List of the names of the project note keyword variables.
    """
    DESCRIPTION = _('File')
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    PRJ_KWVAR = []
    CHP_KWVAR = []
    SCN_KWVAR = []
    CRT_KWVAR = []
    LOC_KWVAR = []
    ITM_KWVAR = []
    PNT_KWVAR = []
    # Keyword variables for custom fields in the .yw7 XML file.

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath: str -- path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.  
        """
        self.novel = None

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a supported type as specified by EXTENSION.

        self.projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self.projectPath = None
        # str
        # URL-coded path to the project directory.

        self.scenesSplit = False
        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.
                
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            try:
                head, tail = os.path.split(os.path.realpath(filePath))
                # realpath() completes relative paths, but may not work on virtual file systems.
            except:
                head, tail = os.path.split(filePath)
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        """Parse the file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        This is a stub to be overridden by subclass methods.
        """
        raise NotImplementedError

    def write(self):
        """Write instance variables to the file.
        
        Raise the "Error" exception in case of error. 
        This is a stub to be overridden by subclass methods.
        """
        raise NotImplementedError

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick: bool -- if True, apply a conversion mode for one-liners without formatting.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()

    def _convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        This is a stub to be overridden by subclass methods.
        """
        return text.rstrip()

