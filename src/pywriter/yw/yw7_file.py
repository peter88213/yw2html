"""Provide a class for yWriter 7 project import and export.

yWriter version-specific file representations inherit from this class.

Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re
from html import unescape
import xml.etree.ElementTree as ET
from pywriter.pywriter_globals import *
from pywriter.model.novel import Novel
from pywriter.model.id_generator import create_id
from pywriter.model.splitter import Splitter
from pywriter.yw.xml_indent import indent


class Yw7File(Novel):
    """yWriter 7 project file representation.

    Public methods: 
        read() -- parse the yWriter xml file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the yWriter xml file.
        is_locked() -- check whether the yw7 file is locked by yWriter.
        remove_custom_fields() -- Remove custom fields from the yWriter file.

    Public instance variables:
        tree -- xml element tree of the yWriter project
        scenesSplit -- bool: True, if a scene or chapter is split during merging.
    """
    DESCRIPTION = _('yWriter 7 project')
    EXTENSION = '.yw7'
    _CDATA_TAGS = ['Title', 'AuthorName', 'Bio', 'Desc',
                   'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                   'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                   'AKA', 'ImageFile', 'FullName', 'Goals',
                   'Notes', 'RTFFile', 'SceneContent',
                   'Outcome', 'Goal', 'Conflict']
    # Names of xml elements containing CDATA.
    # ElementTree.write omits CDATA tags, so they have to be inserted afterwards.

    _PRJ_KWVAR = (
        'Field_LanguageCode',
        'Field_CountryCode',
        )

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath -- str: path to the yw7 file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.tree = None
        self.scenesSplit = False

        #--- Initialize custom keyword variables.
        for field in self._PRJ_KWVAR:
            self.kwVar[field] = None

    def read(self):
        """Parse the yWriter xml file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def read_project(root):
            #--- Read attributes at project level from the xml element tree.
            prj = root.find('PROJECT')

            if prj.find('Title') is not None:
                self.title = prj.find('Title').text

            if prj.find('AuthorName') is not None:
                self.authorName = prj.find('AuthorName').text

            if prj.find('Bio') is not None:
                self.authorBio = prj.find('Bio').text

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

            #--- Initialize custom keyword variables.
            for fieldName in self._PRJ_KWVAR:
                self.kwVar[fieldName] = None

            #--- Read project custom fields.
            for prjFields in prj.findall('Fields'):
                for fieldName in self._PRJ_KWVAR:
                    field = prjFields.find(fieldName)
                    if field is not None:
                        self.kwVar[fieldName] = field.text

            # This is for projects written with v7.6 - v7.10:
            if self.kwVar['Field_LanguageCode']:
                self.languageCode = self.kwVar['Field_LanguageCode']
            if self.kwVar['Field_CountryCode']:
                self.countryCode = self.kwVar['Field_CountryCode']

        def read_locations(root):
            #--- Read locations from the xml element tree.
            self.srtLocations = []
            # This is necessary for re-reading.
            for loc in root.iter('LOCATION'):
                lcId = loc.find('ID').text
                self.srtLocations.append(lcId)
                self.locations[lcId] = self.WE_CLASS()

                if loc.find('Title') is not None:
                    self.locations[lcId].title = loc.find('Title').text

                if loc.find('ImageFile') is not None:
                    self.locations[lcId].image = loc.find('ImageFile').text

                if loc.find('Desc') is not None:
                    self.locations[lcId].desc = loc.find('Desc').text

                if loc.find('AKA') is not None:
                    self.locations[lcId].aka = loc.find('AKA').text

                if loc.find('Tags') is not None:
                    if loc.find('Tags').text is not None:
                        tags = string_to_list(loc.find('Tags').text)
                        self.locations[lcId].tags = self._strip_spaces(tags)

                #--- Initialize custom keyword variables.
                for fieldName in self._LOC_KWVAR:
                    self.locations[lcId].kwVar[fieldName] = None

                #--- Read location custom fields.
                for lcFields in loc.findall('Fields'):
                    for fieldName in self._LOC_KWVAR:
                        field = lcFields.find(fieldName)
                        if field is not None:
                            self.locations[lcId].kwVar[fieldName] = field.text

        def read_items(root):
            #--- Read items from the xml element tree.
            self.srtItems = []
            # This is necessary for re-reading.
            for itm in root.iter('ITEM'):
                itId = itm.find('ID').text
                self.srtItems.append(itId)
                self.items[itId] = self.WE_CLASS()

                if itm.find('Title') is not None:
                    self.items[itId].title = itm.find('Title').text

                if itm.find('ImageFile') is not None:
                    self.items[itId].image = itm.find('ImageFile').text

                if itm.find('Desc') is not None:
                    self.items[itId].desc = itm.find('Desc').text

                if itm.find('AKA') is not None:
                    self.items[itId].aka = itm.find('AKA').text

                if itm.find('Tags') is not None:
                    if itm.find('Tags').text is not None:
                        tags = string_to_list(itm.find('Tags').text)
                        self.items[itId].tags = self._strip_spaces(tags)

                #--- Initialize custom keyword variables.
                for fieldName in self._ITM_KWVAR:
                    self.items[itId].kwVar[fieldName] = None

                #--- Read item custom fields.
                for itFields in itm.findall('Fields'):
                    for fieldName in self._ITM_KWVAR:
                        field = itFields.find(fieldName)
                        if field is not None:
                            self.items[itId].kwVar[fieldName] = field.text

        def read_characters(root):
            #--- Read characters from the xml element tree.
            self.srtCharacters = []
            # This is necessary for re-reading.
            for crt in root.iter('CHARACTER'):
                crId = crt.find('ID').text
                self.srtCharacters.append(crId)
                self.characters[crId] = self.CHARACTER_CLASS()

                if crt.find('Title') is not None:
                    self.characters[crId].title = crt.find('Title').text

                if crt.find('ImageFile') is not None:
                    self.characters[crId].image = crt.find('ImageFile').text

                if crt.find('Desc') is not None:
                    self.characters[crId].desc = crt.find('Desc').text

                if crt.find('AKA') is not None:
                    self.characters[crId].aka = crt.find('AKA').text

                if crt.find('Tags') is not None:
                    if crt.find('Tags').text is not None:
                        tags = string_to_list(crt.find('Tags').text)
                        self.characters[crId].tags = self._strip_spaces(tags)

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

                #--- Initialize custom keyword variables.
                for fieldName in self._CRT_KWVAR:
                    self.characters[crId].kwVar[fieldName] = None

                #--- Read character custom fields.
                for crFields in crt.findall('Fields'):
                    for fieldName in self._CRT_KWVAR:
                        field = crFields.find(fieldName)
                        if field is not None:
                            self.characters[crId].kwVar[fieldName] = field.text

        def read_projectnotes(root):
            #--- Read project notes from the xml element tree.
            self.srtPrjNotes = []
            # This is necessary for re-reading.

            try:
                for pnt in root.find('PROJECTNOTES'):
                    if pnt.find('ID') is not None:
                        pnId = pnt.find('ID').text
                        self.srtPrjNotes.append(pnId)
                        self.projectNotes[pnId] = self.PN_CLASS()
                        if pnt.find('Title') is not None:
                            self.projectNotes[pnId].title = pnt.find('Title').text
                        if pnt.find('Desc') is not None:
                            self.projectNotes[pnId].desc = pnt.find('Desc').text

                    #--- Initialize project note custom fields.
                    for fieldName in self._PNT_KWVAR:
                        self.projectNotes[pnId].kwVar[fieldName] = None

                    #--- Read project note custom fields.
                    for pnFields in pnt.findall('Fields'):
                        field = pnFields.find(fieldName)
                        if field is not None:
                            self.projectNotes[pnId].kwVar[fieldName] = field.text
            except:
                pass

        def read_projectvars(root):
            #--- Read relevant project variables from the xml element tree.
            try:
                for projectvar in root.find('PROJECTVARS'):
                    if projectvar.find('Title') is not None:
                        title = projectvar.find('Title').text
                        if title == 'Language':
                            if projectvar.find('Desc') is not None:
                                self.languageCode = projectvar.find('Desc').text

                        elif title == 'Country':
                            if projectvar.find('Desc') is not None:
                                self.countryCode = projectvar.find('Desc').text

                        elif title.startswith('lang='):
                            try:
                                __, langCode = title.split('=')
                                if self.languages is None:
                                    self.languages = []
                                self.languages.append(langCode)
                            except:
                                pass
            except:
                pass

        def read_scenes(root):
            #--- Read attributes at scene level from the xml element tree.
            for scn in root.iter('SCENE'):
                scId = scn.find('ID').text
                self.scenes[scId] = self.SCENE_CLASS()

                if scn.find('Title') is not None:
                    self.scenes[scId].title = scn.find('Title').text

                if scn.find('Desc') is not None:
                    self.scenes[scId].desc = scn.find('Desc').text

                if scn.find('SceneContent') is not None:
                    sceneContent = scn.find('SceneContent').text
                    if sceneContent is not None:
                        self.scenes[scId].sceneContent = sceneContent

                #--- Read scene type.

                # This is how yWriter 7.1.3.0 reads the scene type:
                #
                # Type   |<Unused>|Field_SceneType>|scType
                #--------+--------+----------------+------
                # Notes  | x      | 1              | 1
                # Todo   | x      | 2              | 2
                # Unused | -1     | N/A            | 3
                # Unused | -1     | 0              | 3
                # Normal | N/A    | N/A            | 0
                # Normal | N/A    | 0              | 0

                self.scenes[scId].scType = 0

                #--- Initialize custom keyword variables.
                for fieldName in self._SCN_KWVAR:
                    self.scenes[scId].kwVar[fieldName] = None

                for scFields in scn.findall('Fields'):
                    #--- Read scene custom fields.
                    for fieldName in self._SCN_KWVAR:
                        field = scFields.find(fieldName)
                        if field is not None:
                            self.scenes[scId].kwVar[fieldName] = field.text

                    # Read scene type, if any.
                    if scFields.find('Field_SceneType') is not None:
                        if scFields.find('Field_SceneType').text == '1':
                            self.scenes[scId].scType = 1
                        elif scFields.find('Field_SceneType').text == '2':
                            self.scenes[scId].scType = 2
                if scn.find('Unused') is not None:
                    if self.scenes[scId].scType == 0:
                        self.scenes[scId].scType = 3

                #--- Export when RTF.
                if scn.find('ExportCondSpecific') is None:
                    self.scenes[scId].doNotExport = False
                elif scn.find('ExportWhenRTF') is not None:
                    self.scenes[scId].doNotExport = False
                else:
                    self.scenes[scId].doNotExport = True

                if scn.find('Status') is not None:
                    self.scenes[scId].status = int(scn.find('Status').text)

                if scn.find('Notes') is not None:
                    self.scenes[scId].notes = scn.find('Notes').text

                if scn.find('Tags') is not None:
                    if scn.find('Tags').text is not None:
                        tags = string_to_list(scn.find('Tags').text)
                        self.scenes[scId].tags = self._strip_spaces(tags)

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
                    for dt in dateTime:
                        if '-' in dt:
                            self.scenes[scId].date = dt
                        elif ':' in dt:
                            self.scenes[scId].time = dt
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

                if scn.find('ImageFile') is not None:
                    self.scenes[scId].image = scn.find('ImageFile').text

                if scn.find('Characters') is not None:
                    for characters in scn.find('Characters').iter('CharID'):
                        crId = characters.text
                        if crId in self.srtCharacters:
                            if self.scenes[scId].characters is None:
                                self.scenes[scId].characters = []
                            self.scenes[scId].characters.append(crId)

                if scn.find('Locations') is not None:
                    for locations in scn.find('Locations').iter('LocID'):
                        lcId = locations.text
                        if lcId in self.srtLocations:
                            if self.scenes[scId].locations is None:
                                self.scenes[scId].locations = []
                            self.scenes[scId].locations.append(lcId)

                if scn.find('Items') is not None:
                    for items in scn.find('Items').iter('ItemID'):
                        itId = items.text
                        if itId in self.srtItems:
                            if self.scenes[scId].items is None:
                                self.scenes[scId].items = []
                            self.scenes[scId].items.append(itId)

        def read_chapters(root):
            #--- Read attributes at chapter level from the xml element tree.
            self.srtChapters = []
            # This is necessary for re-reading.
            for chp in root.iter('CHAPTER'):
                chId = chp.find('ID').text
                self.chapters[chId] = self.CHAPTER_CLASS()
                self.srtChapters.append(chId)

                if chp.find('Title') is not None:
                    self.chapters[chId].title = chp.find('Title').text

                if chp.find('Desc') is not None:
                    self.chapters[chId].desc = chp.find('Desc').text

                if chp.find('SectionStart') is not None:
                    self.chapters[chId].chLevel = 1
                else:
                    self.chapters[chId].chLevel = 0

                # This is how yWriter 7.1.3.0 reads the chapter type:
                #
                # Type   |<Unused>|<Type>|<ChapterType>|chType
                # -------+--------+------+--------------------
                # Normal | N/A    | N/A  | N/A         | 0
                # Normal | N/A    | 0    | N/A         | 0
                # Notes  | x      | 1    | N/A         | 1
                # Unused | -1     | 0    | N/A         | 3
                # Normal | N/A    | x    | 0           | 0
                # Notes  | x      | x    | 1           | 1
                # Todo   | x      | x    | 2           | 2
                # Unused | -1     | x    | x           | 3

                self.chapters[chId].chType = 0
                if chp.find('Unused') is not None:
                    yUnused = True
                else:
                    yUnused = False
                if chp.find('ChapterType') is not None:
                    # The file may be created with yWriter version 7.0.7.2+
                    yChapterType = chp.find('ChapterType').text
                    if yChapterType == '2':
                        self.chapters[chId].chType = 2
                    elif yChapterType == '1':
                        self.chapters[chId].chType = 1
                    elif yUnused:
                        self.chapters[chId].chType = 3
                else:
                    # The file may be created with a yWriter version prior to 7.0.7.2
                    if chp.find('Type') is not None:
                        yType = chp.find('Type').text
                        if yType == '1':
                            self.chapters[chId].chType = 1
                        elif yUnused:
                            self.chapters[chId].chType = 3

                self.chapters[chId].suppressChapterTitle = False
                if self.chapters[chId].title is not None:
                    if self.chapters[chId].title.startswith('@'):
                        self.chapters[chId].suppressChapterTitle = True

                #--- Initialize custom keyword variables.
                for fieldName in self._CHP_KWVAR:
                    self.chapters[chId].kwVar[fieldName] = None

                #--- Read chapter fields.
                for chFields in chp.findall('Fields'):
                    if chFields.find('Field_SuppressChapterTitle') is not None:
                        if chFields.find('Field_SuppressChapterTitle').text == '1':
                            self.chapters[chId].suppressChapterTitle = True
                    self.chapters[chId].isTrash = False
                    if chFields.find('Field_IsTrash') is not None:
                        if chFields.find('Field_IsTrash').text == '1':
                            self.chapters[chId].isTrash = True
                    self.chapters[chId].suppressChapterBreak = False
                    if chFields.find('Field_SuppressChapterBreak') is not None:
                        if chFields.find('Field_SuppressChapterBreak').text == '1':
                            self.chapters[chId].suppressChapterBreak = True

                    #--- Read chapter custom fields.
                    for fieldName in self._CHP_KWVAR:
                        field = chFields.find(fieldName)
                        if field is not None:
                            self.chapters[chId].kwVar[fieldName] = field.text

                #--- Read chapter's scene list.
                self.chapters[chId].srtScenes = []
                if chp.find('Scenes') is not None:
                    for scn in chp.find('Scenes').findall('ScID'):
                        scId = scn.text
                        if scId in self.scenes:
                            self.chapters[chId].srtScenes.append(scId)

        #--- Begin reading.
        if self.is_locked():
            return f'{ERROR}{_("yWriter seems to be open. Please close first")}.'
        try:
            self.tree = ET.parse(self.filePath)
        except:
            return f'{ERROR}{_("Can not process file")}: "{os.path.normpath(self.filePath)}".'

        root = self.tree.getroot()
        read_project(root)
        read_locations(root)
        read_items(root)
        read_characters(root)
        read_projectvars(root)
        read_projectnotes(root)
        read_scenes(root)
        read_chapters(root)
        self.adjust_scene_types()
        return 'yWriter project data read in.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """

        def merge_lists(srcLst, tgtLst):
            """Insert srcLst items to tgtLst, if missing.
            """
            j = 0
            for item in srcLst:
                if not item in tgtLst:
                    tgtLst.insert(j, item)
                    j += 1
                else:
                    j = tgtLst.index(item) + 1

        if os.path.isfile(self.filePath):
            message = self.read()
            # initialize data
            if message.startswith(ERROR):
                return message

        #--- Merge and re-order locations.
        if source.srtLocations:
            self.srtLocations = source.srtLocations
            temploc = self.locations
            self.locations = {}
            for lcId in source.srtLocations:

                # Build a new self.locations dictionary sorted like the source.
                self.locations[lcId] = self.WE_CLASS()
                if not lcId in temploc:
                    # A new location has been added
                    temploc[lcId] = self.WE_CLASS()
                if source.locations[lcId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.locations[lcId].title = source.locations[lcId].title
                else:
                    self.locations[lcId].title = temploc[lcId].title
                if source.locations[lcId].image is not None:
                    self.locations[lcId].image = source.locations[lcId].image
                else:
                    self.locations[lcId].desc = temploc[lcId].desc
                if source.locations[lcId].desc is not None:
                    self.locations[lcId].desc = source.locations[lcId].desc
                else:
                    self.locations[lcId].desc = temploc[lcId].desc
                if source.locations[lcId].aka is not None:
                    self.locations[lcId].aka = source.locations[lcId].aka
                else:
                    self.locations[lcId].aka = temploc[lcId].aka
                if source.locations[lcId].tags is not None:
                    self.locations[lcId].tags = source.locations[lcId].tags
                else:
                    self.locations[lcId].tags = temploc[lcId].tags
                for fieldName in self._LOC_KWVAR:
                    try:
                        self.locations[lcId].kwVar[fieldName] = source.locations[lcId].kwVar[fieldName]
                    except:
                        self.locations[lcId].kwVar[fieldName] = temploc[lcId].kwVar.get(fieldName, None)

        #--- Merge and re-order items.
        if source.srtItems:
            self.srtItems = source.srtItems
            tempitm = self.items
            self.items = {}
            for itId in source.srtItems:

                # Build a new self.items dictionary sorted like the source.
                self.items[itId] = self.WE_CLASS()
                if not itId in tempitm:
                    # A new item has been added
                    tempitm[itId] = self.WE_CLASS()
                if source.items[itId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.items[itId].title = source.items[itId].title
                else:
                    self.items[itId].title = tempitm[itId].title
                if source.items[itId].image is not None:
                    self.items[itId].image = source.items[itId].image
                else:
                    self.items[itId].image = tempitm[itId].image
                if source.items[itId].desc is not None:
                    self.items[itId].desc = source.items[itId].desc
                else:
                    self.items[itId].desc = tempitm[itId].desc
                if source.items[itId].aka is not None:
                    self.items[itId].aka = source.items[itId].aka
                else:
                    self.items[itId].aka = tempitm[itId].aka
                if source.items[itId].tags is not None:
                    self.items[itId].tags = source.items[itId].tags
                else:
                    self.items[itId].tags = tempitm[itId].tags
                for fieldName in self._ITM_KWVAR:
                    try:
                        self.items[itId].kwVar[fieldName] = source.items[itId].kwVar[fieldName]
                    except:
                        self.items[itId].kwVar[fieldName] = tempitm[itId].kwVar.get(fieldName, None)

        #--- Merge and re-order characters.
        if source.srtCharacters:
            self.srtCharacters = source.srtCharacters
            tempchr = self.characters
            self.characters = {}
            for crId in source.srtCharacters:

                # Build a new self.characters dictionary sorted like the source.
                self.characters[crId] = self.CHARACTER_CLASS()
                if not crId in tempchr:
                    # A new character has been added
                    tempchr[crId] = self.CHARACTER_CLASS()
                if source.characters[crId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.characters[crId].title = source.characters[crId].title
                else:
                    self.characters[crId].title = tempchr[crId].title
                if source.characters[crId].image is not None:
                    self.characters[crId].image = source.characters[crId].image
                else:
                    self.characters[crId].image = tempchr[crId].image
                if source.characters[crId].desc is not None:
                    self.characters[crId].desc = source.characters[crId].desc
                else:
                    self.characters[crId].desc = tempchr[crId].desc
                if source.characters[crId].aka is not None:
                    self.characters[crId].aka = source.characters[crId].aka
                else:
                    self.characters[crId].aka = tempchr[crId].aka
                if source.characters[crId].tags is not None:
                    self.characters[crId].tags = source.characters[crId].tags
                else:
                    self.characters[crId].tags = tempchr[crId].tags
                if source.characters[crId].notes is not None:
                    self.characters[crId].notes = source.characters[crId].notes
                else:
                    self.characters[crId].notes = tempchr[crId].notes
                if source.characters[crId].bio is not None:
                    self.characters[crId].bio = source.characters[crId].bio
                else:
                    self.characters[crId].bio = tempchr[crId].bio
                if source.characters[crId].goals is not None:
                    self.characters[crId].goals = source.characters[crId].goals
                else:
                    self.characters[crId].goals = tempchr[crId].goals
                if source.characters[crId].fullName is not None:
                    self.characters[crId].fullName = source.characters[crId].fullName
                else:
                    self.characters[crId].fullName = tempchr[crId].fullName
                if source.characters[crId].isMajor is not None:
                    self.characters[crId].isMajor = source.characters[crId].isMajor
                else:
                    self.characters[crId].isMajor = tempchr[crId].isMajor
                for fieldName in self._CRT_KWVAR:
                    try:
                        self.characters[crId].kwVar[fieldName] = source.characters[crId].kwVar[fieldName]
                    except:
                        self.characters[crId].kwVar[fieldName] = tempchr[crId].kwVar.get(fieldName, None)

        #--- Merge and re-order projectNotes.
        if source.srtPrjNotes:
            self.srtPrjNotes = source.srtPrjNotes
            tempPrjn = self.projectNotes
            self.projectNotes = {}
            for pnId in source.srtPrjNotes:

                # Build a new self.projectNotes dictionary sorted like the source.
                self.projectNotes[pnId] = self.PN_CLASS()
                if not pnId in tempPrjn:
                    # A new projecNote has been added
                    tempPrjn[pnId] = self.PN_CLASS()

                if source.projectNotes[pnId].title:
                    # avoids deleting the title, if it is empty by accident
                    self.projectNotes[pnId].title = source.projectNotes[pnId].title
                else:
                    self.projectNotes[pnId].title = tempPrjn[pnId].title

                if source.projectNotes[pnId].desc is not None:
                    self.projectNotes[pnId].desc = source.projectNotes[pnId].desc
                else:
                    self.projectNotes[pnId].desc = tempPrjn[pnId].desc

                for fieldName in self._prn_KWVAR:
                    try:
                        self.projectNotes[pnId].kwVar[fieldName] = source.projectNotes[pnId].kwVar[fieldName]
                    except:
                        self.projectNotes[pnId].kwVar[fieldName] = tempPrjn[pnId].kwVar.get(fieldName, None)

        #--- Merge scenes.
        sourceHasSceneContent = False
        for scId in source.scenes:
            if not scId in self.scenes:
                self.scenes[scId] = self.SCENE_CLASS()

            if source.scenes[scId].title:
                # avoids deleting the title, if it is empty by accident
                self.scenes[scId].title = source.scenes[scId].title
            if source.scenes[scId].desc is not None:
                self.scenes[scId].desc = source.scenes[scId].desc

            if source.scenes[scId].sceneContent is not None:
                self.scenes[scId].sceneContent = source.scenes[scId].sceneContent
                sourceHasSceneContent = True
            if source.scenes[scId].scType is not None:
                self.scenes[scId].scType = source.scenes[scId].scType

            if source.scenes[scId].status is not None:
                self.scenes[scId].status = source.scenes[scId].status

            if source.scenes[scId].notes is not None:
                self.scenes[scId].notes = source.scenes[scId].notes

            if source.scenes[scId].tags is not None:
                self.scenes[scId].tags = source.scenes[scId].tags

            if source.scenes[scId].field1 is not None:
                self.scenes[scId].field1 = source.scenes[scId].field1

            if source.scenes[scId].field2 is not None:
                self.scenes[scId].field2 = source.scenes[scId].field2

            if source.scenes[scId].field3 is not None:
                self.scenes[scId].field3 = source.scenes[scId].field3

            if source.scenes[scId].field4 is not None:
                self.scenes[scId].field4 = source.scenes[scId].field4

            if source.scenes[scId].appendToPrev is not None:
                self.scenes[scId].appendToPrev = source.scenes[scId].appendToPrev

            if source.scenes[scId].date or source.scenes[scId].time:
                if source.scenes[scId].date is not None:
                    self.scenes[scId].date = source.scenes[scId].date
                if source.scenes[scId].time is not None:
                    self.scenes[scId].time = source.scenes[scId].time
            elif source.scenes[scId].minute or source.scenes[scId].hour or source.scenes[scId].day:
                self.scenes[scId].date = None
                self.scenes[scId].time = None

            if source.scenes[scId].minute is not None:
                self.scenes[scId].minute = source.scenes[scId].minute

            if source.scenes[scId].hour is not None:
                self.scenes[scId].hour = source.scenes[scId].hour

            if source.scenes[scId].day is not None:
                self.scenes[scId].day = source.scenes[scId].day

            if source.scenes[scId].lastsMinutes is not None:
                self.scenes[scId].lastsMinutes = source.scenes[scId].lastsMinutes

            if source.scenes[scId].lastsHours is not None:
                self.scenes[scId].lastsHours = source.scenes[scId].lastsHours

            if source.scenes[scId].lastsDays is not None:
                self.scenes[scId].lastsDays = source.scenes[scId].lastsDays

            if source.scenes[scId].isReactionScene is not None:
                self.scenes[scId].isReactionScene = source.scenes[scId].isReactionScene

            if source.scenes[scId].isSubPlot is not None:
                self.scenes[scId].isSubPlot = source.scenes[scId].isSubPlot

            if source.scenes[scId].goal is not None:
                self.scenes[scId].goal = source.scenes[scId].goal

            if source.scenes[scId].conflict is not None:
                self.scenes[scId].conflict = source.scenes[scId].conflict

            if source.scenes[scId].outcome is not None:
                self.scenes[scId].outcome = source.scenes[scId].outcome

            if source.scenes[scId].characters is not None:
                self.scenes[scId].characters = []
                for crId in source.scenes[scId].characters:
                    if crId in self.characters:
                        self.scenes[scId].characters.append(crId)

            if source.scenes[scId].locations is not None:
                self.scenes[scId].locations = []
                for lcId in source.scenes[scId].locations:
                    if lcId in self.locations:
                        self.scenes[scId].locations.append(lcId)

            if source.scenes[scId].items is not None:
                self.scenes[scId].items = []
                for itId in source.scenes[scId].items:
                    if itId in self.items:
                        self.scenes[scId].items.append(itId)

            for fieldName in self._SCN_KWVAR:
                try:
                    self.scenes[scId].kwVar[fieldName] = source.scenes[scId].kwVar[fieldName]
                except:
                    pass

        #--- Merge chapters.
        for chId in source.chapters:
            if not chId in self.chapters:
                self.chapters[chId] = self.CHAPTER_CLASS()

            if source.chapters[chId].title:
                # avoids deleting the title, if it is empty by accident
                self.chapters[chId].title = source.chapters[chId].title

            if source.chapters[chId].desc is not None:
                self.chapters[chId].desc = source.chapters[chId].desc

            if source.chapters[chId].chLevel is not None:
                self.chapters[chId].chLevel = source.chapters[chId].chLevel

            if source.chapters[chId].chType is not None:
                self.chapters[chId].chType = source.chapters[chId].chType

            if source.chapters[chId].suppressChapterTitle is not None:
                self.chapters[chId].suppressChapterTitle = source.chapters[chId].suppressChapterTitle

            if source.chapters[chId].suppressChapterBreak is not None:
                self.chapters[chId].suppressChapterBreak = source.chapters[chId].suppressChapterBreak

            if source.chapters[chId].isTrash is not None:
                self.chapters[chId].isTrash = source.chapters[chId].isTrash

            for fieldName in self._CHP_KWVAR:
                try:
                    self.chapters[chId].kwVar[fieldName] = source.chapters[chId].kwVar[fieldName]
                except:
                    pass

            #--- Merge the chapter's scene list.
            # New scenes may be added.
            # Existing scenes may be moved to another chapter.
            # Deletion of scenes is not considered.
            # The scene's sort order may not change.

            # Remove scenes that have been moved to another chapter from the scene list.
            srtScenes = []
            for scId in self.chapters[chId].srtScenes:
                if scId in source.chapters[chId].srtScenes or not scId in source.scenes:
                    # The scene has not moved to another chapter or isn't imported
                    srtScenes.append(scId)
            self.chapters[chId].srtScenes = srtScenes

            # Add new or moved scenes to the scene list.
            merge_lists(source.chapters[chId].srtScenes, self.chapters[chId].srtScenes)

        #--- Merge project attributes.
        if source.title:
            # avoids deleting the title, if it is empty by accident
            self.title = source.title

        if source.desc is not None:
            self.desc = source.desc

        if source.authorName is not None:
            self.authorName = source.authorName

        if source.authorBio is not None:
            self.authorBio = source.authorBio

        if source.fieldTitle1 is not None:
            self.fieldTitle1 = source.fieldTitle1

        if source.fieldTitle2 is not None:
            self.fieldTitle2 = source.fieldTitle2

        if source.fieldTitle3 is not None:
            self.fieldTitle3 = source.fieldTitle3

        if source.fieldTitle4 is not None:
            self.fieldTitle4 = source.fieldTitle4

        if source.languageCode is not None:
            self.languageCode = source.languageCode

        if source.countryCode is not None:
            self.countryCode = source.countryCode

        if source.languages is not None:
            self.languages = source.languages

        for fieldName in self._PRJ_KWVAR:
            try:
                self.kwVar[fieldName] = source.kwVar[fieldName]
            except:
                pass

        # Add new chapters to the chapter list.
        # Deletion of chapters is not considered.
        # The sort order of chapters may not change.
        merge_lists(source.srtChapters, self.srtChapters)

        # Split scenes by inserted part/chapter/scene dividers.
        # This must be done after regular merging
        # in order to avoid creating duplicate IDs.
        if sourceHasSceneContent:
            sceneSplitter = Splitter()
            self.scenesSplit = sceneSplitter.split_scenes(self)
        self.adjust_scene_types()
        return 'yWriter project data updated or created.'

    def write(self):
        """Write instance variables to the yWriter xml file.
        
        Open the yWriter xml file located at filePath and replace the instance variables 
        not being None. Create new XML elements if necessary.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if self.is_locked():
            return f'{ERROR}{_("yWriter seems to be open. Please close first")}.'

        if self.languages is None:
            self.get_languages()
        self._build_element_tree()
        message = self._write_element_tree(self)
        if message.startswith(ERROR):
            return message

        return self._postprocess_xml_file(self.filePath)

    def is_locked(self):
        """Check whether the yw7 file is locked by yWriter.
        
        Return True if a .lock file placed by yWriter exists.
        Otherwise, return False. 
        """
        return os.path.isfile(f'{self.filePath}.lock')

    def _build_element_tree(self):
        """Modify the yWriter project attributes of an existing xml element tree."""

        def build_scene_subtree(xmlScn, prjScn):
            if prjScn.title is not None:
                try:
                    xmlScn.find('Title').text = prjScn.title
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Title').text = prjScn.title
            if xmlScn.find('BelongsToChID') is None:
                for chId in self.chapters:
                    if scId in self.chapters[chId].srtScenes:
                        ET.SubElement(xmlScn, 'BelongsToChID').text = chId
                        break

            if prjScn.desc is not None:
                try:
                    xmlScn.find('Desc').text = prjScn.desc
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Desc').text = prjScn.desc

            if xmlScn.find('SceneContent') is None:
                ET.SubElement(xmlScn, 'SceneContent').text = prjScn.sceneContent

            if xmlScn.find('WordCount') is None:
                ET.SubElement(xmlScn, 'WordCount').text = str(prjScn.wordCount)

            if xmlScn.find('LetterCount') is None:
                ET.SubElement(xmlScn, 'LetterCount').text = str(prjScn.letterCount)

            #--- Write scene type.
            #
            # This is how yWriter 7.1.3.0 writes the scene type:
            #
            # Type   |<Unused>|Field_SceneType>|scType
            #--------+--------+----------------+------
            # Normal | N/A    | N/A            | 0
            # Notes  | -1     | 1              | 1
            # Todo   | -1     | 2              | 2
            # Unused | -1     | 0              | 3

            scTypeEncoding = (
                (False, None),
                (True, '1'),
                (True, '2'),
                (True, '0'),
                )
            if prjScn.scType is None:
                prjScn.scType = 0
            yUnused, ySceneType = scTypeEncoding[prjScn.scType]

            # <Unused> (remove, if scene is "Normal").
            if yUnused:
                if xmlScn.find('Unused') is None:
                    ET.SubElement(xmlScn, 'Unused').text = '-1'
            elif xmlScn.find('Unused') is not None:
                xmlScn.remove(xmlScn.find('Unused'))

            # <Fields><Field_SceneType> (remove, if scene is "Normal")
            scFields = xmlScn.find('Fields')
            if scFields is not None:
                fieldScType = scFields.find('Field_SceneType')
                if ySceneType is None:
                    if fieldScType is not None:
                        scFields.remove(fieldScType)
                else:
                    try:
                        fieldScType.text = ySceneType
                    except(AttributeError):
                        ET.SubElement(scFields, 'Field_SceneType').text = ySceneType
            elif ySceneType is not None:
                scFields = ET.SubElement(xmlScn, 'Fields')
                ET.SubElement(scFields, 'Field_SceneType').text = ySceneType

            #--- Write scene custom fields.
            for field in self._SCN_KWVAR:
                if self.scenes[scId].kwVar.get(field, None):
                    if scFields is None:
                        scFields = ET.SubElement(xmlScn, 'Fields')
                    try:
                        scFields.find(field).text = self.scenes[scId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(scFields, field).text = self.scenes[scId].kwVar[field]
                elif scFields is not None:
                    try:
                        scFields.remove(scFields.find(field))
                    except:
                        pass

            if prjScn.status is not None:
                try:
                    xmlScn.find('Status').text = str(prjScn.status)
                except:
                    ET.SubElement(xmlScn, 'Status').text = str(prjScn.status)

            if prjScn.notes is not None:
                try:
                    xmlScn.find('Notes').text = prjScn.notes
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Notes').text = prjScn.notes

            if prjScn.tags is not None:
                try:
                    xmlScn.find('Tags').text = list_to_string(prjScn.tags)
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Tags').text = list_to_string(prjScn.tags)

            if prjScn.field1 is not None:
                try:
                    xmlScn.find('Field1').text = prjScn.field1
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field1').text = prjScn.field1

            if prjScn.field2 is not None:
                try:
                    xmlScn.find('Field2').text = prjScn.field2
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field2').text = prjScn.field2

            if prjScn.field3 is not None:
                try:
                    xmlScn.find('Field3').text = prjScn.field3
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field3').text = prjScn.field3

            if prjScn.field4 is not None:
                try:
                    xmlScn.find('Field4').text = prjScn.field4
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Field4').text = prjScn.field4

            if prjScn.appendToPrev:
                if xmlScn.find('AppendToPrev') is None:
                    ET.SubElement(xmlScn, 'AppendToPrev').text = '-1'
            elif xmlScn.find('AppendToPrev') is not None:
                xmlScn.remove(xmlScn.find('AppendToPrev'))

            # Date/time information
            if (prjScn.date is not None) and (prjScn.time is not None):
                dateTime = f'{prjScn.date} {prjScn.time}'
                if xmlScn.find('SpecificDateTime') is not None:
                    xmlScn.find('SpecificDateTime').text = dateTime
                else:
                    ET.SubElement(xmlScn, 'SpecificDateTime').text = dateTime
                    ET.SubElement(xmlScn, 'SpecificDateMode').text = '-1'

                    if xmlScn.find('Day') is not None:
                        xmlScn.remove(xmlScn.find('Day'))

                    if xmlScn.find('Hour') is not None:
                        xmlScn.remove(xmlScn.find('Hour'))

                    if xmlScn.find('Minute') is not None:
                        xmlScn.remove(xmlScn.find('Minute'))

            elif (prjScn.day is not None) or (prjScn.hour is not None) or (prjScn.minute is not None):

                if xmlScn.find('SpecificDateTime') is not None:
                    xmlScn.remove(xmlScn.find('SpecificDateTime'))

                if xmlScn.find('SpecificDateMode') is not None:
                    xmlScn.remove(xmlScn.find('SpecificDateMode'))
                if prjScn.day is not None:
                    try:
                        xmlScn.find('Day').text = prjScn.day
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Day').text = prjScn.day
                if prjScn.hour is not None:
                    try:
                        xmlScn.find('Hour').text = prjScn.hour
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Hour').text = prjScn.hour
                if prjScn.minute is not None:
                    try:
                        xmlScn.find('Minute').text = prjScn.minute
                    except(AttributeError):
                        ET.SubElement(xmlScn, 'Minute').text = prjScn.minute

            if prjScn.lastsDays is not None:
                try:
                    xmlScn.find('LastsDays').text = prjScn.lastsDays
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsDays').text = prjScn.lastsDays

            if prjScn.lastsHours is not None:
                try:
                    xmlScn.find('LastsHours').text = prjScn.lastsHours
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsHours').text = prjScn.lastsHours

            if prjScn.lastsMinutes is not None:
                try:
                    xmlScn.find('LastsMinutes').text = prjScn.lastsMinutes
                except(AttributeError):
                    ET.SubElement(xmlScn, 'LastsMinutes').text = prjScn.lastsMinutes

            # Plot related information
            if prjScn.isReactionScene:
                if xmlScn.find('ReactionScene') is None:
                    ET.SubElement(xmlScn, 'ReactionScene').text = '-1'
            elif xmlScn.find('ReactionScene') is not None:
                xmlScn.remove(xmlScn.find('ReactionScene'))

            if prjScn.isSubPlot:
                if xmlScn.find('SubPlot') is None:
                    ET.SubElement(xmlScn, 'SubPlot').text = '-1'
            elif xmlScn.find('SubPlot') is not None:
                xmlScn.remove(xmlScn.find('SubPlot'))

            if prjScn.goal is not None:
                try:
                    xmlScn.find('Goal').text = prjScn.goal
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Goal').text = prjScn.goal

            if prjScn.conflict is not None:
                try:
                    xmlScn.find('Conflict').text = prjScn.conflict
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Conflict').text = prjScn.conflict

            if prjScn.outcome is not None:
                try:
                    xmlScn.find('Outcome').text = prjScn.outcome
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Outcome').text = prjScn.outcome

            if prjScn.image is not None:
                try:
                    xmlScn.find('ImageFile').text = prjScn.image
                except(AttributeError):
                    ET.SubElement(xmlScn, 'ImageFile').text = prjScn.image

            #--- Characters/locations/items
            if prjScn.characters is not None:
                characters = xmlScn.find('Characters')
                try:
                    for oldCrId in characters.findall('CharID'):
                        characters.remove(oldCrId)
                except(AttributeError):
                    characters = ET.SubElement(xmlScn, 'Characters')
                for crId in prjScn.characters:
                    ET.SubElement(characters, 'CharID').text = crId

            if prjScn.locations is not None:
                locations = xmlScn.find('Locations')
                try:
                    for oldLcId in locations.findall('LocID'):
                        locations.remove(oldLcId)
                except(AttributeError):
                    locations = ET.SubElement(xmlScn, 'Locations')
                for lcId in prjScn.locations:
                    ET.SubElement(locations, 'LocID').text = lcId

            if prjScn.items is not None:
                items = xmlScn.find('Items')
                try:
                    for oldItId in items.findall('ItemID'):
                        items.remove(oldItId)
                except(AttributeError):
                    items = ET.SubElement(xmlScn, 'Items')
                for itId in prjScn.items:
                    ET.SubElement(items, 'ItemID').text = itId

        def build_chapter_subtree(xmlChp, prjChp, sortOrder):
            try:
                xmlChp.find('SortOrder').text = str(sortOrder)
            except(AttributeError):
                ET.SubElement(xmlChp, 'SortOrder').text = str(sortOrder)
            try:
                xmlChp.find('Title').text = prjChp.title
            except(AttributeError):
                ET.SubElement(xmlChp, 'Title').text = prjChp.title

            if prjChp.desc is not None:
                try:
                    xmlChp.find('Desc').text = prjChp.desc
                except(AttributeError):
                    ET.SubElement(xmlChp, 'Desc').text = prjChp.desc

            if xmlChp.find('SectionStart') is not None:
                if prjChp.chLevel == 0:
                    xmlChp.remove(xmlChp.find('SectionStart'))
            elif prjChp.chLevel == 1:
                ET.SubElement(xmlChp, 'SectionStart').text = '-1'

            # This is how yWriter 7.1.3.0 writes the chapter type:
            #
            # Type   |<Unused>|<Type>|<ChapterType>|chType
            #--------+--------+------+-------------+------
            # Normal | N/A    | 0    | 0           | 0
            # Notes  | -1     | 1    | 1           | 1
            # Todo   | -1     | 1    | 2           | 2
            # Unused | -1     | 1    | 0           | 3

            chTypeEncoding = (
                (False, '0', '0'),
                (True, '1', '1'),
                (True, '1', '2'),
                (True, '1', '0'),
                )
            if prjChp.chType is None:
                prjChp.chType = 0
            yUnused, yType, yChapterType = chTypeEncoding[prjChp.chType]
            try:
                xmlChp.find('ChapterType').text = yChapterType
            except(AttributeError):
                ET.SubElement(xmlChp, 'ChapterType').text = yChapterType
            try:
                xmlChp.find('Type').text = yType
            except(AttributeError):
                ET.SubElement(xmlChp, 'Type').text = yType
            if yUnused:
                if xmlChp.find('Unused') is None:
                    ET.SubElement(xmlChp, 'Unused').text = '-1'
            elif xmlChp.find('Unused') is not None:
                xmlChp.remove(xmlChp.find('Unused'))

            #--- Write chapter fields.
            chFields = xmlChp.find('Fields')
            if prjChp.suppressChapterTitle:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_SuppressChapterTitle').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_SuppressChapterTitle').text = '1'
            elif chFields is not None:
                if chFields.find('Field_SuppressChapterTitle') is not None:
                    chFields.find('Field_SuppressChapterTitle').text = '0'

            if prjChp.suppressChapterBreak:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_SuppressChapterBreak').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_SuppressChapterBreak').text = '1'
            elif chFields is not None:
                if chFields.find('Field_SuppressChapterBreak') is not None:
                    chFields.find('Field_SuppressChapterBreak').text = '0'

            if prjChp.isTrash:
                if chFields is None:
                    chFields = ET.SubElement(xmlChp, 'Fields')
                try:
                    chFields.find('Field_IsTrash').text = '1'
                except(AttributeError):
                    ET.SubElement(chFields, 'Field_IsTrash').text = '1'
            elif chFields is not None:
                if chFields.find('Field_IsTrash') is not None:
                    chFields.remove(chFields.find('Field_IsTrash'))

            #--- Write chapter custom fields.
            for field in self._CHP_KWVAR:
                if prjChp.kwVar.get(field, None):
                    if chFields is None:
                        chFields = ET.SubElement(xmlChp, 'Fields')
                    try:
                        chFields.find(field).text = prjChp.kwVar[field]
                    except(AttributeError):
                        ET.SubElement(chFields, field).text = prjChp.kwVar[field]
                elif chFields is not None:
                    try:
                        chFields.remove(chFields.find(field))
                    except:
                        pass

            #--- Rebuild the chapter's scene list.
            try:
                xScnList = xmlChp.find('Scenes')
                xmlChp.remove(xScnList)
            except:
                pass
            if prjChp.srtScenes:
                sortSc = ET.SubElement(xmlChp, 'Scenes')
                for scId in prjChp.srtScenes:
                    ET.SubElement(sortSc, 'ScID').text = scId

        def build_location_subtree(xmlLoc, prjLoc, sortOrder):
            if prjLoc.title is not None:
                ET.SubElement(xmlLoc, 'Title').text = prjLoc.title

            if prjLoc.image is not None:
                ET.SubElement(xmlLoc, 'ImageFile').text = prjLoc.image

            if prjLoc.desc is not None:
                ET.SubElement(xmlLoc, 'Desc').text = prjLoc.desc

            if prjLoc.aka is not None:
                ET.SubElement(xmlLoc, 'AKA').text = prjLoc.aka

            if prjLoc.tags is not None:
                ET.SubElement(xmlLoc, 'Tags').text = list_to_string(prjLoc.tags)

            ET.SubElement(xmlLoc, 'SortOrder').text = str(sortOrder)

            #--- Write location custom fields.
            lcFields = xmlLoc.find('Fields')
            for field in self._LOC_KWVAR:
                if self.locations[lcId].kwVar.get(field, None):
                    if lcFields is None:
                        lcFields = ET.SubElement(xmlLoc, 'Fields')
                    try:
                        lcFields.find(field).text = self.locations[lcId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(lcFields, field).text = self.locations[lcId].kwVar[field]
                elif lcFields is not None:
                    try:
                        lcFields.remove(lcFields.find(field))
                    except:
                        pass

        def build_prjNote_subtree(xmlPnt, prjPnt, sortOrder):
            if prjPnt.title is not None:
                ET.SubElement(xmlPnt, 'Title').text = prjPnt.title

            if prjPnt.desc is not None:
                ET.SubElement(xmlPnt, 'Desc').text = prjPnt.desc

            ET.SubElement(xmlPnt, 'SortOrder').text = str(sortOrder)

        def add_projectvariable(title, desc, tags):
            # Note:
            # prjVars, projectvars are caller's variables
            pvId = create_id(prjVars)
            prjVars.append(pvId)
            # side effect
            projectvar = ET.SubElement(projectvars, 'PROJECTVAR')
            ET.SubElement(projectvar, 'ID').text = pvId
            ET.SubElement(projectvar, 'Title').text = title
            ET.SubElement(projectvar, 'Desc').text = desc
            ET.SubElement(projectvar, 'Tags').text = tags

        def build_item_subtree(xmlItm, prjItm, sortOrder):
            if prjItm.title is not None:
                ET.SubElement(xmlItm, 'Title').text = prjItm.title

            if prjItm.image is not None:
                ET.SubElement(xmlItm, 'ImageFile').text = prjItm.image

            if prjItm.desc is not None:
                ET.SubElement(xmlItm, 'Desc').text = prjItm.desc

            if prjItm.aka is not None:
                ET.SubElement(xmlItm, 'AKA').text = prjItm.aka

            if prjItm.tags is not None:
                ET.SubElement(xmlItm, 'Tags').text = list_to_string(prjItm.tags)

            ET.SubElement(xmlItm, 'SortOrder').text = str(sortOrder)

            #--- Write item custom fields.
            itFields = xmlItm.find('Fields')
            for field in self._ITM_KWVAR:
                if self.items[itId].kwVar.get(field, None):
                    if itFields is None:
                        itFields = ET.SubElement(xmlItm, 'Fields')
                    try:
                        itFields.find(field).text = self.items[itId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(itFields, field).text = self.items[itId].kwVar[field]
                elif itFields is not None:
                    try:
                        itFields.remove(itFields.find(field))
                    except:
                        pass

        def build_character_subtree(xmlCrt, prjCrt, sortOrder):
            if prjCrt.title is not None:
                ET.SubElement(xmlCrt, 'Title').text = prjCrt.title

            if prjCrt.desc is not None:
                ET.SubElement(xmlCrt, 'Desc').text = prjCrt.desc

            if prjCrt.image is not None:
                ET.SubElement(xmlCrt, 'ImageFile').text = prjCrt.image

            ET.SubElement(xmlCrt, 'SortOrder').text = str(sortOrder)

            if prjCrt.notes is not None:
                ET.SubElement(xmlCrt, 'Notes').text = prjCrt.notes

            if prjCrt.aka is not None:
                ET.SubElement(xmlCrt, 'AKA').text = prjCrt.aka

            if prjCrt.tags is not None:
                ET.SubElement(xmlCrt, 'Tags').text = list_to_string(prjCrt.tags)

            if prjCrt.bio is not None:
                ET.SubElement(xmlCrt, 'Bio').text = prjCrt.bio

            if prjCrt.goals is not None:
                ET.SubElement(xmlCrt, 'Goals').text = prjCrt.goals

            if prjCrt.fullName is not None:
                ET.SubElement(xmlCrt, 'FullName').text = prjCrt.fullName

            if prjCrt.isMajor:
                ET.SubElement(xmlCrt, 'Major').text = '-1'

            #--- Write character custom fields.
            crFields = xmlCrt.find('Fields')
            for field in self._CRT_KWVAR:
                if self.characters[crId].kwVar.get(field, None):
                    if crFields is None:
                        crFields = ET.SubElement(xmlCrt, 'Fields')
                    try:
                        crFields.find(field).text = self.characters[crId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(crFields, field).text = self.characters[crId].kwVar[field]
                elif crFields is not None:
                    try:
                        crFields.remove(crFields.find(field))
                    except:
                        pass

        def build_project_subtree(xmlPrj):
            VER = '7'
            try:
                xmlPrj.find('Ver').text = VER
            except(AttributeError):
                ET.SubElement(xmlPrj, 'Ver').text = VER

            if self.title is not None:
                try:
                    xmlPrj.find('Title').text = self.title
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Title').text = self.title

            if self.desc is not None:
                try:
                    xmlPrj.find('Desc').text = self.desc
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Desc').text = self.desc

            if self.authorName is not None:
                try:
                    xmlPrj.find('AuthorName').text = self.authorName
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'AuthorName').text = self.authorName

            if self.authorBio is not None:
                try:
                    xmlPrj.find('Bio').text = self.authorBio
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'Bio').text = self.authorBio

            if self.fieldTitle1 is not None:
                try:
                    xmlPrj.find('FieldTitle1').text = self.fieldTitle1
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle1').text = self.fieldTitle1

            if self.fieldTitle2 is not None:
                try:
                    xmlPrj.find('FieldTitle2').text = self.fieldTitle2
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle2').text = self.fieldTitle2

            if self.fieldTitle3 is not None:
                try:
                    xmlPrj.find('FieldTitle3').text = self.fieldTitle3
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle3').text = self.fieldTitle3

            if self.fieldTitle4 is not None:
                try:
                    xmlPrj.find('FieldTitle4').text = self.fieldTitle4
                except(AttributeError):
                    ET.SubElement(xmlPrj, 'FieldTitle4').text = self.fieldTitle4

            if self.languageCode:
                self.kwVar['Field_LanguageCode'] = self.languageCode
            if self.countryCode:
                self.kwVar['Field_CountryCode'] = self.countryCode

            #--- Write project custom fields.

            # This is for projects written with v7.6 - v7.10:
            self.kwVar['Field_LanguageCode'] = None
            self.kwVar['Field_CountryCode'] = None

            prjFields = xmlPrj.find('Fields')
            for field in self._PRJ_KWVAR:
                setting = self.kwVar.get(field, None)
                if setting:
                    if prjFields is None:
                        prjFields = ET.SubElement(xmlPrj, 'Fields')
                    try:
                        prjFields.find(field).text = setting
                    except(AttributeError):
                        ET.SubElement(prjFields, field).text = setting
                else:
                    try:
                        prjFields.remove(prjFields.find(field))
                    except:
                        pass

        TAG = 'YWRITER7'
        xmlScenes = {}
        xmlChapters = {}
        try:
            # Try processing an existing tree.
            root = self.tree.getroot()
            xmlPrj = root.find('PROJECT')
            locations = root.find('LOCATIONS')
            items = root.find('ITEMS')
            characters = root.find('CHARACTERS')
            prjNotes = root.find('PROJECTNOTES')
            scenes = root.find('SCENES')
            chapters = root.find('CHAPTERS')
        except(AttributeError):
            # Build a new tree.
            root = ET.Element(TAG)
            xmlPrj = ET.SubElement(root, 'PROJECT')
            locations = ET.SubElement(root, 'LOCATIONS')
            items = ET.SubElement(root, 'ITEMS')
            characters = ET.SubElement(root, 'CHARACTERS')
            prjNotes = ET.SubElement(root, 'PROJECTNOTES')
            scenes = ET.SubElement(root, 'SCENES')
            chapters = ET.SubElement(root, 'CHAPTERS')

        #--- Process project attributes.

        build_project_subtree(xmlPrj)

        #--- Process locations.

        # Remove LOCATION entries in order to rewrite
        # the LOCATIONS section in a modified sort order.
        for xmlLoc in locations.findall('LOCATION'):
            locations.remove(xmlLoc)

        # Add the new XML location subtrees to the project tree.
        sortOrder = 0
        for lcId in self.srtLocations:
            sortOrder += 1
            xmlLoc = ET.SubElement(locations, 'LOCATION')
            ET.SubElement(xmlLoc, 'ID').text = lcId
            build_location_subtree(xmlLoc, self.locations[lcId], sortOrder)

        #--- Process items.

        # Remove ITEM entries in order to rewrite
        # the ITEMS section in a modified sort order.
        for xmlItm in items.findall('ITEM'):
            items.remove(xmlItm)

        # Add the new XML item subtrees to the project tree.
        sortOrder = 0
        for itId in self.srtItems:
            sortOrder += 1
            xmlItm = ET.SubElement(items, 'ITEM')
            ET.SubElement(xmlItm, 'ID').text = itId
            build_item_subtree(xmlItm, self.items[itId], sortOrder)

        #--- Process characters.

        # Remove CHARACTER entries in order to rewrite
        # the CHARACTERS section in a modified sort order.
        for xmlCrt in characters.findall('CHARACTER'):
            characters.remove(xmlCrt)

        # Add the new XML character subtrees to the project tree.
        sortOrder = 0
        for crId in self.srtCharacters:
            sortOrder += 1
            xmlCrt = ET.SubElement(characters, 'CHARACTER')
            ET.SubElement(xmlCrt, 'ID').text = crId
            build_character_subtree(xmlCrt, self.characters[crId], sortOrder)

        #--- Process project notes.

        # Remove PROJECTNOTE entries in order to rewrite
        # the PROJECTNOTES section in a modified sort order.
        if prjNotes is not None:
            for xmlPnt in prjNotes.findall('PROJECTNOTE'):
                prjNotes.remove(xmlPnt)
            if not self.srtPrjNotes:
                root.remove(prjNotes)
        elif self.srtPrjNotes:
            prjNotes = ET.SubElement(root, 'PROJECTNOTES')
        if self.srtPrjNotes:
            # Add the new XML prjNote subtrees to the project tree.
            sortOrder = 0
            for pnId in self.srtPrjNotes:
                sortOrder += 1
                xmlPnt = ET.SubElement(prjNotes, 'PROJECTNOTE')
                ET.SubElement(xmlPnt, 'ID').text = pnId
                build_prjNote_subtree(xmlPnt, self.projectNotes[pnId], sortOrder)

        #--- Process project variables.
        if self.languages or self.languageCode or self.countryCode:
            self.check_locale()
            projectvars = root.find('PROJECTVARS')
            if projectvars is None:
                projectvars = ET.SubElement(root, 'PROJECTVARS')
            prjVars = []
            # list of all project variable IDs
            languages = self.languages.copy()
            hasLanguageCode = False
            hasCountryCode = False
            for projectvar in projectvars.findall('PROJECTVAR'):
                prjVars.append(projectvar.find('ID').text)
                title = projectvar.find('Title').text

                # Collect language codes.
                if title.startswith('lang='):
                    try:
                        __, langCode = title.split('=')
                        languages.remove(langCode)
                    except:
                        pass

                # Get the document's locale.
                elif title == 'Language':
                    projectvar.find('Desc').text = self.languageCode
                    hasLanguageCode = True

                elif title == 'Country':
                    projectvar.find('Desc').text = self.countryCode
                    hasCountryCode = True

            # Define project variables for the missing locale.
            if not hasLanguageCode:
                add_projectvariable('Language',
                                    self.languageCode,
                                    '0')

            if not hasCountryCode:
                add_projectvariable('Country',
                                    self.countryCode,
                                    '0')

            # Define project variables for the missing language code tags.
            for langCode in languages:
                add_projectvariable(f'lang={langCode}',
                                    f'<HTM <SPAN LANG="{langCode}"> /HTM>',
                                    '0')
                add_projectvariable(f'/lang={langCode}',
                                    f'<HTM </SPAN> /HTM>',
                                    '0')
                # adding new IDs to the prjVars list

        #--- Process scenes.

        # Save the original XML scene subtrees
        # and remove them from the project tree.
        for xmlScn in scenes.findall('SCENE'):
            scId = xmlScn.find('ID').text
            xmlScenes[scId] = xmlScn
            scenes.remove(xmlScn)

        # Add the new XML scene subtrees to the project tree.
        for scId in self.scenes:
            if not scId in xmlScenes:
                xmlScenes[scId] = ET.Element('SCENE')
                ET.SubElement(xmlScenes[scId], 'ID').text = scId
            build_scene_subtree(xmlScenes[scId], self.scenes[scId])
            scenes.append(xmlScenes[scId])

        #--- Process chapters.

        # Save the original XML chapter subtree
        # and remove it from the project tree.
        for xmlChp in chapters.findall('CHAPTER'):
            chId = xmlChp.find('ID').text
            xmlChapters[chId] = xmlChp
            chapters.remove(xmlChp)

        # Add the new XML chapter subtrees to the project tree.
        sortOrder = 0
        for chId in self.srtChapters:
            sortOrder += 1
            if not chId in xmlChapters:
                xmlChapters[chId] = ET.Element('CHAPTER')
                ET.SubElement(xmlChapters[chId], 'ID').text = chId
            build_chapter_subtree(xmlChapters[chId], self.chapters[chId], sortOrder)
            chapters.append(xmlChapters[chId])

        # Modify the scene contents of an existing xml element tree.
        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            if self.scenes[scId].sceneContent is not None:
                scn.find('SceneContent').text = self.scenes[scId].sceneContent
                scn.find('WordCount').text = str(self.scenes[scId].wordCount)
                scn.find('LetterCount').text = str(self.scenes[scId].letterCount)
            try:
                scn.remove(scn.find('RTFFile'))
            except:
                pass

        indent(root)
        self.tree = ET.ElementTree(root)

    def _write_element_tree(self, ywProject):
        """Write back the xml element tree to a .yw7 xml file located at filePath.
        
        Return a message beginning with the ERROR constant in case of error.
        """
        if os.path.isfile(ywProject.filePath):
            os.replace(ywProject.filePath, f'{ywProject.filePath}.bak')
            backedUp = True
        else:
            backedUp = False
        try:
            ywProject.tree.write(ywProject.filePath, xml_declaration=False, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{ywProject.filePath}.bak', ywProject.filePath)
            return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(ywProject.filePath)}".'

        return 'yWriter XML tree written.'

    def _postprocess_xml_file(self, filePath):
        '''Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath -- str: path to xml file.
        
        Read the xml file, put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text (unescape). Overwrite the .yw7 xml file.
        Return a message beginning with the ERROR constant in case of error.
        
        Note: The path is given as an argument rather than using self.filePath. 
        So this routine can be used for yWriter-generated xml files other than .yw7 as well. 
        '''
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        newlines = ['<?xml version="1.0" encoding="utf-8"?>']
        for line in lines:
            for tag in self._CDATA_TAGS:
                line = re.sub(f'\<{tag}\>', f'<{tag}><![CDATA[', line)
                line = re.sub(f'\<\/{tag}\>', f']]></{tag}>', line)
            newlines.append(line)
        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        text = unescape(text)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            return f'{ERROR}{_("Cannot write file")}: "{os.path.normpath(filePath)}".'

        return f'{_("File written")}: "{os.path.normpath(filePath)}".'

    def _strip_spaces(self, lines):
        """Local helper method.

        Positional argument:
            lines -- list of strings

        Return lines with leading and trailing spaces removed.
        """
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return stripped

    def reset_custom_variables(self):
        """Set custom keyword variables to an empty string.
        
        Thus the write() method will remove the associated custom fields
        from the .yw7 XML file. 
        Return True, if a keyword variable has changed (i.e information is lost).
        """
        hasChanged = False
        for field in self._PRJ_KWVAR:
            if self.kwVar.get(field, None):
                self.kwVar[field] = ''
                hasChanged = True
        for chId in self.chapters:
            # Deliberatey not iterate srtChapters: make sure to get all chapters.
            for field in self._CHP_KWVAR:
                if self.chapters[chId].kwVar.get(field, None):
                    self.chapters[chId].kwVar[field] = ''
                    hasChanged = True
        for scId in self.scenes:
            for field in self._SCN_KWVAR:
                if self.scenes[scId].kwVar.get(field, None):
                    self.scenes[scId].kwVar[field] = ''
                    hasChanged = True
        return hasChanged

    def adjust_scene_types(self):
        """Make sure that scenes in non-"Normal" chapters inherit the chapter's type."""
        for chId in self.srtChapters:
            if self.chapters[chId].chType != 0:
                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].scType = self.chapters[chId].chType

