"""Build a Python script for the yw2html distribution.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the.pyriter package.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import sys
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = f'{SRC}yw2html_.py'
TARGET_FILE = f'{BUILD}yw2html.py'


def main():
    inliner.run(SOURCE_FILE, TARGET_FILE, 'yw2htmllib', '../src/')
    inliner.run(TARGET_FILE, TARGET_FILE, 'pywriter', '../src/')
    # inliner.run(SOURCE_FILE, TARGET_FILE, 'yw2htmllib', '../src/', copyPyWriter=True)
    # inliner.run(TARGET_FILE, TARGET_FILE, 'pywriter', '../../PyWriter/src/', copyPyWriter=True)
    print('Done.')


if __name__ == '__main__':
    main()
