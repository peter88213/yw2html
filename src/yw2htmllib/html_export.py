"""Provide a class for HTML file representation.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
from pywriter.file.file_export import FileExport


class HtmlExport(FileExport):
    """HTML file representation.
    
    Provide basic HTML templates for exporting chapters and scenes.
    """
    DESCRIPTION = 'HTML export'
    EXTENSION = '.html'
    SCENE_DIVIDER = '* * *'

    _fileHeader = '''<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>

<style type="text/css">
h1, h2, h3, h4, p {font: 1em monospace; margin: 3em; line-height: 1.5em}
h1, h2, h3, h4 {text-align: center}
h1 {letter-spacing: 0.5em; font-style: italic}
h1, h2 {font-weight: bold}
h3 {font-style: italic}
p {margin-top:0; margin-bottom:0}
p+p {margin-top:0; margin-bottom:0; text-indent: 1em}
p.title {text-align:center; font-weight:normal; text-transform: uppercase}
p.author {text-align:center; font-weight:normal}
p.scenedivider {text-align:center; margin: 1.5em; line-height: 1.5em}
strong {font-weight:normal; text-transform: uppercase}
</style>

<title>$Title</title>
</head>

<body>
<p class=title><strong>$Title</strong></p>
<p class=author>by</p>
<p class=author>$AuthorName</p>

'''

    _partTemplate = '''<h1><a name="ChID:$ID" />$Title</h1>
'''

    _chapterTemplate = '''<h2><a name="ChID:$ID" />$Title</h2>
'''

    _sceneTemplate = '''<a name="ScID:$ID" /><!-- ${Title} -->
<p>$SceneContent</p>
'''

    _sceneDivider = f'<p class="scenedivider">{SCENE_DIVIDER}</p>'

    _fileFooter = '''</body>
</html>
'''

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to HTML markup.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if quick:
            # Just clean up a one-liner without sophisticated formatting.
            if text is None:
                return ''
            else:
                return text

        if text:
            # Remove inline code.
            YW_SPECIAL_CODES = ('HTM', 'TEX', 'RTF', 'epub', 'mobi', 'rtfimg', 'RTFBRK')
            for specialCode in YW_SPECIAL_CODES:
                text = re.sub(f'\<{specialCode} .+?\/{specialCode}\>', '', text)

            # Apply html formatting.
            HTML_REPLACEMENTS = [
                ('\n', '</p>\n<p>'),
                ('[i]', '<em>'),
                ('[/i]', '</em>'),
                ('[b]', '<strong>'),
                ('[/b]', '</strong>'),
                ('<p></p>', '<p><br /></p>'),
                ('/*', '<!--'),
                ('*/', '-->'),
            ]
            for yw, htm in HTML_REPLACEMENTS:
                text = text.replace(yw, htm)

            # Remove highlighting, alignment,
            # strikethrough, and underline tags.
            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)
        else:
            text = ''
        return(text)
