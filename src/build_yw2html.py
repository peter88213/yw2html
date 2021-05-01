""" Build a python script for the yw2html distribution.
        
In order to distribute a single script without dependencies, 
this script "inlines" all modules imported from the.pyriter package.

The.pyriter project (see see https://github.com/peter88213.pyriter)
must be located on the same directory level as the yW2OO project. 

For further information see https://github.com/peter88213/yW2OO
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import inliner

SRC = '../src/'
BUILD = '../test/'


def main():
    os.chdir(SRC)
    inliner.run('yw_to_html.py', BUILD + 'yw2html.py', 'pywriter')
    print('Done.')


if __name__ == '__main__':
    main()
