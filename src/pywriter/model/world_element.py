"""Provide a generic class for yWriter story world element representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.model.basic_element import BasicElement


class WorldElement(BasicElement):
    """Story world element representation (may be location or item).
    
    Public instance variables:
        image -- str: image file path.
        tags -- list of tags.
        aka -- str: alternate name.
    """

    def __init__(self):
        """Initialize instance variables.
        
        Extends the superclass constructor.
        """
        super().__init__()

        self.image = None
        # str
        # xml: <ImageFile>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>

