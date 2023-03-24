"""Provide a class for yWriter character representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
from pywriter.model.world_element import WorldElement


class Character(WorldElement):
    """yWriter character representation.

    Public instance variables:
        notes: str -- character notes.
        bio: str -- character biography.
        goals: str -- character's goals in the story.
        fullName: str -- full name (the title inherited may be a short name).
        isMajor: bool -- True, if it's a major character.
    """
    MAJOR_MARKER: str = 'Major'
    MINOR_MARKER: str = 'Minor'

    def __init__(self):
        """Extends the superclass constructor by adding instance variables."""
        super().__init__()

        self.notes: str = None
        # xml: <Notes>

        self.bio: str = None
        # xml: <Bio>

        self.goals: str = None
        # xml: <Goals>

        self.fullName: str = None
        # xml: <FullName>

        self.isMajor: bool = None
        # xml: <Major>
