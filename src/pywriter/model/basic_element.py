"""Provide a generic class for yWriter element representation.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""


class BasicElement:
    """Basic element representation (may be a project note).
    
    Public instance variables:
        title: str -- title (name).
        desc: str -- description.
        kwVar: dict -- custom keyword variables.
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # xml: <Title>

        self.desc = None
        # xml: <Desc>

        self.kwVar = {}
        # Optional key/value instance variables for customization.
