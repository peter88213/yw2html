#!/usr/bin/python3
"""Export yWriter project to html. 

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse
from pywriter.ui.ui import Ui
from pywriter.ui.ui_cmd import UiCmd
from yw2htmllib.html_exporter import HtmlExporter


def run(sourcePath, templatePath, suffix, silentMode=True):
    if silentMode:
        ui = Ui('')
    else:
        ui = UiCmd('Export html from yWriter')
    converter = HtmlExporter()
    converter.ui = ui
    kwargs = {'suffix': suffix, 'template_path': templatePath}
    converter.run(sourcePath, **kwargs)
    ui.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Export yWriter project to html.',
        epilog='If no template directory is set, templates are searched for in the yWriter project directory. If no templates are found, the output file will be empty.')
    parser.add_argument('sourcePath', metavar='Project',
                        help='yWriter project file')
    parser.add_argument('-t', dest='templatePath', metavar='template-dir',
                        help='path to the directory containing the templates')
    parser.add_argument('-s', dest='suffix', metavar='suffix',
                        help='suffix to the output file name (optional)')
    parser.add_argument('--silent',
                        action="store_true",
                        help='suppress error messages and the request to confirm overwriting')
    args = parser.parse_args()
    if args.templatePath:
        templatePath = args.templatePath
    else:
        templatePath = os.path.dirname(args.sourcePath)
    if args.templatePath is not None:
        templatePath = args.templatePath
    else:
        templatePath = os.path.dirname(args.sourcePath)
    if not templatePath:
        templatePath = '.'
    if args.suffix is not None:
        suffix = args.suffix
    else:
        suffix = ''
    run(args.sourcePath, templatePath, suffix, args.silent)
