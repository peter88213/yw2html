"""Provide global variables and functions.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
import gettext
import locale

ERROR = '!'

# Initialize localization.
LOCALE_PATH = f'{os.path.dirname(sys.argv[0])}/locale/'
CURRENT_LANGUAGE = locale.getdefaultlocale()[0][:2]
try:
    t = gettext.translation('pywriter', LOCALE_PATH, languages=[CURRENT_LANGUAGE])
    _ = t.gettext
except:

    def _(message):
        return message


def string_to_list(text, divider=';'):
    """Convert a string into a list.
    
    Positional arguments:
        text -- string containing divider-separated substrings.
        
    Optional arguments:
        divider -- string that divides the substrings.
    
    Split a string into a list of strings.
    Remove leading and trailing spaces, if any.
    Return a list of strings.
    """
    elements = []
    tempList = text.split(divider)
    for element in tempList:
        element = element.strip()
        if element and not element in elements:
            elements.append(element)
    return elements


def list_to_string(elements, divider=';'):
    """Join strings from a list.
    
    Positional arguments:
        elements -- list of elements to be concatenated.
        
    Optional arguments:
        divider -- string that divides the substrings.
    
    Return a string which is the concatenation of the 
    members of the list of strings "elements", separated by 
    a comma plus a space. The space allows word wrap in 
    spreadsheet cells.
    """
    text = divider.join(elements)
    return text


__all__ = ['ERROR', '_', 'LOCALE_PATH', 'CURRENT_LANGUAGE', 'string_to_list', 'list_to_string']
