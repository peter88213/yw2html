"""Helper module for HTML file operations.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
from pywriter.pywriter_globals import *


def read_html_file(filePath):
    """Open a html file being encoded utf-8 or ANSI.
    
    Return the file content in a single string. None in case of error.
    Raise the "Error" exception in case of error. 
    """
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        try:
            with open(filePath, 'r') as f:
                content = (f.read())
        except(FileNotFoundError):
            raise Error(f'{_("File not found")}: "{norm_path(filePath)}".')

    return content
