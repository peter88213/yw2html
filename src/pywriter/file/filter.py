"""Provide a generic filter class for template-based file export.

All specific filters inherit from this class.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""


class Filter:
    """Filter an entity (chapter/scene/character/location/item) by filter criteria.
    
    Public methods:
        accept(source, eId) -- check whether an entity matches the filter criteria.
    
    Strategy class, implementing filtering criteria for template-based export.
    This is a stub with no filter criteria specified.
    """

    def accept(self, source, eId):
        """Check whether an entity matches the filter criteria.
        
        Positional arguments:
            source -- Novel instance holding the entity to check.
            eId -- ID of the entity to check.       
        
        Return True if the entity is not to be filtered out.
        This is a stub to be overridden by subclass methods implementing filters.
        """
        return True
