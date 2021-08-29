""" Build a python script for the yw2html distribution.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the.pyriter package.

The.pyriter project (see see https://github.com/peter88213.pyriter)
must be located on the same directory level as the yw2html project. 

For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import inliner

SRC = '../src/'
BUILD = '../test/'
SOURCE_FILE = 'yw2html_.py'
TARGET_FILE = BUILD + 'yw2html.py'


def main():
    os.chdir(SRC)

    try:
        os.remove(TARGET_FILE)

    except:
        pass

    inliner.run(SOURCE_FILE,
                TARGET_FILE, 'pywhtml', '../src/')
    inliner.run(TARGET_FILE,
                TARGET_FILE, 'pywriter', '../../PyWriter/src/')
    print('Done.')


if __name__ == '__main__':
    main()
