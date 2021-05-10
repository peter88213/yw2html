"""Export yWriter project to html. 

Copyright (c) 2021 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re

from pywriter.file.file_export import FileExport


class HtmlExport(FileExport):
    """Export content or metadata from an yWriter project to a HTML file.
    """

    DESCRIPTION = 'HTML export'
    EXTENSION = '.html'

    SCENE_DIVIDER = '* * *'

    fileHeader = '''<html>
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

    partTemplate = '''<h1><a name="ChID:$ID" />$Title</h1>
'''

    chapterTemplate = '''<h2><a name="ChID:$ID" />$Title</h2>
'''

    sceneTemplate = '''<a name="ScID:$ID" /><!-- ${Title} -->
<p>$SceneContent</p>
'''

    sceneDivider = '<p class="scenedivider">' + SCENE_DIVIDER + '</p>'

    fileFooter = '''</body>
</html>
'''

    def get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 
        """
        chapterMapping = FileExport.get_chapterMapping(
            self, chId, chapterNumber)

        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''

        return chapterMapping

    def convert_from_yw(self, text):
        """Convert yw7 markup to HTML.
        """
        HTML_REPLACEMENTS = [
            ['\n', '</p>\n<p>'],
            ['[i]', '<em>'],
            ['[/i]', '</em>'],
            ['[b]', '<strong>'],
            ['[/b]', '</strong>'],
            ['<p></p>', '<p><br /></p>'],
            ['/*', '<!--'],
            ['*/', '-->'],
        ]

        try:

            for r in HTML_REPLACEMENTS:
                text = text.replace(r[0], r[1])

            # Remove highlighting, alignment,
            # strikethrough, and underline tags.

            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)

        except AttributeError:
            text = ''

        return(text)
