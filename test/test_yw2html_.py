"""Regression test for the yw2html project.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import unittest
import yw2html_
from shutil import copyfile

# Test environment

# The paths are relative to the "test" directory,
# where this script is placed and executed

TEST_PATH = os.getcwd() + '/../test'
TEST_DATA_PATH = TEST_PATH + '/data/'
TEST_EXEC_PATH = TEST_PATH + '/yw7/'
TEMPLATE_PATH = '../../template/'

# To be placed in TEST_DATA_PATH:

# Test data
YW7 = 'normal.yw7'
YW7_INCL = 'with_templates.yw7'
PAPERBACK = 'normal_paperback.html'
SCENELIST = 'normal_scenelist.html'
SCRIPT = 'normal_manuscript.html'
CHARAS = 'normal_characters.html'


def read_file(inputFile):
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        with open(inputFile, 'r') as f:
            return f.read()


def remove_all_testfiles():
    try:
        os.remove(TEST_EXEC_PATH + YW7)
    except:
        pass
    try:
        os.remove(TEST_EXEC_PATH + SCENELIST)
    except:
        pass
    try:
        os.remove(TEST_EXEC_PATH + SCRIPT)
    except:
        pass
    try:
        os.remove(TEST_EXEC_PATH + CHARAS)
    except:
        pass
    try:
        os.remove(TEST_EXEC_PATH + PAPERBACK)
    except:
        pass


class NormalOperation(unittest.TestCase):
    """Test case: Normal operation."""

    def setUp(self):
        try:
            os.mkdir(TEST_EXEC_PATH)
        except:
            pass
        remove_all_testfiles()
        copyfile(TEST_DATA_PATH + YW7, TEST_EXEC_PATH + YW7)

    def test_scenelist(self):
        os.chdir(TEST_EXEC_PATH)
        yw2html_.run(TEST_EXEC_PATH + YW7, TEMPLATE_PATH +
                     'scenelist', '_scenelist', True)
        self.assertEqual(read_file(TEST_EXEC_PATH + SCENELIST),
                         read_file(TEST_DATA_PATH + SCENELIST))

    def test_script(self):
        os.chdir(TEST_EXEC_PATH)
        yw2html_.run(TEST_EXEC_PATH + YW7, TEMPLATE_PATH +
                     'manuscript', '_manuscript', True)
        self.assertEqual(read_file(TEST_EXEC_PATH + SCRIPT),
                         read_file(TEST_DATA_PATH + SCRIPT))

    def test_characters(self):
        os.chdir(TEST_EXEC_PATH)
        yw2html_.run(TEST_EXEC_PATH + YW7, TEMPLATE_PATH +
                     'characters', '_characters', True)
        self.assertEqual(read_file(TEST_EXEC_PATH + CHARAS),
                         read_file(TEST_DATA_PATH + CHARAS))

    def test_templates_included(self):
        os.chdir(TEST_EXEC_PATH)
        copyfile(TEST_DATA_PATH + YW7_INCL, TEST_EXEC_PATH + YW7)
        yw2html_.run(TEST_EXEC_PATH + YW7, '', '_paperback', True)
        self.assertEqual(read_file(TEST_EXEC_PATH + PAPERBACK),
                         read_file(TEST_DATA_PATH + PAPERBACK))

    def tearDown(self):
        remove_all_testfiles()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
