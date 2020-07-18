"""Export yWriter project to html. 

Version 0.5.0

positional arguments:
  Project          yWriter project file

optional arguments:
  -h, --help       show this help message and exit
  -t template-dir  path to the directory containing the templates
  -s suffix        suffix to the output file name (optional)

If no template directory is set, templates are searched for in the yWriter
project directory. If no templates are found, the output file will be empty.

Copyright (c) 2020 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""

import sys
import os
import argparse

from tkinter import *
from tkinter import messagebox


import xml.etree.ElementTree as ET

from abc import abstractmethod
from urllib.parse import quote


class Novel():
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).
    """

    EXTENSION = ''
    SUFFIX = ''
    # To be extended by file format specific subclasses.

    def __init__(self, filePath):
        self.title = None
        # str
        # xml: <PROJECT><Title>

        self.desc = None
        # str
        # xml: <PROJECT><Desc>

        self.author = None
        # str
        # xml: <PROJECT><AuthorName>

        self.fieldTitle1 = None
        # str
        # xml: <PROJECT><FieldTitle1>

        self.fieldTitle2 = None
        # str
        # xml: <PROJECT><FieldTitle2>

        self.fieldTitle3 = None
        # str
        # xml: <PROJECT><FieldTitle3>

        self.fieldTitle4 = None
        # str
        # xml: <PROJECT><FieldTitle4>

        self.chapters = {}
        # dict
        # xml: <CHAPTERS><CHAPTER><ID>
        # key = chapter ID, value = Chapter object.
        # The order of the elements does not matter (the novel's
        # order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene object.
        # The order of the elements does not matter (the novel's
        # order of the scenes is defined by the order of the chapters
        # and the order of the scenes within the chapters)

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements
        # corresponds to the novel's order of the chapters.

        self.locations = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = Object.
        # The order of the elements does not matter.

        self.items = {}
        # dict
        # xml: <ITEMS>
        # key = item ID, value = Object.
        # The order of the elements does not matter.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character object.
        # The order of the elements does not matter.

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a
        # supported type as specified by _FILE_EXTENSION.

        self._projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self._projectPath = None
        # str
        # URL-coded path to the project directory.

        self.filePath = filePath

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Accept only filenames with the right extension. """
        if filePath.lower().endswith(self.SUFFIX + self.EXTENSION):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(
                self.SUFFIX + self.EXTENSION, ''))

    @abstractmethod
    def read(self):
        """Parse the file and store selected properties.
        To be overwritten by file format specific subclasses.
        """

    @abstractmethod
    def merge(self, novel):
        """Merge selected novel properties.
        To be overwritten by file format specific subclasses.
        """

    @abstractmethod
    def write(self):
        """Write selected properties to the file.
        To be overwritten by file format specific subclasses.
        """

    @abstractmethod
    def convert_to_yw(self, text):
        """Convert source format to yw7 markup.
        To be overwritten by file format specific subclasses.
        """

    @abstractmethod
    def convert_from_yw(self, text):
        """Convert yw7 markup to target format.
        To be overwritten by file format specific subclasses.
        """

    def file_exists(self):
        """Check whether the file specified by _filePath exists. """
        if os.path.isfile(self._filePath):
            return True

        else:
            return False

    def get_structure(self):
        """returns a string showing the order of chapters and scenes 
        as a tree. The result can be used to compare two Novel objects 
        by their structure.
        """
        lines = []

        for chId in self.srtChapters:
            lines.append('ChID:' + str(chId) + '\n')

            for scId in self.chapters[chId].srtScenes:
                lines.append('  ScID:' + str(scId) + '\n')

        return ''.join(lines)


class Chapter():
    """yWriter chapter representation.
    # xml: <CHAPTERS><CHAPTER>
    """

    stripChapterFromTitle = False
    # bool
    # True: Remove 'Chapter ' from the chapter title upon import.
    # False: Do not modify the chapter title.

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.chLevel = None
        # int
        # xml: <SectionStart>
        # 0 = chapter level
        # 1 = section level ("this chapter begins a section")

        self.chType = None
        # int
        # xml: <Type>
        # 0 = chapter type (marked "Chapter")
        # 1 = other type (marked "Other")

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.suppressChapterTitle = None
        # bool
        # xml: <Fields><Field_SuppressChapterTitle> 1
        # True: Chapter heading not to be displayed in written document.
        # False: Chapter heading to be displayed in written document.

        self.isTrash = None
        # bool
        # xml: <Fields><Field_IsTrash> 1
        # True: This chapter is the yw7 project's "trash bin".
        # False: This chapter is not a "trash bin".

        self.doNotExport = None
        # bool
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes = []
        # list of str
        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.

    def get_title(self):
        """Fix auto-chapter titles for non-English """
        text = self.title

        if self.stripChapterFromTitle:
            text = text.replace('Chapter ', '')

        return text


import re


class Scene():
    """yWriter scene representation.
    # xml: <SCENES><SCENE>
    """

    # Emulate an enumeration for the scene status

    STATUS = [None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done']
    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self._sceneContent = None
        # str
        # xml: <SceneContent>
        # Scene text with yW7 raw markup.

        self.wordCount = 0
        # int # xml: <WordCount>
        # To be updated by the sceneContent setter

        self.letterCount = 0
        # int
        # xml: <LetterCount>
        # To be updated by the sceneContent setter

        self.isUnused = None
        # bool
        # xml: <Unused> -1

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int # xml: <Status>

        self.sceneNotes = None
        # str
        # xml: <Notes>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.field1 = None
        # str
        # xml: <Field1>

        self.field2 = None
        # str
        # xml: <Field2>

        self.field3 = None
        # str
        # xml: <Field3>

        self.field4 = None
        # str
        # xml: <Field4>

        self.appendToPrev = None
        # bool
        # xml: <AppendToPrev> -1

        self.isReactionScene = None
        # bool
        # xml: <ReactionScene> -1

        self.isSubPlot = None
        # bool
        # xml: <SubPlot> -1

        self.goal = None
        # str
        # xml: <Goal>

        self.conflict = None
        # str
        # xml: <Conflict>

        self.outcome = None
        # str
        # xml: <Outcome>

        self.characters = None
        # list of str
        # xml: <Characters><CharID>

        self.locations = None
        # list of str
        # xml: <Locations><LocID>

        self.items = None
        # list of str
        # xml: <Items><ItemID>

        self.date = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.time = None
        # str
        # xml: <SpecificDateMode>-1
        # xml: <SpecificDateTime>1900-06-01 20:38:00

        self.minute = None
        # str
        # xml: <Minute>

        self.hour = None
        # str
        # xml: <Hour>

        self.day = None
        # str
        # xml: <Day>

        self.lastsMinutes = None
        # str
        # xml: <LastsMinutes>

        self.lastsHours = None
        # str
        # xml: <LastsHours>

        self.lastsDays = None
        # str
        # xml: <LastsDays>

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = re.sub('\[.+?\]|\.|\,| -', '', self._sceneContent)
        # Remove yWriter raw markup for word count

        wordList = text.split()
        self.wordCount = len(wordList)

        text = re.sub('\[.+?\]', '', self._sceneContent)
        # Remove yWriter raw markup for letter count

        text = text.replace('\n', '')
        text = text.replace('\r', '')
        self.letterCount = len(text)


class Object():
    """yWriter object representation.
    # xml: <LOCATIONS><LOCATION> or # xml: <ITEMS><ITEM>
    """

    def __init__(self):
        self.title = None
        # str
        # xml: <Title>

        self.desc = None
        # str
        # xml: <Desc>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>


class Character(Object):
    """yWriter character representation.
    # xml: <CHARACTERS><CHARACTER>
    """

    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        Object.__init__(self)

        self.notes = None
        # str
        # xml: <Notes>

        self.bio = None
        # str
        # xml: <Bio>

        self.goals = None
        # str
        # xml: <Goals>

        self.fullName = None
        # str
        # xml: <FullName>

        self.isMajor = None


        # bool
        # xml: <Major>
from html import unescape

EM_DASH = '—'
EN_DASH = '–'
SAFE_DASH = '--'


def replace_unsafe_glyphs(text):
    """Replace glyphs being corrupted by yWriter with safe substitutes. """
    return text.replace(EN_DASH, SAFE_DASH).replace(EM_DASH, SAFE_DASH)


def indent(elem, level=0):
    """xml pretty printer

    Kudos to to Fredrik Lundh. 
    Source: http://effbot.org/zone/element-lib.htm#prettyprint
    """
    i = "\n" + level * "  "

    if len(elem):

        if not elem.text or not elem.text.strip():
            elem.text = i + "  "

        if not elem.tail or not elem.tail.strip():
            elem.tail = i

        for elem in elem:
            indent(elem, level + 1)

        if not elem.tail or not elem.tail.strip():
            elem.tail = i

    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def xml_postprocess(filePath, fileEncoding, cdataTags: list):
    '''Postprocess the xml file created by ElementTree:
       Put a header on top, insert the missing CDATA tags,
       and replace "ampersand" xml entity by plain text.
    '''
    with open(filePath, 'r', encoding=fileEncoding) as f:
        lines = f.readlines()

    newlines = ['<?xml version="1.0" encoding="' + fileEncoding + '"?>\n']

    for line in lines:

        for tag in cdataTags:
            line = re.sub('\<' + tag + '\>', '<' +
                          tag + '><![CDATA[', line)
            line = re.sub('\<\/' + tag + '\>',
                          ']]></' + tag + '>', line)

        newlines.append(line)

    newXml = ''.join(newlines)
    newXml = newXml.replace('[CDATA[ \n', '[CDATA[')
    newXml = newXml.replace('\n]]', ']]')
    newXml = unescape(newXml)

    try:
        with open(filePath, 'w', encoding=fileEncoding) as f:
            f.write(newXml)

    except:
        return 'ERROR: Can not write"' + filePath + '".'

    return 'SUCCESS: "' + filePath + '" written.'


class YwFile(Novel):
    """yWriter xml project file representation."""

    def __init__(self, filePath):
        Novel.__init__(self, filePath)
        self._cdataTags = ['Title', 'AuthorName', 'Bio', 'Desc',
                           'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                           'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                           'AKA', 'ImageFile', 'FullName', 'Goals',
                           'Notes', 'RTFFile', 'SceneContent',
                           'Outcome', 'Goal', 'Conflict']
        # Names of yWriter xml elements containing CDATA.
        # ElementTree.write omits CDATA tags, so they have to be inserted
        # afterwards.

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Accept only filenames with the correct extension. """

        if filePath.lower().endswith('.yw7'):
            self.EXTENSION = '.yw7'
            self._ENCODING = 'utf-8'
            self._filePath = filePath

        elif filePath.lower().endswith('.yw6'):
            self.EXTENSION = '.yw6'
            self._ENCODING = 'utf-8'
            self._filePath = filePath

        elif filePath.lower().endswith('.yw5'):
            self.EXTENSION = '.yw5'
            self._ENCODING = 'iso-8859-1'
            self._filePath = filePath

    def read(self):
        """Parse the yWriter xml file located at filePath, fetching the Novel attributes.
        Return a message beginning with SUCCESS or ERROR.
        """

        # Complete the list of tags requiring CDATA (if incomplete).

        try:
            with open(self._filePath, 'r', encoding=self._ENCODING) as f:
                xmlData = f.read()

        except(FileNotFoundError):
            return 'ERROR: "' + self._filePath + '" not found.'

        lines = xmlData.split('\n')

        for line in lines:
            tag = re.search('\<(.+?)\>\<\!\[CDATA', line)

            if tag is not None:

                if not (tag.group(1) in self._cdataTags):
                    self._cdataTags.append(tag.group(1))

        # Open the file again to let ElementTree parse its xml structure.

        try:
            self._tree = ET.parse(self._filePath)
            root = self._tree.getroot()

        except:
            return 'ERROR: Can not process "' + self._filePath + '".'

        # Read locations from the xml element tree.

        for loc in root.iter('LOCATION'):
            lcId = loc.find('ID').text

            self.locations[lcId] = Object()
            self.locations[lcId].title = loc.find('Title').text

            if loc.find('Desc') is not None:
                self.locations[lcId].desc = loc.find('Desc').text

            if loc.find('AKA') is not None:
                self.locations[lcId].aka = loc.find('AKA').text

            if loc.find('Tags') is not None:

                if loc.find('Tags').text is not None:
                    self.locations[lcId].tags = loc.find(
                        'Tags').text.split(';')

        # Read items from the xml element tree.

        for itm in root.iter('ITEM'):
            itId = itm.find('ID').text

            self.items[itId] = Object()
            self.items[itId].title = itm.find('Title').text

            if itm.find('Desc') is not None:
                self.items[itId].desc = itm.find('Desc').text

            if itm.find('AKA') is not None:
                self.items[itId].aka = itm.find('AKA').text

            if itm.find('Tags') is not None:

                if itm.find('Tags').text is not None:
                    self.items[itId].tags = itm.find(
                        'Tags').text.split(';')

        # Read characters from the xml element tree.

        for crt in root.iter('CHARACTER'):
            crId = crt.find('ID').text

            self.characters[crId] = Character()
            self.characters[crId].title = crt.find('Title').text

            if crt.find('Desc') is not None:
                self.characters[crId].desc = crt.find('Desc').text

            if crt.find('AKA') is not None:
                self.characters[crId].aka = crt.find('AKA').text

            if crt.find('Tags') is not None:

                if crt.find('Tags').text is not None:
                    self.characters[crId].tags = crt.find(
                        'Tags').text.split(';')

            if crt.find('Notes') is not None:
                self.characters[crId].notes = crt.find('Notes').text

            if crt.find('Bio') is not None:
                self.characters[crId].bio = crt.find('Bio').text

            if crt.find('Goals') is not None:
                self.characters[crId].goals = crt.find('Goals').text

            if crt.find('FullName') is not None:
                self.characters[crId].fullName = crt.find('FullName').text

            if crt.find('Major') is not None:
                self.characters[crId].isMajor = True

            else:
                self.characters[crId].isMajor = False

        # Read attributes at novel level from the xml element tree.

        prj = root.find('PROJECT')
        self.title = prj.find('Title').text

        if prj.find('AuthorName') is not None:
            self.author = prj.find('AuthorName').text

        if prj.find('Desc') is not None:
            self.desc = prj.find('Desc').text

        if prj.find('FieldTitle1') is not None:
            self.fieldTitle1 = prj.find('FieldTitle1').text

        if prj.find('FieldTitle2') is not None:
            self.fieldTitle2 = prj.find('FieldTitle2').text

        if prj.find('FieldTitle3') is not None:
            self.fieldTitle3 = prj.find('FieldTitle3').text

        if prj.find('FieldTitle4') is not None:
            self.fieldTitle4 = prj.find('FieldTitle4').text

        # Read attributes at chapter level from the xml element tree.

        for chp in root.iter('CHAPTER'):
            chId = chp.find('ID').text
            self.chapters[chId] = Chapter()
            self.srtChapters.append(chId)

            self.chapters[chId].title = chp.find('Title').text

            if self.chapters[chId].title.startswith('@'):
                self.chapters[chId].suppressChapterTitle = True

            else:
                self.chapters[chId].suppressChapterTitle = False

            if chp.find('Desc') is not None:
                self.chapters[chId].desc = chp.find('Desc').text

            if chp.find('SectionStart') is not None:
                self.chapters[chId].chLevel = 1

            else:
                self.chapters[chId].chLevel = 0

            if chp.find('Type') is not None:
                self.chapters[chId].chType = int(chp.find('Type').text)

            if chp.find('Unused') is not None:
                self.chapters[chId].isUnused = True

            else:
                self.chapters[chId].isUnused = False

            for fields in chp.findall('Fields'):

                if fields.find('Field_SuppressChapterTitle') is not None:

                    if fields.find('Field_SuppressChapterTitle').text == '1':
                        self.chapters[chId].suppressChapterTitle = True

                if fields.find('Field_IsTrash') is not None:

                    if fields.find('Field_IsTrash').text == '1':
                        self.chapters[chId].isTrash = True

                    else:
                        self.chapters[chId].isTrash = False

                if fields.find('Field_SuppressChapterBreak') is not None:

                    if fields.find('Field_SuppressChapterTitle').text == '0':
                        self.chapters[chId].doNotExport = True

                    else:
                        self.chapters[chId].doNotExport = False

                else:
                    self.chapters[chId].doNotExport = False

            self.chapters[chId].srtScenes = []

            if chp.find('Scenes') is not None:

                if not self.chapters[chId].isTrash:

                    for scn in chp.find('Scenes').findall('ScID'):
                        scId = scn.text
                        self.chapters[chId].srtScenes.append(scId)

        # Read attributes at scene level from the xml element tree.

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            self.scenes[scId] = Scene()

            self.scenes[scId].title = scn.find('Title').text

            if scn.find('Desc') is not None:
                self.scenes[scId].desc = scn.find('Desc').text

            if scn.find('SceneContent') is not None:
                sceneContent = scn.find('SceneContent').text

                if sceneContent is not None:
                    self.scenes[scId].sceneContent = sceneContent

            if scn.find('Unused') is not None:
                self.scenes[scId].isUnused = True

            else:
                self.scenes[scId].isUnused = False

            if scn.find('ExportCondSpecific') is None:
                self.scenes[scId].doNotExport = False

            elif scn.find('ExportWhenRTF') is not None:
                self.scenes[scId].doNotExport = False

            else:
                self.scenes[scId].doNotExport = True

            if scn.find('Status') is not None:
                self.scenes[scId].status = int(scn.find('Status').text)

            if scn.find('Notes') is not None:
                self.scenes[scId].sceneNotes = scn.find('Notes').text

            if scn.find('Tags') is not None:

                if scn.find('Tags').text is not None:
                    self.scenes[scId].tags = scn.find(
                        'Tags').text.split(';')

            if scn.find('Field1') is not None:
                self.scenes[scId].field1 = scn.find('Field1').text

            if scn.find('Field2') is not None:
                self.scenes[scId].field2 = scn.find('Field2').text

            if scn.find('Field3') is not None:
                self.scenes[scId].field3 = scn.find('Field3').text

            if scn.find('Field4') is not None:
                self.scenes[scId].field4 = scn.find('Field4').text

            if scn.find('AppendToPrev') is not None:
                self.scenes[scId].appendToPrev = True

            else:
                self.scenes[scId].appendToPrev = False

            if scn.find('SpecificDateTime') is not None:
                dateTime = scn.find('SpecificDateTime').text.split(' ')
                self.scenes[scId].date = dateTime[0]
                self.scenes[scId].time = dateTime[1]

            else:
                if scn.find('Day') is not None:
                    self.scenes[scId].day = scn.find('Day').text

                if scn.find('Hour') is not None:
                    self.scenes[scId].hour = scn.find('Hour').text

                if scn.find('Minute') is not None:
                    self.scenes[scId].minute = scn.find('Minute').text

            if scn.find('LastsDays') is not None:
                self.scenes[scId].lastsDays = scn.find('LastsDays').text

            if scn.find('LastsHours') is not None:
                self.scenes[scId].lastsHours = scn.find('LastsHours').text

            if scn.find('LastsMinutes') is not None:
                self.scenes[scId].lastsMinutes = scn.find('LastsMinutes').text

            if scn.find('ReactionScene') is not None:
                self.scenes[scId].isReactionScene = True

            else:
                self.scenes[scId].isReactionScene = False

            if scn.find('SubPlot') is not None:
                self.scenes[scId].isSubPlot = True

            else:
                self.scenes[scId].isSubPlot = False

            if scn.find('Goal') is not None:
                self.scenes[scId].goal = scn.find('Goal').text

            if scn.find('Conflict') is not None:
                self.scenes[scId].conflict = scn.find('Conflict').text

            if scn.find('Outcome') is not None:
                self.scenes[scId].outcome = scn.find('Outcome').text

            if scn.find('Characters') is not None:
                for crId in scn.find('Characters').iter('CharID'):

                    if self.scenes[scId].characters is None:
                        self.scenes[scId].characters = []

                    self.scenes[scId].characters.append(crId.text)

            if scn.find('Locations') is not None:
                for lcId in scn.find('Locations').iter('LocID'):

                    if self.scenes[scId].locations is None:
                        self.scenes[scId].locations = []

                    self.scenes[scId].locations.append(lcId.text)

            if scn.find('Items') is not None:
                for itId in scn.find('Items').iter('ItemID'):

                    if self.scenes[scId].items is None:
                        self.scenes[scId].items = []

                    self.scenes[scId].items.append(itId.text)

        return 'SUCCESS: ' + str(len(self.scenes)) + ' Scenes read from "' + self._filePath + '".'

    def merge(self, novel):
        """Merge attributes.
        """
        # Merge locations.

        for lcId in novel.locations:

            if not lcId in self.locations:
                self.locations[lcId] = Object()

            if novel.locations[lcId].title:
                # avoids deleting the title, if it is empty by accident
                self.locations[lcId].title = novel.locations[lcId].title

            if novel.locations[lcId].desc is not None:
                self.locations[lcId].desc = novel.locations[lcId].desc

            if novel.locations[lcId].aka is not None:
                self.locations[lcId].aka = novel.locations[lcId].aka

            if novel.locations[lcId].tags is not None:
                self.locations[lcId].tags = novel.locations[lcId].tags

        # Merge items.

        for itId in novel.items:

            if not itId in self.items:
                self.items[itId] = Object()

            if novel.items[itId].title:
                # avoids deleting the title, if it is empty by accident
                self.items[itId].title = novel.items[itId].title

            if novel.items[itId].desc is not None:
                self.items[itId].desc = novel.items[itId].desc

            if novel.items[itId].aka is not None:
                self.items[itId].aka = novel.items[itId].aka

            if novel.items[itId].tags is not None:
                self.items[itId].tags = novel.items[itId].tags

        # Merge characters.

        for crId in novel.characters:

            if not crId in self.characters:
                self.characters[crId] = Character()

            if novel.characters[crId].title:
                # avoids deleting the title, if it is empty by accident
                self.characters[crId].title = novel.characters[crId].title

            if novel.characters[crId].desc is not None:
                self.characters[crId].desc = novel.characters[crId].desc

            if novel.characters[crId].aka is not None:
                self.characters[crId].aka = novel.characters[crId].aka

            if novel.characters[crId].tags is not None:
                self.characters[crId].tags = novel.characters[crId].tags

            if novel.characters[crId].notes is not None:
                self.characters[crId].notes = novel.characters[crId].notes

            if novel.characters[crId].bio is not None:
                self.characters[crId].bio = novel.characters[crId].bio

            if novel.characters[crId].goals is not None:
                self.characters[crId].goals = novel.characters[crId].goals

            if novel.characters[crId].fullName is not None:
                self.characters[crId].fullName = novel.characters[crId].fullName

            if novel.characters[crId].isMajor is not None:
                self.characters[crId].isMajor = novel.characters[crId].isMajor

        # Merge scenes.

        for scId in novel.scenes:

            if not scId in self.scenes:
                self.scenes[scId] = Scene()

            if novel.scenes[scId].title:
                # avoids deleting the title, if it is empty by accident
                self.scenes[scId].title = novel.scenes[scId].title

            if novel.scenes[scId].desc is not None:
                self.scenes[scId].desc = novel.scenes[scId].desc

            if novel.scenes[scId].sceneContent is not None:
                self.scenes[scId].sceneContent = novel.scenes[scId].sceneContent

            if novel.scenes[scId].isUnused is not None:
                self.scenes[scId].isUnused = novel.scenes[scId].isUnused

            if novel.scenes[scId].status is not None:
                self.scenes[scId].status = novel.scenes[scId].status

            if novel.scenes[scId].sceneNotes is not None:
                self.scenes[scId].sceneNotes = novel.scenes[scId].sceneNotes

            if novel.scenes[scId].tags is not None:
                self.scenes[scId].tags = novel.scenes[scId].tags

            if novel.scenes[scId].field1 is not None:
                self.scenes[scId].field1 = novel.scenes[scId].field1

            if novel.scenes[scId].field2 is not None:
                self.scenes[scId].field2 = novel.scenes[scId].field2

            if novel.scenes[scId].field3 is not None:
                self.scenes[scId].field3 = novel.scenes[scId].field3

            if novel.scenes[scId].field4 is not None:
                self.scenes[scId].field4 = novel.scenes[scId].field4

            if novel.scenes[scId].appendToPrev is not None:
                self.scenes[scId].appendToPrev = novel.scenes[scId].appendToPrev

            if novel.scenes[scId].date is not None:
                self.scenes[scId].date = novel.scenes[scId].date

            if novel.scenes[scId].time is not None:
                self.scenes[scId].time = novel.scenes[scId].time

            if novel.scenes[scId].minute is not None:
                self.scenes[scId].minute = novel.scenes[scId].minute

            if novel.scenes[scId].hour is not None:
                self.scenes[scId].hour = novel.scenes[scId].hour

            if novel.scenes[scId].day is not None:
                self.scenes[scId].day = novel.scenes[scId].day

            if novel.scenes[scId].lastsMinutes is not None:
                self.scenes[scId].lastsMinutes = novel.scenes[scId].lastsMinutes

            if novel.scenes[scId].lastsHours is not None:
                self.scenes[scId].lastsHours = novel.scenes[scId].lastsHours

            if novel.scenes[scId].lastsDays is not None:
                self.scenes[scId].lastsDays = novel.scenes[scId].lastsDays

            if novel.scenes[scId].isReactionScene is not None:
                self.scenes[scId].isReactionScene = novel.scenes[scId].isReactionScene

            if novel.scenes[scId].isSubPlot is not None:
                self.scenes[scId].isSubPlot = novel.scenes[scId].isSubPlot

            if novel.scenes[scId].goal is not None:
                self.scenes[scId].goal = novel.scenes[scId].goal

            if novel.scenes[scId].conflict is not None:
                self.scenes[scId].conflict = novel.scenes[scId].conflict

            if novel.scenes[scId].outcome is not None:
                self.scenes[scId].outcome = novel.scenes[scId].outcome

            if novel.scenes[scId].characters is not None:
                self.scenes[scId].characters = []

                for crId in novel.scenes[scId].characters:

                    if crId in self.characters:
                        self.scenes[scId].characters.append(crId)

            if novel.scenes[scId].locations is not None:
                self.scenes[scId].locations = []

                for lcId in novel.scenes[scId].locations:

                    if lcId in self.locations:
                        self.scenes[scId].locations.append(lcId)

            if novel.scenes[scId].items is not None:
                self.scenes[scId].items = []

                for itId in novel.scenes[scId].items:

                    if itId in self.items:
                        self.scenes[scId].append(itId)

        # Merge chapters.

        scenesAssigned = []

        for chId in novel.chapters:

            if not chId in self.chapters:
                self.chapters[chId] = Chapter()

            if novel.chapters[chId].title:
                # avoids deleting the title, if it is empty by accident
                self.chapters[chId].title = novel.chapters[chId].title

            if novel.chapters[chId].desc is not None:
                self.chapters[chId].desc = novel.chapters[chId].desc

            if novel.chapters[chId].chLevel is not None:
                self.chapters[chId].chLevel = novel.chapters[chId].chLevel

            if novel.chapters[chId].chType is not None:
                self.chapters[chId].chType = novel.chapters[chId].chType

            if novel.chapters[chId].isUnused is not None:
                self.chapters[chId].isUnused = novel.chapters[chId].isUnused

            if novel.chapters[chId].suppressChapterTitle is not None:
                self.chapters[chId].suppressChapterTitle = novel.chapters[chId].suppressChapterTitle

            if novel.chapters[chId].isTrash is not None:
                self.chapters[chId].isTrash = novel.chapters[chId].isTrash

            if novel.chapters[chId].srtScenes is not None:
                self.chapters[chId].srtScenes = []

                for scId in novel.chapters[chId].srtScenes:

                    if (scId in self.scenes) and not (scId in scenesAssigned):
                        self.chapters[chId].srtScenes.append(scId)
                        scenesAssigned.append(scId)

        # Merge attributes at novel level.

        if novel.title:
            # avoids deleting the title, if it is empty by accident
            self.title = novel.title

        if novel.desc is not None:
            self.desc = novel.desc

        if novel.author is not None:
            self.author = novel.author

        if novel.fieldTitle1 is not None:
            self.fieldTitle1 = novel.fieldTitle1

        if novel.fieldTitle2 is not None:
            self.fieldTitle2 = novel.fieldTitle2

        if novel.fieldTitle3 is not None:
            self.fieldTitle3 = novel.fieldTitle3

        if novel.fieldTitle4 is not None:
            self.fieldTitle4 = novel.fieldTitle4

        if novel.srtChapters != []:
            self.srtChapters = []

            for chId in novel.srtChapters:

                if chId in self.chapters:
                    self.srtChapters.append(chId)

    def write(self):
        """Open the yWriter xml file located at filePath and 
        replace a set of attributes not being None.
        Return a message beginning with SUCCESS or ERROR.
        """

        root = self._tree.getroot()

        # Write locations to the xml element tree.

        for loc in root.iter('LOCATION'):
            lcId = loc.find('ID').text

            if lcId in self.locations:

                if self.locations[lcId].title is not None:
                    loc.find('Title').text = self.locations[lcId].title

                if self.locations[lcId].desc is not None:

                    if loc.find('Desc') is None:
                        ET.SubElement(
                            loc, 'Desc').text = self.locations[lcId].desc

                    else:
                        loc.find('Desc').text = self.locations[lcId].desc

                if self.locations[lcId].aka is not None:

                    if loc.find('AKA') is None:
                        ET.SubElement(
                            loc, 'AKA').text = self.locations[lcId].aka

                    else:
                        loc.find('AKA').text = self.locations[lcId].aka

                if self.locations[lcId].tags is not None:

                    if loc.find('Tags') is None:
                        ET.SubElement(loc, 'Tags').text = ';'.join(
                            self.locations[lcId].tags)

                    else:
                        loc.find('Tags').text = ';'.join(
                            self.locations[lcId].tags)

        # Write items to the xml element tree.

        for itm in root.iter('ITEM'):
            itId = itm.find('ID').text

            if itId in self.items:

                if self.items[itId].title is not None:
                    itm.find('Title').text = self.items[itId].title

                if self.items[itId].desc is not None:

                    if itm.find('Desc') is None:
                        ET.SubElement(itm, 'Desc').text = self.items[itId].desc

                    else:
                        itm.find('Desc').text = self.items[itId].desc

                if self.items[itId].aka is not None:

                    if itm.find('AKA') is None:
                        ET.SubElement(itm, 'AKA').text = self.items[itId].aka

                    else:
                        itm.find('AKA').text = self.items[itId].aka

                if self.items[itId].tags is not None:

                    if itm.find('Tags') is None:
                        ET.SubElement(itm, 'Tags').text = ';'.join(
                            self.items[itId].tags)

                    else:
                        itm.find('Tags').text = ';'.join(
                            self.items[itId].tags)

        # Write characters to the xml element tree.

        for crt in root.iter('CHARACTER'):
            crId = crt.find('ID').text

            if crId in self.characters:

                if self.characters[crId].title is not None:
                    crt.find('Title').text = self.characters[crId].title

                if self.characters[crId].desc is not None:

                    if crt.find('Desc') is None:
                        ET.SubElement(
                            crt, 'Desc').text = self.characters[crId].desc

                    else:
                        crt.find('Desc').text = self.characters[crId].desc

                if self.characters[crId].aka is not None:

                    if crt.find('AKA') is None:
                        ET.SubElement(
                            crt, 'AKA').text = self.characters[crId].aka

                    else:
                        crt.find('AKA').text = self.characters[crId].aka

                if self.characters[crId].tags is not None:

                    if crt.find('Tags') is None:
                        ET.SubElement(crt, 'Tags').text = ';'.join(
                            self.characters[crId].tags)

                    else:
                        crt.find('Tags').text = ';'.join(
                            self.characters[crId].tags)

                if self.characters[crId].notes is not None:

                    if crt.find('Notes') is None:
                        ET.SubElement(
                            crt, 'Notes').text = self.characters[crId].notes

                    else:
                        crt.find(
                            'Notes').text = self.characters[crId].notes

                if self.characters[crId].bio is not None:

                    if crt.find('Bio') is None:
                        ET.SubElement(
                            crt, 'Bio').text = self.characters[crId].bio

                    else:
                        crt.find('Bio').text = self.characters[crId].bio

                if self.characters[crId].goals is not None:

                    if crt.find('Goals') is None:
                        ET.SubElement(
                            crt, 'Goals').text = self.characters[crId].goals

                    else:
                        crt.find(
                            'Goals').text = self.characters[crId].goals

                if self.characters[crId].fullName is not None:

                    if crt.find('FullName') is None:
                        ET.SubElement(
                            crt, 'FullName').text = self.characters[crId].fullName

                    else:
                        crt.find(
                            'FullName').text = self.characters[crId].fullName

                majorMarker = crt.find('Major')

                if majorMarker is not None:

                    if not self.characters[crId].isMajor:
                        crt.remove(majorMarker)

                else:
                    if self.characters[crId].isMajor:
                        ET.SubElement(crt, 'Major').text = '-1'

        # Write attributes at novel level to the xml element tree.

        prj = root.find('PROJECT')
        prj.find('Title').text = self.title

        if self.desc is not None:

            if prj.find('Desc') is None:
                ET.SubElement(prj, 'Desc').text = self.desc

            else:
                prj.find('Desc').text = self.desc

        if self.author is not None:

            if prj.find('AuthorName') is None:
                ET.SubElement(prj, 'AuthorName').text = self.author

            else:
                prj.find('AuthorName').text = self.author

        prj.find('FieldTitle1').text = self.fieldTitle1
        prj.find('FieldTitle2').text = self.fieldTitle2
        prj.find('FieldTitle3').text = self.fieldTitle3
        prj.find('FieldTitle4').text = self.fieldTitle4

        # Write attributes at chapter level to the xml element tree.

        for chp in root.iter('CHAPTER'):
            chId = chp.find('ID').text

            if chId in self.chapters:
                chp.find('Title').text = self.chapters[chId].title

                if self.chapters[chId].desc is not None:

                    if chp.find('Desc') is None:
                        ET.SubElement(
                            chp, 'Desc').text = self.chapters[chId].desc

                    else:
                        chp.find('Desc').text = self.chapters[chId].desc

                levelInfo = chp.find('SectionStart')

                if levelInfo is not None:

                    if self.chapters[chId].chLevel == 0:
                        chp.remove(levelInfo)

                chp.find('Type').text = str(self.chapters[chId].chType)

                if self.chapters[chId].isUnused:

                    if chp.find('Unused') is None:
                        ET.SubElement(chp, 'Unused').text = '-1'

                elif chp.find('Unused') is not None:
                    chp.remove(chp.find('Unused'))

        # Write attributes at scene level to the xml element tree.

        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text

            if scId in self.scenes:

                if self.scenes[scId].title is not None:
                    scn.find('Title').text = self.scenes[scId].title

                if self.scenes[scId].desc is not None:

                    if scn.find('Desc') is None:
                        ET.SubElement(
                            scn, 'Desc').text = self.scenes[scId].desc

                    else:
                        scn.find('Desc').text = self.scenes[scId].desc

                if self.scenes[scId]._sceneContent is not None:
                    scn.find(
                        'SceneContent').text = replace_unsafe_glyphs(self.scenes[scId]._sceneContent)
                    scn.find('WordCount').text = str(
                        self.scenes[scId].wordCount)
                    scn.find('LetterCount').text = str(
                        self.scenes[scId].letterCount)

                if self.scenes[scId].isUnused:

                    if scn.find('Unused') is None:
                        ET.SubElement(scn, 'Unused').text = '-1'

                elif scn.find('Unused') is not None:
                    scn.remove(scn.find('Unused'))

                if self.scenes[scId].status is not None:
                    scn.find('Status').text = str(self.scenes[scId].status)

                if self.scenes[scId].sceneNotes is not None:

                    if scn.find('Notes') is None:
                        ET.SubElement(
                            scn, 'Notes').text = self.scenes[scId].sceneNotes

                    else:
                        scn.find(
                            'Notes').text = self.scenes[scId].sceneNotes

                if self.scenes[scId].tags is not None:

                    if scn.find('Tags') is None:
                        ET.SubElement(scn, 'Tags').text = ';'.join(
                            self.scenes[scId].tags)

                    else:
                        scn.find('Tags').text = ';'.join(
                            self.scenes[scId].tags)

                if self.scenes[scId].field1 is not None:

                    if scn.find('Field1') is None:
                        ET.SubElement(
                            scn, 'Field1').text = self.scenes[scId].field1

                    else:
                        scn.find('Field1').text = self.scenes[scId].field1

                if self.scenes[scId].field2 is not None:

                    if scn.find('Field2') is None:
                        ET.SubElement(
                            scn, 'Field2').text = self.scenes[scId].field2

                    else:
                        scn.find('Field2').text = self.scenes[scId].field2

                if self.scenes[scId].field3 is not None:

                    if scn.find('Field3') is None:
                        ET.SubElement(
                            scn, 'Field3').text = self.scenes[scId].field3

                    else:
                        scn.find('Field3').text = self.scenes[scId].field3

                if self.scenes[scId].field4 is not None:

                    if scn.find('Field4') is None:
                        ET.SubElement(
                            scn, 'Field4').text = self.scenes[scId].field4

                    else:
                        scn.find('Field4').text = self.scenes[scId].field4

                if self.scenes[scId].appendToPrev:

                    if scn.find('AppendToPrev') is None:
                        ET.SubElement(scn, 'AppendToPrev').text = '-1'

                elif scn.find('AppendToPrev') is not None:
                    scn.remove(scn.find('AppendToPrev'))

                # Date/time information

                if (self.scenes[scId].date is not None) and (self.scenes[scId].time is not None):
                    dateTime = self.scenes[scId].date + \
                        ' ' + self.scenes[scId].time

                    if scn.find('SpecificDateTime') is not None:
                        scn.find('SpecificDateTime').text = dateTime

                    else:
                        ET.SubElement(scn, 'SpecificDateTime').text = dateTime
                        ET.SubElement(scn, 'SpecificDateMode').text = '-1'

                        if scn.find('Day') is not None:
                            scn.remove(scn.find('Day'))

                        if scn.find('Hour') is not None:
                            scn.remove(scn.find('Hour'))

                        if scn.find('Minute') is not None:
                            scn.remove(scn.find('Minute'))

                elif (self.scenes[scId].day is not None) or (self.scenes[scId].hour is not None) or (self.scenes[scId].minute is not None):

                    if scn.find('SpecificDateTime') is not None:
                        scn.remove(scn.find('SpecificDateTime'))

                    if scn.find('SpecificDateMode') is not None:
                        scn.remove(scn.find('SpecificDateMode'))

                    if self.scenes[scId].day is not None:

                        if scn.find('Day') is not None:
                            scn.find('Day').text = self.scenes[scId].day

                        else:
                            ET.SubElement(
                                scn, 'Day').text = self.scenes[scId].day

                    if self.scenes[scId].hour is not None:

                        if scn.find('Hour') is not None:
                            scn.find('Hour').text = self.scenes[scId].hour

                        else:
                            ET.SubElement(
                                scn, 'Hour').text = self.scenes[scId].hour

                    if self.scenes[scId].minute is not None:

                        if scn.find('Minute') is not None:
                            scn.find('Minute').text = self.scenes[scId].minute

                        else:
                            ET.SubElement(
                                scn, 'Minute').text = self.scenes[scId].minute

                if self.scenes[scId].lastsDays is not None:

                    if scn.find('LastsDays') is not None:
                        scn.find(
                            'LastsDays').text = self.scenes[scId].lastsDays

                    else:
                        ET.SubElement(
                            scn, 'LastsDays').text = self.scenes[scId].lastsDays

                if self.scenes[scId].lastsHours is not None:

                    if scn.find('LastsHours') is not None:
                        scn.find(
                            'LastsHours').text = self.scenes[scId].lastsHours

                    else:
                        ET.SubElement(
                            scn, 'LastsHours').text = self.scenes[scId].lastsHours

                if self.scenes[scId].lastsMinutes is not None:

                    if scn.find('LastsMinutes') is not None:
                        scn.find(
                            'LastsMinutes').text = self.scenes[scId].lastsMinutes

                    else:
                        ET.SubElement(
                            scn, 'LastsMinutes').text = self.scenes[scId].lastsMinutes

                # Plot related information

                if self.scenes[scId].isReactionScene:

                    if scn.find('ReactionScene') is None:
                        ET.SubElement(scn, 'ReactionScene').text = '-1'

                elif scn.find('ReactionScene') is not None:
                    scn.remove(scn.find('ReactionScene'))

                if self.scenes[scId].isSubPlot:

                    if scn.find('SubPlot') is None:
                        ET.SubElement(scn, 'SubPlot').text = '-1'

                elif scn.find('SubPlot') is not None:
                    scn.remove(scn.find('SubPlot'))

                if self.scenes[scId].goal is not None:

                    if scn.find('Goal') is None:
                        ET.SubElement(
                            scn, 'Goal').text = self.scenes[scId].goal

                    else:
                        scn.find('Goal').text = self.scenes[scId].goal

                if self.scenes[scId].conflict is not None:

                    if scn.find('Conflict') is None:
                        ET.SubElement(
                            scn, 'Conflict').text = self.scenes[scId].conflict

                    else:
                        scn.find(
                            'Conflict').text = self.scenes[scId].conflict

                if self.scenes[scId].outcome is not None:

                    if scn.find('Outcome') is None:
                        ET.SubElement(
                            scn, 'Outcome').text = self.scenes[scId].outcome

                    else:
                        scn.find(
                            'Outcome').text = self.scenes[scId].outcome

                if self.scenes[scId].characters is not None:
                    characters = scn.find('Characters')

                    for oldCrId in characters.findall('CharID'):
                        characters.remove(oldCrId)

                    for crId in self.scenes[scId].characters:
                        ET.SubElement(characters, 'CharID').text = crId

                if self.scenes[scId].locations is not None:
                    locations = scn.find('Locations')

                    for oldLcId in locations.findall('LocID'):
                        locations.remove(oldLcId)

                    for lcId in self.scenes[scId].locations:
                        ET.SubElement(locations, 'LocID').text = lcId

                if self.scenes[scId].items is not None:
                    items = scn.find('Items')

                    for oldItId in items.findall('ItemID'):
                        items.remove(oldItId)

                    for itId in self.scenes[scId].items:
                        ET.SubElement(items, 'ItemID').text = itId

        # Pretty print the xml tree.

        indent(root)

        # Save the xml tree in a file.

        self._tree = ET.ElementTree(root)

        try:
            self._tree.write(
                self._filePath, xml_declaration=False, encoding=self._ENCODING)

        except(PermissionError):
            return 'ERROR: "' + self._filePath + '" is write protected.'

        # Postprocess the xml file created by ElementTree.

        message = xml_postprocess(
            self._filePath, self._ENCODING, self._cdataTags)

        if message.startswith('ERROR'):
            return message

        return 'SUCCESS: project data written to "' + self._filePath + '".'

    def is_locked(self):
        """Test whether a .lock file placed by yWriter exists.
        """
        if os.path.isfile(self._filePath + '.lock'):
            return True

        else:
            return False


class YwNewFile(YwFile):
    """yWriter xml project file representation."""

    def write(self):
        """Open the yWriter xml file located at filePath and 
        replace a set of attributes not being None.
        Return a message beginning with SUCCESS or ERROR.
        """

        root = ET.Element('YWRITER7')

        # Write attributes at novel level to the xml element tree.

        prj = ET.SubElement(root, 'PROJECT')
        ET.SubElement(prj, 'Ver').text = '7'

        if self.title is not None:
            ET.SubElement(prj, 'Title').text = self.title

        if self.desc is not None:
            ET.SubElement(prj, 'Desc').text = self.desc

        if self.author is not None:
            ET.SubElement(prj, 'AuthorName').text = self.author

        if self.fieldTitle1 is not None:
            ET.SubElement(prj, 'FieldTitle1').text = self.fieldTitle1

        if self.fieldTitle2 is not None:
            ET.SubElement(prj, 'FieldTitle2').text = self.fieldTitle2

        if self.fieldTitle3 is not None:
            ET.SubElement(prj, 'FieldTitle3').text = self.fieldTitle3

        if self.fieldTitle4 is not None:
            ET.SubElement(prj, 'FieldTitle4').text = self.fieldTitle4

        # Write locations to the xml element tree.

        locations = ET.SubElement(root, 'LOCATIONS')

        for lcId in self.locations:
            loc = ET.SubElement(locations, 'LOCATION')
            ET.SubElement(loc, 'ID').text = lcId

            if self.locations[lcId].title is not None:
                ET.SubElement(loc, 'Title').text = self.locations[lcId].title

            if self.locations[lcId].desc is not None:
                ET.SubElement(loc, 'Desc').text = self.locations[lcId].desc

            if self.locations[lcId].aka is not None:
                ET.SubElement(loc, 'AKA').text = self.locations[lcId].aka

            if self.locations[lcId].tags is not None:
                ET.SubElement(loc, 'Tags').text = ';'.join(
                    self.locations[lcId].tags)

        # Write items to the xml element tree.

        items = ET.SubElement(root, 'ITEMS')

        for itId in self.items:
            itm = ET.SubElement(items, 'ITEM')
            ET.SubElement(itm, 'ID').text = itId

            if self.items[itId].title is not None:
                ET.SubElement(itm, 'Title').text = self.items[itId].title

            if self.items[itId].desc is not None:
                ET.SubElement(itm, 'Desc').text = self.items[itId].desc

            if self.items[itId].aka is not None:
                ET.SubElement(itm, 'AKA').text = self.items[itId].aka

            if self.items[itId].tags is not None:
                ET.SubElement(itm, 'Tags').text = ';'.join(
                    self.items[itId].tags)

        # Write characters to the xml element tree.

        characters = ET.SubElement(root, 'CHARACTERS')

        for crId in self.characters:
            crt = ET.SubElement(characters, 'CHARACTER')
            ET.SubElement(crt, 'ID').text = crId

            if self.characters[crId].title is not None:
                ET.SubElement(
                    crt, 'Title').text = self.characters[crId].title

            if self.characters[crId].desc is not None:
                ET.SubElement(
                    crt, 'Desc').text = self.characters[crId].desc

            if self.characters[crId].aka is not None:
                ET.SubElement(crt, 'AKA').text = self.characters[crId].aka

            if self.characters[crId].tags is not None:
                ET.SubElement(crt, 'Tags').text = ';'.join(
                    self.characters[crId].tags)

            if self.characters[crId].notes is not None:
                ET.SubElement(
                    crt, 'Notes').text = self.characters[crId].notes

            if self.characters[crId].bio is not None:
                ET.SubElement(crt, 'Bio').text = self.characters[crId].bio

            if self.characters[crId].goals is not None:
                ET.SubElement(
                    crt, 'Goals').text = self.characters[crId].goals

            if self.characters[crId].fullName is not None:
                ET.SubElement(
                    crt, 'FullName').text = self.characters[crId].fullName

            if self.characters[crId].isMajor:
                ET.SubElement(crt, 'Major').text = '-1'

        # Write attributes at scene level to the xml element tree.

        scenes = ET.SubElement(root, 'SCENES')

        for scId in self.scenes:
            scn = ET.SubElement(scenes, 'SCENE')
            ET.SubElement(scn, 'ID').text = scId

            if self.scenes[scId].title is not None:
                ET.SubElement(scn, 'Title').text = self.scenes[scId].title

            for chId in self.chapters:

                if scId in self.chapters[chId].srtScenes:
                    ET.SubElement(scn, 'BelongsToChID').text = chId
                    break

            if self.scenes[scId].desc is not None:
                ET.SubElement(scn, 'Desc').text = self.scenes[scId].desc

            if self.scenes[scId]._sceneContent is not None:
                ET.SubElement(scn,
                              'SceneContent').text = replace_unsafe_glyphs(self.scenes[scId]._sceneContent)
                ET.SubElement(scn, 'WordCount').text = str(
                    self.scenes[scId].wordCount)
                ET.SubElement(scn, 'LetterCount').text = str(
                    self.scenes[scId].letterCount)

            if self.scenes[scId].isUnused:
                ET.SubElement(scn, 'Unused').text = '-1'

            if self.scenes[scId].status is not None:
                ET.SubElement(scn, 'Status').text = str(
                    self.scenes[scId].status)

            if self.scenes[scId].sceneNotes is not None:
                ET.SubElement(scn, 'Notes').text = self.scenes[scId].sceneNotes

            if self.scenes[scId].tags is not None:
                ET.SubElement(scn, 'Tags').text = ';'.join(
                    self.scenes[scId].tags)

            if self.scenes[scId].field1 is not None:
                ET.SubElement(scn, 'Field1').text = self.scenes[scId].field1

            if self.scenes[scId].field2 is not None:
                ET.SubElement(scn, 'Field2').text = self.scenes[scId].field2

            if self.scenes[scId].field3 is not None:
                ET.SubElement(scn, 'Field3').text = self.scenes[scId].field3

            if self.scenes[scId].field4 is not None:
                ET.SubElement(scn, 'Field4').text = self.scenes[scId].field4

            if self.scenes[scId].appendToPrev:
                ET.SubElement(scn, 'AppendToPrev').text = '-1'

            # Date/time information

            if (self.scenes[scId].date is not None) and (self.scenes[scId].time is not None):
                dateTime = ' '.join(
                    self.scenes[scId].date, self.scenes[scId].time)
                ET.SubElement(scn, 'SpecificDateTime').text = dateTime
                ET.SubElement(scn, 'SpecificDateMode').text = '-1'

            elif (self.scenes[scId].day is not None) or (self.scenes[scId].hour is not None) or (self.scenes[scId].minute is not None):

                if self.scenes[scId].day is not None:
                    ET.SubElement(scn, 'Day').text = self.scenes[scId].day

                if self.scenes[scId].hour is not None:
                    ET.SubElement(scn, 'Hour').text = self.scenes[scId].hour

                if self.scenes[scId].minute is not None:
                    ET.SubElement(
                        scn, 'Minute').text = self.scenes[scId].minute

            if self.scenes[scId].lastsDays is not None:
                ET.SubElement(
                    scn, 'LastsDays').text = self.scenes[scId].lastsDays

            if self.scenes[scId].lastsHours is not None:
                ET.SubElement(
                    scn, 'LastsHours').text = self.scenes[scId].lastsHours

            if self.scenes[scId].lastsMinutes is not None:
                ET.SubElement(
                    scn, 'LastsMinutes').text = self.scenes[scId].lastsMinutes

            # Plot related information

            if self.scenes[scId].isReactionScene:
                ET.SubElement(scn, 'ReactionScene').text = '-1'

            if self.scenes[scId].isSubPlot:
                ET.SubElement(scn, 'SubPlot').text = '-1'

            if self.scenes[scId].goal is not None:
                ET.SubElement(scn, 'Goal').text = self.scenes[scId].goal

            if self.scenes[scId].conflict is not None:
                ET.SubElement(
                    scn, 'Conflict').text = self.scenes[scId].conflict

            if self.scenes[scId].outcome is not None:
                ET.SubElement(scn, 'Outcome').text = self.scenes[scId].outcome

            if self.scenes[scId].characters is not None:
                scCharacters = ET.SubElement(scn, 'Characters')

                for crId in self.scenes[scId].characters:
                    ET.SubElement(scCharacters, 'CharID').text = crId

            if self.scenes[scId].locations is not None:
                scLocations = ET.SubElement(scn, 'Locations')

                for lcId in self.scenes[scId].locations:
                    ET.SubElement(scLocations, 'LocID').text = lcId

            if self.scenes[scId].items is not None:
                scItems = ET.SubElement(scn, 'Items')

                for itId in self.scenes[scId].items:
                    ET.SubElement(scItems, 'ItemID').text = itId

        # Write attributes at chapter level to the xml element tree.

        chapters = ET.SubElement(root, 'CHAPTERS')

        sortOrder = 0

        for chId in self.srtChapters:
            sortOrder += 1
            chp = ET.SubElement(chapters, 'CHAPTER')
            ET.SubElement(chp, 'ID').text = chId
            ET.SubElement(chp, 'SortOrder').text = str(sortOrder)

            if self.chapters[chId].title is not None:
                ET.SubElement(chp, 'Title').text = self.chapters[chId].title

            if self.chapters[chId].desc is not None:
                ET.SubElement(chp, 'Desc').text = self.chapters[chId].desc

            if self.chapters[chId].chLevel == 1:
                ET.SubElement(chp, 'SectionStart').text = '-1'

            if self.chapters[chId].chType is not None:
                ET.SubElement(chp, 'Type').text = str(
                    self.chapters[chId].chType)

            if self.chapters[chId].isUnused:
                ET.SubElement(chp, 'Unused').text = '-1'

            sortSc = ET.SubElement(chp, 'Scenes')

            for scId in self.chapters[chId].srtScenes:
                ET.SubElement(sortSc, 'ScID').text = scId

            chFields = ET.SubElement(chp, 'Fields')

            if self.chapters[chId].title.startswith('@'):
                self.chapters[chId].suppressChapterTitle = True

            if self.chapters[chId].suppressChapterTitle:
                ET.SubElement(
                    chFields, 'Field_SuppressChapterTitle').text = '1'

        # Pretty print the xml tree.

        indent(root)

        # Save the xml tree in a file.

        self._tree = ET.ElementTree(root)

        try:
            self._tree.write(
                self._filePath, xml_declaration=False, encoding=self._ENCODING)

        except(PermissionError):
            return 'ERROR: "' + self._filePath + '" is write protected.'

        # Postprocess the xml file created by ElementTree.

        message = xml_postprocess(
            self._filePath, self._ENCODING, self._cdataTags)

        if message.startswith('ERROR'):
            return message

        return 'SUCCESS: project data written to "' + self._filePath + '".'


class YwCnv():
    """Converter for yWriter project files.

    # Methods

    yw_to_document : str
        Arguments
            ywFile : YwFile
                an object representing the source file.
            documentFile : Novel
                a Novel subclass instance representing the target file.
        Read yWriter file, parse xml and create a document file.
        Return a message beginning with SUCCESS or ERROR.    

    document_to_yw : str
        Arguments
            documentFile : Novel
                a Novel subclass instance representing the source file.
            ywFile : YwFile
                an object representing the target file.
        Read document file, convert its content to xml, and replace yWriter file.
        Return a message beginning with SUCCESS or ERROR.

    confirm_overwrite : bool
        Arguments
            fileName : str
                Path to the file to be overwritten
        Ask for permission to overwrite the target file.
        Returns True by default.
        This method is to be overwritten by subclasses with an user interface.
    """

    def yw_to_document(self, ywFile, documentFile):
        """Read yWriter file and convert xml to a document file."""
        if ywFile.is_locked():
            return 'ERROR: yWriter seems to be open. Please close first.'

        if ywFile.filePath is None:
            return 'ERROR: "' + ywFile.filePath + '" is not an yWriter project.'

        message = ywFile.read()

        if message.startswith('ERROR'):
            return message

        if documentFile.file_exists():

            if not self.confirm_overwrite(documentFile.filePath):
                return 'Program abort by user.'

        documentFile.merge(ywFile)
        return documentFile.write()

    def document_to_yw(self, documentFile, ywFile):
        """Read document file, convert its content to xml, and replace yWriter file."""
        if ywFile.is_locked():
            return 'ERROR: yWriter seems to be open. Please close first.'

        if ywFile.filePath is None:
            return 'ERROR: "' + ywFile.filePath + '" is not an yWriter project.'

        if ywFile.file_exists() and not self.confirm_overwrite(ywFile.filePath):
            return 'Program abort by user.'

        if documentFile.filePath is None:
            return 'ERROR: Document is not of the supported type.'

        if not documentFile.file_exists():
            return 'ERROR: "' + documentFile.filePath + '" not found.'

        message = documentFile.read()

        if message.startswith('ERROR'):
            return message

        if ywFile.file_exists():
            message = ywFile.read()
            # initialize ywFile data

            if message.startswith('ERROR'):
                return message

        prjStructure = documentFile.get_structure()

        if prjStructure is not None:

            if prjStructure == '':
                return 'ERROR: Source file contains no yWriter project structure information.'

            if prjStructure != ywFile.get_structure():
                return 'ERROR: Structure mismatch - yWriter project not modified.'

        ywFile.merge(documentFile)
        return ywFile.write()

    def confirm_overwrite(self, fileName):
        """To be overwritten by subclasses with UI."""
        return True


TITLE = 'yWriter import/export'


class YwCnvGui(YwCnv):
    """Standalone yWriter converter with a simple GUI. 

    # Arguments

        sourcePath : str
            a full or relative path to the file to be converted.
            Either an yWriter file or a file of any supported type. 
            The file type determines the conversion's direction.    

        document : Novel
            instance of any Novel subclass representing the 
            source or target document. 

        extension : str
            File extension determining the source or target 
            document's file type. The extension is needed because 
            there can be ambiguous Novel subclasses 
            (e.g. OfficeFile).
            Examples: 
            - md
            - docx
            - odt
            - html

        silentMode : bool
            True by default. Intended for automated tests. 
            If True, the GUI is not started and no further 
            user interaction is required. Overwriting of existing
            files is forced. 
            Calling scripts shall set silentMode = False.

        suffix : str
            Optional file name suffix used for ambiguous html files.
            Examples:
            - _manuscript for a html file containing scene contents.
            - _scenes for a html file containing scene summaries.
            - _chapters for a html file containing chapter summaries.
    """

    def __init__(self, sourcePath, document, silentMode=True):
        """Run the converter with a GUI. """

        # Prepare the graphical user interface.

        self.root = Tk()
        self.root.geometry("800x360")
        self.root.title(TITLE)
        self.header = Label(self.root, text=__doc__)
        self.header.pack(padx=5, pady=5)
        self.appInfo = Label(self.root, text='')
        self.appInfo.pack(padx=5, pady=5)
        self.successInfo = Label(self.root)
        self.successInfo.pack(fill=X, expand=1, padx=50, pady=5)
        self.processInfo = Label(self.root, text='')
        self.processInfo.pack(padx=5, pady=5)

        self._success = False

        # Run the converter.

        self.silentMode = silentMode
        self.convert(sourcePath, document)

        # Visualize the outcome.

        if not self.silentMode:

            if self._success:
                self.successInfo.config(bg='green')

            else:
                self.successInfo.config(bg='red')

            self.root.quitButton = Button(text="Quit", command=quit)
            self.root.quitButton.config(height=1, width=10)
            self.root.quitButton.pack(padx=5, pady=5)
            self.root.mainloop()

    def convert(self, sourcePath, document):
        """Determine the direction and invoke the converter. """

        # The conversion's direction depends on the sourcePath argument.

        if not os.path.isfile(sourcePath):
            self.processInfo.config(text='ERROR: File not found.')

        else:
            fileName, FileExtension = os.path.splitext(sourcePath)

            if FileExtension in ['.yw5', '.yw6', '.yw7']:

                # Generate the target file path.

                document.filePath = fileName + document.SUFFIX + document.EXTENSION
                self.appInfo.config(
                    text='Export yWriter scenes content to ' + document.EXTENSION)
                self.processInfo.config(text='Project: "' + sourcePath + '"')

                # Instantiate an YwFile object and pass it along with
                # the document to the converter class.

                ywFile = YwFile(sourcePath)
                self.processInfo.config(
                    text=self.yw_to_document(ywFile, document))

            elif (document.SUFFIX == '') and (document.EXTENSIION == '.html'):
                document.filePath = sourcePath
                ywPath = sourcePath.split('.html')[0] + '.yw7'
                ywFile = YwNewFile(ywPath)

                if ywFile.file_exists():
                    self.processInfo.config(
                        text='ERROR: yWriter project already exists.')

                else:
                    self.appInfo.config(
                        text='Create a yWriter project file')
                    self.processInfo.config(
                        text='New project: "' + ywPath + '"')
                    self.processInfo.config(
                        text=self.document_to_yw(document, ywFile))

            elif sourcePath.endswith(document.SUFFIX + document.EXTENSION):
                document.filePath = sourcePath

                # Determine the project file path.

                ywPath = sourcePath.split(document.SUFFIX)[0] + '.yw7'

                if not os.path.isfile(ywPath):
                    ywPath = sourcePath.split(document.SUFFIX)[0] + '.yw6'

                    if not os.path.isfile(ywPath):
                        ywPath = sourcePath.split(document.SUFFIX)[0] + '.yw5'

                        if not os.path.isfile(ywPath):
                            ywPath = None
                            self.processInfo.config(
                                text='ERROR: No yWriter project found.')

                if ywPath:
                    self.appInfo.config(
                        text='Import yWriter scenes content from ' + document.EXTENSION)
                    self.processInfo.config(
                        text='Project: "' + ywPath + '"')

                    # Instantiate an YwFile object and pass it along with
                    # the document to the converter class.

                    ywFile = YwFile(ywPath)
                    self.processInfo.config(
                        text=self.document_to_yw(document, ywFile))

            else:
                self.processInfo.config(
                    text='ERROR: File type is not supported.')

            # Visualize the outcome.

            if self.processInfo.cget('text').startswith('SUCCESS'):
                self._success = True

    def confirm_overwrite(self, filePath):
        """ Invoked by the parent if a file already exists. """

        if self.silentMode:
            return True

        else:
            return messagebox.askyesno('WARNING', 'Overwrite existing file "' + filePath + '"?')

    def edit(self):
        pass


from string import Template


class FileExport(Novel):
    """Abstract yWriter project file exporter representation.
    """

    fileHeader = ''
    partTemplate = ''
    chapterTemplate = ''
    unusedChapterTemplate = ''
    infoChapterTemplate = ''
    sceneTemplate = ''
    unusedSceneTemplate = ''
    infoSceneTemplate = ''
    sceneDivider = ''
    chapterEndTemplate = ''
    unusedChapterEndTemplate = ''
    infoChapterEndTemplate = ''
    characterTemplate = ''
    locationTemplate = ''
    itemTemplate = ''
    fileFooter = ''

    def convert_from_yw(self, text):
        """Convert yw7 markup to target format.
        To be overwritten by file format specific subclasses.
        """

        if text is None:
            text = ''

        return(text)

    def merge(self, novel):
        """Copy selected novel attributes.
        """

        if novel.title is not None:
            self.title = novel.title

        else:
            self.title = ''

        if novel.desc is not None:
            self.desc = novel.desc

        else:
            self.desc = ''

        if novel.author is not None:
            self.author = novel.author

        else:
            self.author = ''

        if novel.fieldTitle1 is not None:
            self.fieldTitle1 = novel.fieldTitle1

        else:
            self.fieldTitle1 = 'Field 1'

        if novel.fieldTitle2 is not None:
            self.fieldTitle2 = novel.fieldTitle2

        else:
            self.fieldTitle2 = 'Field 2'

        if novel.fieldTitle3 is not None:
            self.fieldTitle3 = novel.fieldTitle3

        else:
            self.fieldTitle3 = 'Field 3'

        if novel.fieldTitle4 is not None:
            self.fieldTitle4 = novel.fieldTitle4

        else:
            self.fieldTitle4 = 'Field 4'

        if novel.srtChapters != []:
            self.srtChapters = novel.srtChapters

        if novel.scenes is not None:
            self.scenes = novel.scenes

        if novel.chapters is not None:
            self.chapters = novel.chapters

        if novel.characters is not None:
            self.characters = novel.characters

        if novel.locations is not None:
            self.locations = novel.locations

        if novel.items is not None:
            self.items = novel.items

    def get_projectTemplateSubst(self):
        return dict(
            Title=self.title,
            Desc=self.convert_from_yw(self.desc),
            AuthorName=self.author,
            FieldTitle1=self.fieldTitle1,
            FieldTitle2=self.fieldTitle2,
            FieldTitle3=self.fieldTitle3,
            FieldTitle4=self.fieldTitle4,
        )

    def get_chapterSubst(self, chId, chapterNumber):
        return dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self.chapters[chId].title,
            Desc=self.convert_from_yw(self.chapters[chId].desc),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )

    def get_sceneSubst(self, scId, sceneNumber, wordsTotal, lettersTotal):

        if self.scenes[scId].tags is not None:
            tags = ', '.join(self.scenes[scId].tags)

        else:
            tags = ''

        if self.scenes[scId].characters is not None:
            sChList = []

            for chId in self.scenes[scId].characters:
                sChList.append(self.characters[chId].title)

            sceneChars = ', '.join(sChList)
            viewpointChar = sChList[0]

        else:
            sceneChars = ''
            viewpointChar = ''

        if self.scenes[scId].locations is not None:
            sLcList = []

            for lcId in self.scenes[scId].locations:
                sLcList.append(self.locations[lcId].title)

            sceneLocs = ', '.join(sLcList)

        else:
            sceneLocs = ''

        if self.scenes[scId].items is not None:
            sItList = []

            for itId in self.scenes[scId].items:
                sItList.append(self.items[itId].title)

            sceneItems = ', '.join(sItList)

        else:
            sceneItems = ''

        if self.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER

        else:
            reactionScene = Scene.ACTION_MARKER

        return dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self.scenes[scId].title,
            Desc=self.convert_from_yw(self.scenes[scId].desc),
            WordCount=str(self.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.scenes[scId].status],
            SceneContent=self.convert_from_yw(
                self.scenes[scId].sceneContent),
            FieldTitle1=self.fieldTitle1,
            FieldTitle2=self.fieldTitle2,
            FieldTitle3=self.fieldTitle3,
            FieldTitle4=self.fieldTitle4,
            Field1=self.scenes[scId].field1,
            Field2=self.scenes[scId].field2,
            Field3=self.scenes[scId].field3,
            Field4=self.scenes[scId].field4,
            Date=self.scenes[scId].date,
            Time=self.scenes[scId].time,
            Day=self.scenes[scId].day,
            Hour=self.scenes[scId].hour,
            Minute=self.scenes[scId].minute,
            LastsDays=self.scenes[scId].lastsDays,
            LastsHours=self.scenes[scId].lastsHours,
            LastsMinutes=self.scenes[scId].lastsMinutes,
            ReactionScene=reactionScene,
            Goal=self.convert_from_yw(self.scenes[scId].goal),
            Conflict=self.convert_from_yw(self.scenes[scId].conflict),
            Outcome=self.convert_from_yw(self.scenes[scId].outcome),
            Tags=tags,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self.convert_from_yw(self.scenes[scId].sceneNotes),
            ProjectName=self.projectName,
            ProjectPath=self.projectPath,
        )

    def get_characterSubst(self, crId):

        if self.characters[crId].tags is not None:
            tags = ', '.join(self.characters[crId].tags)

        else:
            tags = ''

        if self.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER

        else:
            characterStatus = Character.MINOR_MARKER

        return dict(
            ID=crId,
            Title=self.characters[crId].title,
            Desc=self.convert_from_yw(self.characters[crId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.characters[crId].aka),
            Notes=self.convert_from_yw(self.characters[crId].notes),
            Bio=self.convert_from_yw(self.characters[crId].bio),
            Goals=self.convert_from_yw(self.characters[crId].goals),
            FullName=FileExport.convert_from_yw(
                self, self.characters[crId].fullName),
            Status=characterStatus,
        )

    def get_locationSubst(self, lcId):

        if self.locations[lcId].tags is not None:
            tags = ', '.join(self.locations[lcId].tags)

        else:
            tags = ''

        return dict(
            ID=lcId,
            Title=self.locations[lcId].title,
            Desc=self.convert_from_yw(self.locations[lcId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.locations[lcId].aka),
        )

    def get_itemSubst(self, itId):

        if self.items[itId].tags is not None:
            tags = ', '.join(self.items[itId].tags)

        else:
            tags = ''

        return dict(
            ID=itId,
            Title=self.items[itId].title,
            Desc=self.convert_from_yw(self.items[itId].desc),
            Tags=tags,
            AKA=FileExport.convert_from_yw(self, self.items[itId].aka),
        )

    def write(self):
        lines = []
        wordsTotal = 0
        lettersTotal = 0
        chapterNumber = 0
        sceneNumber = 0

        template = Template(self.fileHeader)
        lines.append(template.safe_substitute(self.get_projectTemplateSubst()))

        for chId in self.srtChapters:

            if self.chapters[chId].isUnused:

                if self.unusedChapterTemplate != '':
                    template = Template(self.unusedChapterTemplate)

                else:
                    continue

            elif self.chapters[chId].chType != 0:

                if self.infoChapterTemplate != '':
                    template = Template(self.infoChapterTemplate)

                else:
                    continue

            elif self.chapters[chId].chLevel == 1 and self.partTemplate != '':
                template = Template(self.partTemplate)

            else:
                template = Template(self.chapterTemplate)
                chapterNumber += 1

            lines.append(template.safe_substitute(
                self.get_chapterSubst(chId, chapterNumber)))
            firstSceneInChapter = True

            for scId in self.chapters[chId].srtScenes:
                wordsTotal += self.scenes[scId].wordCount
                lettersTotal += self.scenes[scId].letterCount

                if self.scenes[scId].isUnused or self.chapters[chId].isUnused or self.scenes[scId].doNotExport:

                    if self.unusedSceneTemplate != '':
                        template = Template(self.unusedSceneTemplate)

                    else:
                        continue

                elif self.chapters[chId].chType != 0:

                    if self.infoSceneTemplate != '':
                        template = Template(self.infoSceneTemplate)

                    else:
                        continue

                else:
                    sceneNumber += 1
                    template = Template(self.sceneTemplate)

                if not (firstSceneInChapter or self.scenes[scId].appendToPrev):
                    lines.append(self.sceneDivider)

                lines.append(template.safe_substitute(self.get_sceneSubst(
                    scId, sceneNumber, wordsTotal, lettersTotal)))

                firstSceneInChapter = False

            if self.chapters[chId].isUnused and self.unusedChapterEndTemplate != '':
                lines.append(self.unusedChapterEndTemplate)

            elif self.chapters[chId].chType != 0 and self.infoChapterEndTemplate != '':
                lines.append(self.infoChapterEndTemplate)

            else:
                lines.append(self.chapterEndTemplate)

        for crId in self.characters:
            template = Template(self.characterTemplate)
            lines.append(template.safe_substitute(
                self.get_characterSubst(crId)))

        for lcId in self.locations:
            template = Template(self.locationTemplate)
            lines.append(template.safe_substitute(
                self.get_locationSubst(lcId)))

        for itId in self.items:
            template = Template(self.itemTemplate)
            lines.append(template.safe_substitute(self.get_itemSubst(itId)))

        lines.append(self.fileFooter)
        text = ''.join(lines)

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)

        except:
            return 'ERROR: Cannot write "' + self.filePath + '".'

        return 'SUCCESS: Content written to "' + self.filePath + '".'


class HtmlExport(FileExport):
    EXTENSION = '.html'
    # overwrites Novel._FILE_EXTENSION

    def convert_from_yw(self, text):
        """Convert yw7 markup to target format."""

        try:
            text = text.replace('\n', '</p>\n<p>')
            text = text.replace('[i]', '<em>')
            text = text.replace('[/i]', '</em>')
            text = text.replace('[b]', '<strong>')
            text = text.replace('[/b]', '</strong>')
            text = text.replace('<p></p>', '<p><br /></p>')
            text = text.replace('/*', '<!--')
            text = text.replace('*/', '-->')

        except AttributeError:
            text = ''

        return(text)


def read_html_file(filePath):
    """Open a html file being encoded utf-8 or ANSI.
    Return a tuple:
    [0] = Message beginning with SUCCESS or ERROR.
    [1] = The file content in a single string. 
    """
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            text = (f.read())
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        try:
            with open(filePath, 'r') as f:
                text = (f.read())

        except(FileNotFoundError):
            return ('ERROR: "' + filePath + '" not found.', None)

    return ('SUCCESS', text)


class Exporter(HtmlExport):

    # Template files

    _HTML_HEADER = '/html_header.html'

    _CHARACTER_TEMPLATE = '/character_template.html'
    _LOCATION_TEMPLATE = '/location_template.html'
    _ITEM_TEMPLATE = '/item_template.html'

    _HTML_FOOTER = '/html_footer.html'

    _PART_TEMPLATE = '/part_template.html'
    _CHAPTER_TEMPLATE = '/chapter_template.html'
    _UNUSED_CHAPTER_TEMPLATE = '/unused_chapter_template.html'
    _INFO_CHAPTER_TEMPLATE = '/info_chapter_template.html'

    _CHAPTER_END_TEMPLATE = '/chapter_end_template.html'
    _UNUSED_CHAPTER_END_TEMPLATE = '/unused_chapter_end_template.html'
    _INFO_CHAPTER_END_TEMPLATE = '/info_chapter_end_template.html'

    _SCENE_TEMPLATE = '/scene_template.html'
    _UNUSED_SCENE_TEMPLATE = '/unused_scene_template.html'
    _INFO_SCENE_TEMPLATE = '/info_scene_template.html'
    _SCENE_DIVIDER = '/scene_divider.html'

    def __init__(self, filePath, templatePath='.'):
        FileExport.__init__(self, filePath)

        # Initialize templates.

        self.templatePath = templatePath

        # Project level.

        result = read_html_file(self.templatePath + self._HTML_HEADER)

        if result[1] is not None:
            self.fileHeader = result[1]

        result = read_html_file(self.templatePath + self._CHARACTER_TEMPLATE)

        if result[1] is not None:
            self.characterTemplate = result[1]

        result = read_html_file(self.templatePath + self._LOCATION_TEMPLATE)

        if result[1] is not None:
            self.locationTemplate = result[1]

        result = read_html_file(self.templatePath + self._ITEM_TEMPLATE)

        if result[1] is not None:
            self.itemTemplate = result[1]

        result = read_html_file(self.templatePath + self._HTML_FOOTER)

        if result[1] is not None:
            self.fileFooter = result[1]

        # Chapter level.

        result = read_html_file(self.templatePath + self._PART_TEMPLATE)

        if result[1] is not None:
            self.partTemplate = result[1]

        result = read_html_file(self.templatePath + self._CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.chapterTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._UNUSED_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.unusedChapterTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._INFO_CHAPTER_TEMPLATE)

        if result[1] is not None:
            self.infoChapterTemplate = result[1]

        result = read_html_file(self.templatePath + self._CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.chapterEndTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._UNUSED_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.unusedChapterEndTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._INFO_CHAPTER_END_TEMPLATE)

        if result[1] is not None:
            self.infoChapterEndTemplate = result[1]

        # Scene level.

        result = read_html_file(self.templatePath + self._SCENE_TEMPLATE)

        if result[1] is not None:
            self.sceneTemplate = result[1]

        result = read_html_file(
            self.templatePath + self._UNUSED_SCENE_TEMPLATE)

        if result[1] is not None:
            self.unusedSceneTemplate = result[1]

        result = read_html_file(self.templatePath + self._INFO_SCENE_TEMPLATE)

        if result[1] is not None:
            self.infoSceneTemplate = result[1]

        result = read_html_file(self.templatePath + self._SCENE_DIVIDER)

        if result[1] is not None:
            self.sceneDivider = result[1]


def run(sourcePath, templatePath, suffix, silentMode=True):
    fileName, FileExtension = os.path.splitext(sourcePath)

    if FileExtension in ['.yw6', '.yw7']:
        document = Exporter('', templatePath)
        document.SUFFIX = suffix

    else:
        sys.exit('ERROR: File type is not supported.')

    converter = YwCnvGui(sourcePath, document, silentMode)


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
    args = parser.parse_args()

    if args.templatePath is not None:
        templatePath = args.templatePath

    else:
        templatePath = os.path.dirname(args.sourcePath)

    if templatePath == '':
        templatePath = '.'

    if args.suffix is not None:
        suffix = args.suffix

    else:
        suffix = ''

    run(args.sourcePath, templatePath, suffix, False)
