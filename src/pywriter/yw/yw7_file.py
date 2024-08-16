"""Provide a class for yWriter 7 project import and export.

yWriter version-specific file representations inherit from this class.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re
from html import unescape
from datetime import datetime
import xml.etree.ElementTree as ET
from pywriter.pywriter_globals import *
from pywriter.model.chapter import Chapter
from pywriter.model.scene import Scene
from pywriter.model.character import Character
from pywriter.model.world_element import WorldElement
from pywriter.model.basic_element import BasicElement
from pywriter.file.file import File
from pywriter.model.id_generator import create_id
from pywriter.yw.xml_indent import indent


class Yw7File(File):
    """yWriter 7 project file representation.

    Public methods:
        adjust_scene_types() -- Make sure that scenes in non-"Normal" chapters inherit the chapter's type.
        is_locked() -- check whether the yw7 file is locked by yWriter.
        read() -- parse the yWriter xml file and get the instance variables.
        write() -- write instance variables to the yWriter xml file.

    Public instance variables:
        tree -- xml element tree of the yWriter project
        
    Public class constants:
        PRJ_KWVAR -- List of the names of the project keyword variables.
        SCN_KWVAR -- List of the names of the scene keyword variables.
    """
    DESCRIPTION = _('yWriter 7 project')
    EXTENSION = '.yw7'
    _CDATA_TAGS = [
        'Title',
        'AuthorName',
        'Bio',
        'Desc',
        'FieldTitle1',
        'FieldTitle2',
        'FieldTitle3',
        'FieldTitle4',
        'LaTeXHeaderFile',
        'Tags',
        'AKA',
        'ImageFile',
        'FullName',
        'Goals',
        'Notes',
        'RTFFile',
        'SceneContent',
        'Outcome',
        'Goal',
        'Conflict'
        'Field_ChapterHeadingPrefix',
        'Field_ChapterHeadingSuffix',
        'Field_PartHeadingPrefix',
        'Field_PartHeadingSuffix',
        'Field_CustomGoal',
        'Field_CustomConflict',
        'Field_CustomOutcome',
        'Field_CustomChrBio',
        'Field_CustomChrGoals',
        'Field_ArcDefinition',
        'Field_SceneArcs',
        'Field_CustomAR',
        ]
    # Names of xml elements containing CDATA.
    # ElementTree.write omits CDATA tags, so they have to be inserted afterwards.

    PRJ_KWVAR = [
        'Field_LanguageCode',
        'Field_CountryCode',
        ]
    SCN_KWVAR = [
        'Field_SceneArcs',
        'Field_SceneMode',
        ]
    CRT_KWVAR = [
        'Field_Link',
        'Field_BirthDate',
        'Field_DeathDate',
        ]
    LOC_KWVAR = [
        'Field_Link',
        ]
    ITM_KWVAR = [
        'Field_Link',
        ]

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.
        
        Positional arguments:
            filePath: str -- path to the yw7 file.
            
        Optional arguments:
            kwargs -- keyword arguments (not used here).            
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        self.tree = None

    def adjust_scene_types(self):
        """Make sure that scenes in non-"Normal" chapters inherit the chapter's type."""
        for chId in self.novel.srtChapters:
            if self.novel.chapters[chId].chType != 0:
                for scId in self.novel.chapters[chId].srtScenes:
                    self.novel.scenes[scId].scType = self.novel.chapters[chId].chType

    def is_locked(self):
        """Check whether the yw7 file is locked by yWriter.
        
        Return True if a .lock file placed by yWriter exists.
        Otherwise, return False. 
        """
        return os.path.isfile(f'{self.filePath}.lock')

    def read(self):
        """Parse the yWriter xml file and get the instance variables.
        
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """

        for field in self.PRJ_KWVAR:
            self.novel.kwVar[field] = None

        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')
        try:
            try:
                self.tree = ET.parse(self.filePath)
                root = self.tree.getroot()
            except:
                # yw7 file may be UTF-16 encoded, with a wrong XML header (yWriter for iOS)
                with open(self.filePath, 'r', encoding='utf-16') as f:
                    xmlText = f.read()
                root = ET.fromstring(xmlText)
                xmlText = None
                # saving memory
                self.tree = ET.ElementTree(root)
        except:
            try:
                self.tree = ET.parse(self.filePath)
            except Exception as ex:
                raise Error(f'{_("Can not process file")} - {str(ex)}')

        self._read_project(root)
        self._read_locations(root)
        self._read_items(root)
        self._read_characters(root)
        self._read_projectvars(root)
        self._read_projectnotes(root)
        self._read_scenes(root)
        self._read_chapters(root)
        self.adjust_scene_types()

        #--- Set custom instance variables.
        for scId in self.novel.scenes:
            self.novel.scenes[scId].scnArcs = self.novel.scenes[scId].kwVar.get('Field_SceneArcs', None)
            scnMode = self.novel.scenes[scId].kwVar.get('Field_SceneMode', None)
            try:
                self.novel.scenes[scId].scnMode = int(scnMode)
            except:
                self.novel.scenes[scId].scnMode = None

    def write(self):
        """Write instance variables to the yWriter xml file.
        
        Open the yWriter xml file located at filePath and replace the instance variables 
        not being None. Create new XML elements if necessary.
        Raise the "Error" exception in case of error. 
        Overrides the superclass method.
        """
        if self.is_locked():
            raise Error(f'{_("yWriter seems to be open. Please close first")}.')

        if self.novel.languages is None:
            self.novel.get_languages()

        #--- Get custom instance variables.
        for scId in self.novel.scenes:
            if self.novel.scenes[scId].scnArcs is not None:
                self.novel.scenes[scId].kwVar['Field_SceneArcs'] = self.novel.scenes[scId].scnArcs
            if self.novel.scenes[scId].scnMode is not None:
                if self.novel.scenes[scId].scnMode == 0:
                    self.novel.scenes[scId].kwVar['Field_SceneMode'] = None
                else:
                    self.novel.scenes[scId].kwVar['Field_SceneMode'] = str(self.novel.scenes[scId].scnMode)
            self.novel.scenes[scId].kwVar['Field_SceneStyle'] = None
        self._build_element_tree()
        self._write_element_tree(self)
        self._postprocess_xml_file(self.filePath)

    def _build_element_tree(self):
        """Modify the yWriter project attributes of an existing xml element tree."""

        def set_element(parent, tag, text, index):
            subelement = parent.find(tag)
            if subelement is None:
                if text is not None:
                    subelement = ET.Element(tag)
                    parent.insert(index, subelement)
                    subelement.text = text
                    index += 1
            elif text is not None:
                subelement.text = text
                index += 1
            return index

        def build_scene_subtree(xmlScene, prjScn):

            def remove_date_time():
                """Delete all scene start data."""
                if xmlScene.find('SpecificDateTime') is not None:
                    xmlScene.remove(xmlScene.find('SpecificDateTime'))

                if xmlScene.find('SpecificDateMode') is not None:
                    xmlScene.remove(xmlScene.find('SpecificDateMode'))

                if xmlScene.find('Day') is not None:
                    xmlScene.remove(xmlScene.find('Day'))

                if xmlScene.find('Hour') is not None:
                    xmlScene.remove(xmlScene.find('Hour'))

                if xmlScene.find('Minute') is not None:
                    xmlScene.remove(xmlScene.find('Minute'))

            i = 1
            i = set_element(xmlScene, 'Title', prjScn.title, i)

            if prjScn.desc is not None:
                try:
                    xmlScene.find('Desc').text = prjScn.desc
                except(AttributeError):
                    if prjScn.desc:
                        ET.SubElement(xmlScene, 'Desc').text = prjScn.desc

            if xmlScene.find('SceneContent') is None:
                ET.SubElement(xmlScene, 'SceneContent').text = prjScn.sceneContent

            if xmlScene.find('WordCount') is None:
                ET.SubElement(xmlScene, 'WordCount').text = str(prjScn.wordCount)

            if xmlScene.find('LetterCount') is None:
                ET.SubElement(xmlScene, 'LetterCount').text = str(prjScn.letterCount)

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
                if xmlScene.find('Unused') is None:
                    ET.SubElement(xmlScene, 'Unused').text = '-1'
            elif xmlScene.find('Unused') is not None:
                xmlScene.remove(xmlScene.find('Unused'))

            # <Fields><Field_SceneType> (remove, if scene is "Normal")
            xmlSceneFields = xmlScene.find('Fields')
            if xmlSceneFields is not None:
                fieldScType = xmlSceneFields.find('Field_SceneType')
                if ySceneType is None:
                    if fieldScType is not None:
                        xmlSceneFields.remove(fieldScType)
                else:
                    try:
                        fieldScType.text = ySceneType
                    except(AttributeError):
                        ET.SubElement(xmlSceneFields, 'Field_SceneType').text = ySceneType
            elif ySceneType is not None:
                xmlSceneFields = ET.SubElement(xmlScene, 'Fields')
                ET.SubElement(xmlSceneFields, 'Field_SceneType').text = ySceneType

            #--- Export when RTF.
            if prjScn.doNotExport is not None:
                xmlExportCondSpecific = xmlScene.find('ExportCondSpecific')
                xmlExportWhenRtf = xmlScene.find('ExportWhenRTF')
                if prjScn.doNotExport:
                    if xmlExportCondSpecific is None:
                        xmlExportCondSpecific = ET.SubElement(xmlScene, 'ExportCondSpecific')
                    if xmlExportWhenRtf is not None:
                        xmlScene.remove(xmlExportWhenRtf)
                else:
                    if xmlExportCondSpecific is not None:
                        if xmlExportWhenRtf is None:
                            ET.SubElement(xmlScene, 'ExportWhenRTF').text = '-1'

            #--- Write scene custom fields.
            for field in self.SCN_KWVAR:
                if prjScn.kwVar.get(field, None):
                    if xmlSceneFields is None:
                        xmlSceneFields = ET.SubElement(xmlScene, 'Fields')
                    fieldEntry = self._convert_from_yw(prjScn.kwVar[field])
                    try:
                        xmlSceneFields.find(field).text = fieldEntry
                    except(AttributeError):
                        ET.SubElement(xmlSceneFields, field).text = fieldEntry
                elif xmlSceneFields is not None:
                    try:
                        xmlSceneFields.remove(xmlSceneFields.find(field))
                    except:
                        pass

            if prjScn.status is not None:
                try:
                    xmlScene.find('Status').text = str(prjScn.status)
                except:
                    ET.SubElement(xmlScene, 'Status').text = str(prjScn.status)

            if prjScn.notes is not None:
                try:
                    xmlScene.find('Notes').text = prjScn.notes
                except(AttributeError):
                    if prjScn.notes:
                        ET.SubElement(xmlScene, 'Notes').text = prjScn.notes

            if prjScn.tags is not None:
                try:
                    xmlScene.find('Tags').text = list_to_string(prjScn.tags)
                except(AttributeError):
                    if prjScn.tags:
                        ET.SubElement(xmlScene, 'Tags').text = list_to_string(prjScn.tags)

            if prjScn.field1 is not None:
                try:
                    xmlScene.find('Field1').text = prjScn.field1
                except(AttributeError):
                    if prjScn.field1:
                        ET.SubElement(xmlScene, 'Field1').text = prjScn.field1

            if prjScn.field2 is not None:
                try:
                    xmlScene.find('Field2').text = prjScn.field2
                except(AttributeError):
                    if prjScn.field2:
                        ET.SubElement(xmlScene, 'Field2').text = prjScn.field2

            if prjScn.field3 is not None:
                try:
                    xmlScene.find('Field3').text = prjScn.field3
                except(AttributeError):
                    if prjScn.field3:
                        ET.SubElement(xmlScene, 'Field3').text = prjScn.field3

            if prjScn.field4 is not None:
                try:
                    xmlScene.find('Field4').text = prjScn.field4
                except(AttributeError):
                    if prjScn.field4:
                        ET.SubElement(xmlScene, 'Field4').text = prjScn.field4

            if prjScn.appendToPrev:
                if xmlScene.find('AppendToPrev') is None:
                    ET.SubElement(xmlScene, 'AppendToPrev').text = '-1'
            elif xmlScene.find('AppendToPrev') is not None:
                xmlScene.remove(xmlScene.find('AppendToPrev'))

            #--- Write scene start.
            if (prjScn.date is not None) and (prjScn.time is not None):
                separator = ' '
                dateTime = f'{prjScn.date}{separator}{prjScn.time}'

                # Remove scene start data from XML, if date and time are empty strings.
                if dateTime == separator:
                    remove_date_time()

                elif xmlScene.find('SpecificDateTime') is not None:
                    if dateTime.count(':') < 2:
                        dateTime = f'{dateTime}:00'
                    xmlScene.find('SpecificDateTime').text = dateTime
                else:
                    ET.SubElement(xmlScene, 'SpecificDateTime').text = dateTime
                    ET.SubElement(xmlScene, 'SpecificDateMode').text = '-1'

                    if xmlScene.find('Day') is not None:
                        xmlScene.remove(xmlScene.find('Day'))

                    if xmlScene.find('Hour') is not None:
                        xmlScene.remove(xmlScene.find('Hour'))

                    if xmlScene.find('Minute') is not None:
                        xmlScene.remove(xmlScene.find('Minute'))

            elif (prjScn.day is not None) or (prjScn.time is not None):

                # Remove scene start data from XML, if day and time are empty strings.
                if not prjScn.day and not prjScn.time:
                    remove_date_time()

                else:
                    if xmlScene.find('SpecificDateTime') is not None:
                        xmlScene.remove(xmlScene.find('SpecificDateTime'))

                    if xmlScene.find('SpecificDateMode') is not None:
                        xmlScene.remove(xmlScene.find('SpecificDateMode'))
                    if prjScn.day is not None:
                        try:
                            xmlScene.find('Day').text = prjScn.day
                        except(AttributeError):
                            ET.SubElement(xmlScene, 'Day').text = prjScn.day
                    if prjScn.time is not None:
                        hours, minutes, __ = prjScn.time.split(':')
                        try:
                            xmlScene.find('Hour').text = hours
                        except(AttributeError):
                            ET.SubElement(xmlScene, 'Hour').text = hours
                        try:
                            xmlScene.find('Minute').text = minutes
                        except(AttributeError):
                            ET.SubElement(xmlScene, 'Minute').text = minutes

            #--- Write scene duration.
            if prjScn.lastsDays is not None:
                try:
                    xmlScene.find('LastsDays').text = prjScn.lastsDays
                except(AttributeError):
                    if prjScn.lastsDays:
                        ET.SubElement(xmlScene, 'LastsDays').text = prjScn.lastsDays

            if prjScn.lastsHours is not None:
                try:
                    xmlScene.find('LastsHours').text = prjScn.lastsHours
                except(AttributeError):
                    if prjScn.lastsHours:
                        ET.SubElement(xmlScene, 'LastsHours').text = prjScn.lastsHours

            if prjScn.lastsMinutes is not None:
                try:
                    xmlScene.find('LastsMinutes').text = prjScn.lastsMinutes
                except(AttributeError):
                    if prjScn.lastsMinutes:
                        ET.SubElement(xmlScene, 'LastsMinutes').text = prjScn.lastsMinutes

            # Plot related information
            if prjScn.isReactionScene:
                if xmlScene.find('ReactionScene') is None:
                    ET.SubElement(xmlScene, 'ReactionScene').text = '-1'
            elif xmlScene.find('ReactionScene') is not None:
                xmlScene.remove(xmlScene.find('ReactionScene'))

            if prjScn.isSubPlot:
                if xmlScene.find('SubPlot') is None:
                    ET.SubElement(xmlScene, 'SubPlot').text = '-1'
            elif xmlScene.find('SubPlot') is not None:
                xmlScene.remove(xmlScene.find('SubPlot'))

            if prjScn.goal is not None:
                try:
                    xmlScene.find('Goal').text = prjScn.goal
                except(AttributeError):
                    if prjScn.goal:
                        ET.SubElement(xmlScene, 'Goal').text = prjScn.goal

            if prjScn.conflict is not None:
                try:
                    xmlScene.find('Conflict').text = prjScn.conflict
                except(AttributeError):
                    if prjScn.conflict:
                        ET.SubElement(xmlScene, 'Conflict').text = prjScn.conflict

            if prjScn.outcome is not None:
                try:
                    xmlScene.find('Outcome').text = prjScn.outcome
                except(AttributeError):
                    if prjScn.outcome:
                        ET.SubElement(xmlScene, 'Outcome').text = prjScn.outcome

            if prjScn.image is not None:
                try:
                    xmlScene.find('ImageFile').text = prjScn.image
                except(AttributeError):
                    if prjScn.image:
                        ET.SubElement(xmlScene, 'ImageFile').text = prjScn.image

            #--- Characters/Locations/Items
            try:
                xmlScene.remove(xmlScene.find('Characters'))
            except:
                pass
            if prjScn.characters:
                xmlCharacters = ET.SubElement(xmlScene, 'Characters')
                for crId in prjScn.characters:
                    ET.SubElement(xmlCharacters, 'CharID').text = crId

            try:
                xmlScene.remove(xmlScene.find('Locations'))
            except:
                pass
            if prjScn.locations:
                xmlLocations = ET.SubElement(xmlScene, 'Locations')
                for lcId in prjScn.locations:
                    ET.SubElement(xmlLocations, 'LocID').text = lcId

            try:
                xmlScene.remove(xmlScene.find('Items'))
            except:
                pass
            if prjScn.items:
                xmlItems = ET.SubElement(xmlScene, 'Items')
                for ItId in prjScn.items:
                    ET.SubElement(xmlItems, 'ItmID').text = ItId

        def build_chapter_subtree(xmlChapter, prjChp):
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

            i = 1
            i = set_element(xmlChapter, 'Title', prjChp.title, i)
            i = set_element(xmlChapter, 'Desc', prjChp.desc, i)

            if yUnused:
                if xmlChapter.find('Unused') is None:
                    elem = ET.Element('Unused')
                    elem.text = '-1'
                    xmlChapter.insert(i, elem)
            elif xmlChapter.find('Unused') is not None:
                xmlChapter.remove(xmlChapter.find('Unused'))
            if xmlChapter.find('Unused') is not None:
                i += 1
            try:
                xmlChapter.remove(xmlChapter.find('SortOrder'))
            except:
                pass

            #--- Write chapter fields.
            xmlChapterFields = xmlChapter.find('Fields')
            if prjChp.suppressChapterTitle:
                if xmlChapterFields is None:
                    xmlChapterFields = ET.Element('Fields')
                    xmlChapter.insert(i, xmlChapterFields)
                try:
                    xmlChapterFields.find('Field_SuppressChapterTitle').text = '1'
                except(AttributeError):
                    ET.SubElement(xmlChapterFields, 'Field_SuppressChapterTitle').text = '1'
            elif xmlChapterFields is not None:
                if xmlChapterFields.find('Field_SuppressChapterTitle') is not None:
                    xmlChapterFields.find('Field_SuppressChapterTitle').text = '0'

            if prjChp.suppressChapterBreak:
                if xmlChapterFields is None:
                    xmlChapterFields = ET.Element('Fields')
                    xmlChapter.insert(i, xmlChapterFields)
                try:
                    xmlChapterFields.find('Field_SuppressChapterBreak').text = '1'
                except(AttributeError):
                    ET.SubElement(xmlChapterFields, 'Field_SuppressChapterBreak').text = '1'
            elif xmlChapterFields is not None:
                if xmlChapterFields.find('Field_SuppressChapterBreak') is not None:
                    xmlChapterFields.find('Field_SuppressChapterBreak').text = '0'

            if prjChp.isTrash:
                if xmlChapterFields is None:
                    xmlChapterFields = ET.Element('Fields')
                    xmlChapter.insert(i, xmlChapterFields)
                try:
                    xmlChapterFields.find('Field_IsTrash').text = '1'
                except(AttributeError):
                    ET.SubElement(xmlChapterFields, 'Field_IsTrash').text = '1'

            elif xmlChapterFields is not None:
                if xmlChapterFields.find('Field_IsTrash') is not None:
                    xmlChapterFields.remove(xmlChapterFields.find('Field_IsTrash'))

            #--- Write chapter custom fields.
            for field in self.CHP_KWVAR:
                if prjChp.kwVar.get(field, None):
                    if xmlChapterFields is None:
                        xmlChapterFields = ET.Element('Fields')
                        xmlChapter.insert(i, xmlChapterFields)
                    fieldEntry = self._convert_from_yw(prjChp.kwVar[field])
                    try:
                        xmlChapterFields.find(field).text = fieldEntry
                    except(AttributeError):
                        ET.SubElement(xmlChapterFields, field).text = fieldEntry
                elif xmlChapterFields is not None:
                    try:
                        xmlChapterFields.remove(xmlChapterFields.find(field))
                    except:
                        pass
            if xmlChapter.find('Fields') is not None:
                i += 1

            if xmlChapter.find('SectionStart') is not None:
                if prjChp.chLevel == 0:
                    xmlChapter.remove(xmlChapter.find('SectionStart'))
            elif prjChp.chLevel == 1:
                elem = ET.Element('SectionStart')
                elem.text = '-1'
                xmlChapter.insert(i, elem)
            if xmlChapter.find('SectionStart') is not None:
                i += 1

            i = set_element(xmlChapter, 'Type', yType, i)
            i = set_element(xmlChapter, 'ChapterType', yChapterType, i)

            #--- Rebuild the chapter's scene list.
            xmlScnList = xmlChapter.find('Scenes')
            if xmlScnList is not None:
                xmlChapter.remove(xmlScnList)

            # Rebuild the Scenes section in a modified sort order.
            if prjChp.srtScenes:
                xmlScnList = ET.SubElement(xmlChapter, 'Scenes')
                for scId in prjChp.srtScenes:
                    ET.SubElement(xmlScnList, 'ScID').text = scId

        def build_location_subtree(xmlLoc, prjLoc):
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

            #--- Write location custom fields.
            xmlLocationFields = xmlLoc.find('Fields')
            for field in self.LOC_KWVAR:
                if prjLoc.kwVar.get(field, None):
                    if xmlLocationFields is None:
                        xmlLocationFields = ET.SubElement(xmlLoc, 'Fields')
                    fieldEntry = self._convert_from_yw(prjLoc.kwVar[field])
                    try:
                        xmlLocationFields.find(field).text = fieldEntry
                    except(AttributeError):
                        ET.SubElement(xmlLocationFields, field).text = fieldEntry
                elif xmlLocationFields is not None:
                    try:
                        xmlLocationFields.remove(xmlLocationFields.find(field))
                    except:
                        pass
            try:
                xmlLoc.remove(xmlLoc.find('SortOrder'))
            except:
                pass

        def build_prjNote_subtree(xmlProjectnote, projectNote):
            if projectNote.title is not None:
                ET.SubElement(xmlProjectnote, 'Title').text = projectNote.title

            if projectNote.desc is not None:
                ET.SubElement(xmlProjectnote, 'Desc').text = projectNote.desc

        def add_projectvariable(title, desc, tags):
            # Note:
            # prjVars, xmlProjectvars are caller's variables
            pvId = create_id(prjVars)
            prjVars.append(pvId)
            # side effect
            xmlProjectvar = ET.SubElement(xmlProjectvars, 'PROJECTVAR')
            ET.SubElement(xmlProjectvar, 'ID').text = pvId
            ET.SubElement(xmlProjectvar, 'Title').text = title
            ET.SubElement(xmlProjectvar, 'Desc').text = desc
            ET.SubElement(xmlProjectvar, 'Tags').text = tags

        def build_item_subtree(xmlItm, prjItm):
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

            #--- Write item custom fields.
            xmlItemFields = xmlItm.find('Fields')
            for field in self.ITM_KWVAR:
                if prjItm.kwVar.get(field, None):
                    if xmlItemFields is None:
                        xmlItemFields = ET.SubElement(xmlItm, 'Fields')
                    fieldEntry = self._convert_from_yw(prjItm.kwVar[field])
                    try:
                        xmlItemFields.find(field).text = fieldEntry
                    except(AttributeError):
                        ET.SubElement(xmlItemFields, field).text = fieldEntry
                elif xmlItemFields is not None:
                    try:
                        xmlItemFields.remove(xmlItemFields.find(field))
                    except:
                        pass
            try:
                xmlItm.remove(xmlItm.find('SortOrder'))
            except:
                pass

        def build_character_subtree(xmlCrt, prjCrt):
            if prjCrt.title is not None:
                ET.SubElement(xmlCrt, 'Title').text = prjCrt.title

            if prjCrt.desc is not None:
                ET.SubElement(xmlCrt, 'Desc').text = prjCrt.desc

            if prjCrt.image is not None:
                ET.SubElement(xmlCrt, 'ImageFile').text = prjCrt.image

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
            xmlCharacterFields = xmlCrt.find('Fields')
            for field in self.CRT_KWVAR:
                if prjCrt.kwVar.get(field, None):
                    if xmlCharacterFields is None:
                        xmlCharacterFields = ET.SubElement(xmlCrt, 'Fields')
                    fieldEntry = self._convert_from_yw(prjCrt.kwVar[field])
                    try:
                        xmlCharacterFields.find(field).text = fieldEntry
                    except(AttributeError):
                        ET.SubElement(xmlCharacterFields, field).text = fieldEntry
                elif xmlCharacterFields is not None:
                    try:
                        xmlCharacterFields.remove(xmlCharacterFields.find(field))
                    except:
                        pass
            try:
                xmlCrt.remove(xmlCrt.find('SortOrder'))
            except:
                pass

        def build_project_subtree(xmlProject):
            VER = '7'
            try:
                xmlProject.find('Ver').text = VER
            except(AttributeError):
                ET.SubElement(xmlProject, 'Ver').text = VER

            if self.novel.title is not None:
                try:
                    xmlProject.find('Title').text = self.novel.title
                except(AttributeError):
                    ET.SubElement(xmlProject, 'Title').text = self.novel.title

            if self.novel.desc is not None:
                try:
                    xmlProject.find('Desc').text = self.novel.desc
                except(AttributeError):
                    ET.SubElement(xmlProject, 'Desc').text = self.novel.desc

            if self.novel.authorName is not None:
                try:
                    xmlProject.find('AuthorName').text = self.novel.authorName
                except(AttributeError):
                    ET.SubElement(xmlProject, 'AuthorName').text = self.novel.authorName

            if self.novel.authorBio is not None:
                try:
                    xmlProject.find('Bio').text = self.novel.authorBio
                except(AttributeError):
                    ET.SubElement(xmlProject, 'Bio').text = self.novel.authorBio

            if self.novel.fieldTitle1 is not None:
                try:
                    xmlProject.find('FieldTitle1').text = self.novel.fieldTitle1
                except(AttributeError):
                    ET.SubElement(xmlProject, 'FieldTitle1').text = self.novel.fieldTitle1

            if self.novel.fieldTitle2 is not None:
                try:
                    xmlProject.find('FieldTitle2').text = self.novel.fieldTitle2
                except(AttributeError):
                    ET.SubElement(xmlProject, 'FieldTitle2').text = self.novel.fieldTitle2

            if self.novel.fieldTitle3 is not None:
                try:
                    xmlProject.find('FieldTitle3').text = self.novel.fieldTitle3
                except(AttributeError):
                    ET.SubElement(xmlProject, 'FieldTitle3').text = self.novel.fieldTitle3

            if self.novel.fieldTitle4 is not None:
                try:
                    xmlProject.find('FieldTitle4').text = self.novel.fieldTitle4
                except(AttributeError):
                    ET.SubElement(xmlProject, 'FieldTitle4').text = self.novel.fieldTitle4

            #--- Write word target data.
            if self.novel.wordCountStart is not None:
                try:
                    xmlProject.find('WordCountStart').text = str(self.novel.wordCountStart)
                except(AttributeError):
                    ET.SubElement(xmlProject, 'WordCountStart').text = str(self.novel.wordCountStart)

            if self.novel.wordTarget is not None:
                try:
                    xmlProject.find('WordTarget').text = str(self.novel.wordTarget)
                except(AttributeError):
                    ET.SubElement(xmlProject, 'WordTarget').text = str(self.novel.wordTarget)

            #--- Write project custom fields.

            # This is for projects written with v7.6 - v7.10:
            self.novel.kwVar['Field_LanguageCode'] = None
            self.novel.kwVar['Field_CountryCode'] = None

            xmlProjectFields = xmlProject.find('Fields')
            for field in self.PRJ_KWVAR:
                setting = self.novel.kwVar.get(field, None)
                if setting:
                    if xmlProjectFields is None:
                        xmlProjectFields = ET.SubElement(xmlProject, 'Fields')
                    fieldEntry = self._convert_from_yw(setting)
                    try:
                        xmlProjectFields.find(field).text = fieldEntry
                    except(AttributeError):
                        ET.SubElement(xmlProjectFields, field).text = fieldEntry
                else:
                    try:
                        xmlProjectFields.remove(xmlProjectFields.find(field))
                    except:
                        pass
            try:
                xmlProject.remove(xmlProject.find('SavedWith'))
            except:
                pass
            try:
                xmlProject.remove(xmlProject.find('SavedOn'))
            except:
                pass

        TAG = 'YWRITER7'
        xmlNewScenes = {}
        xmlNewChapters = {}
        try:
            # Try processing an existing tree.
            root = self.tree.getroot()
            xmlProject = root.find('PROJECT')
            xmlLocations = root.find('LOCATIONS')
            xmlItems = root.find('ITEMS')
            xmlCharacters = root.find('CHARACTERS')
            xmlProjectnotes = root.find('PROJECTNOTES')
            xmlScenes = root.find('SCENES')
            xmlChapters = root.find('CHAPTERS')
        except(AttributeError):
            # Build a new tree.
            root = ET.Element(TAG)
            xmlProject = ET.SubElement(root, 'PROJECT')
            xmlLocations = ET.SubElement(root, 'LOCATIONS')
            xmlItems = ET.SubElement(root, 'ITEMS')
            xmlCharacters = ET.SubElement(root, 'CHARACTERS')
            xmlProjectnotes = ET.SubElement(root, 'PROJECTNOTES')
            xmlScenes = ET.SubElement(root, 'SCENES')
            xmlChapters = ET.SubElement(root, 'CHAPTERS')

        #--- Process project attributes.

        build_project_subtree(xmlProject)

        #--- Process Locations.

        # Remove LOCATION entries in order to rewrite
        # the LOCATIONS section in a modified sort order.
        for xmlLoc in xmlLocations.findall('LOCATION'):
            xmlLocations.remove(xmlLoc)

        # Add the new XML location subtrees to the project tree.
        for lcId in self.novel.srtLocations:
            xmlLoc = ET.SubElement(xmlLocations, 'LOCATION')
            ET.SubElement(xmlLoc, 'ID').text = lcId
            build_location_subtree(xmlLoc, self.novel.locations[lcId])

        #--- Process Items.

        # Remove ITEM entries in order to rewrite
        # the ITEMS section in a modified sort order.
        for xmlItm in xmlItems.findall('ITEM'):
            xmlItems.remove(xmlItm)

        # Add the new XML item subtrees to the project tree.
        for itId in self.novel.srtItems:
            xmlItm = ET.SubElement(xmlItems, 'ITEM')
            ET.SubElement(xmlItm, 'ID').text = itId
            build_item_subtree(xmlItm, self.novel.items[itId])

        #--- Process Characters.

        # Remove CHARACTER entries in order to rewrite
        # the CHARACTERS section in a modified sort order.
        for xmlCrt in xmlCharacters.findall('CHARACTER'):
            xmlCharacters.remove(xmlCrt)

        # Add the new XML character subtrees to the project tree.
        for crId in self.novel.srtCharacters:
            xmlCrt = ET.SubElement(xmlCharacters, 'CHARACTER')
            ET.SubElement(xmlCrt, 'ID').text = crId
            build_character_subtree(xmlCrt, self.novel.characters[crId])

        #--- Process project notes.

        # Remove PROJECTNOTE entries in order to rewrite
        # the PROJECTNOTES section in a modified sort order.
        if xmlProjectnotes is not None:
            for xmlProjectnote in xmlProjectnotes.findall('PROJECTNOTE'):
                xmlProjectnotes.remove(xmlProjectnote)
            if not self.novel.srtPrjNotes:
                root.remove(xmlProjectnotes)
        elif self.novel.srtPrjNotes:
            xmlProjectnotes = ET.SubElement(root, 'PROJECTNOTES')
        if self.novel.srtPrjNotes:
            # Add the new XML prjNote subtrees to the project tree.
            for pnId in self.novel.srtPrjNotes:
                xmlProjectnote = ET.SubElement(xmlProjectnotes, 'PROJECTNOTE')
                ET.SubElement(xmlProjectnote, 'ID').text = pnId
                build_prjNote_subtree(xmlProjectnote, self.novel.projectNotes[pnId])

        #--- Process project variables.
        xmlProjectvars = root.find('PROJECTVARS')
        if self.novel.languages or self.novel.languageCode or self.novel.countryCode:
            self.novel.check_locale()
            if xmlProjectvars is None:
                xmlProjectvars = ET.SubElement(root, 'PROJECTVARS')
            prjVars = []
            # list of all project variable IDs
            languages = self.novel.languages.copy()
            hasLanguageCode = False
            hasCountryCode = False
            for xmlProjectvar in xmlProjectvars.findall('PROJECTVAR'):
                prjVars.append(xmlProjectvar.find('ID').text)
                title = xmlProjectvar.find('Title').text

                # Collect language codes.
                if title.startswith('lang='):
                    try:
                        __, langCode = title.split('=')
                        languages.remove(langCode)
                    except:
                        pass

                # Get the document's locale.
                elif title == 'Language':
                    xmlProjectvar.find('Desc').text = self.novel.languageCode
                    hasLanguageCode = True

                elif title == 'Country':
                    xmlProjectvar.find('Desc').text = self.novel.countryCode
                    hasCountryCode = True

            # Define project variables for the missing locale.
            if not hasLanguageCode:
                add_projectvariable('Language',
                                    self.novel.languageCode,
                                    '0')

            if not hasCountryCode:
                add_projectvariable('Country',
                                    self.novel.countryCode,
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
        for xmlScene in xmlScenes.findall('SCENE'):
            scId = xmlScene.find('ID').text
            xmlNewScenes[scId] = xmlScene
            xmlScenes.remove(xmlScene)

        # Add the new XML scene subtrees to the project tree.
        for scId in self.novel.scenes:
            if not scId in xmlNewScenes:
                xmlNewScenes[scId] = ET.Element('SCENE')
                ET.SubElement(xmlNewScenes[scId], 'ID').text = scId
            build_scene_subtree(xmlNewScenes[scId], self.novel.scenes[scId])
            xmlScenes.append(xmlNewScenes[scId])

        #--- Process chapters.

        # Save the original XML chapter subtree
        # and remove it from the project tree.
        for xmlChapter in xmlChapters.findall('CHAPTER'):
            chId = xmlChapter.find('ID').text
            xmlNewChapters[chId] = xmlChapter
            xmlChapters.remove(xmlChapter)

        # Add the new XML chapter subtrees to the project tree.
        for chId in self.novel.srtChapters:
            if not chId in xmlNewChapters:
                xmlNewChapters[chId] = ET.Element('CHAPTER')
                ET.SubElement(xmlNewChapters[chId], 'ID').text = chId
            build_chapter_subtree(xmlNewChapters[chId], self.novel.chapters[chId])
            xmlChapters.append(xmlNewChapters[chId])

        # Modify the scene contents of an existing xml element tree.
        for xmlScene in root.find('SCENES'):
            scId = xmlScene.find('ID').text
            if self.novel.scenes[scId].sceneContent is not None:
                xmlScene.find('SceneContent').text = self.novel.scenes[scId].sceneContent
            try:
                xmlScene.remove(xmlScene.find('WordCount'))
            except:
                pass
            try:
                xmlScene.remove(xmlScene.find('LetterCount'))
            except:
                pass
            try:
                xmlScene.remove(xmlScene.find('RTFFile'))
            except:
                pass
            try:
                xmlScene.remove(xmlScene.find('BelongsToChID'))
            except:
                pass

        indent(root)
        self.tree = ET.ElementTree(root)

    def _convert_from_yw(self, text, quick=False):
        """Return text without markup, converted to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick: bool -- if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if text:
            # Apply XML predefined entities.
            XML_REPLACEMENTS = [
                ('&', '&amp;'),
                ('>', '&gt;'),
                ('<', '&lt;'),
                ("'", '&apos;'),
                ('"', '&quot;'),
                ]
            for yw, xm in XML_REPLACEMENTS:
                text = text.replace(yw, xm)
        else:
            text = ''
        return text

    def _postprocess_xml_file(self, filePath):
        """Postprocess an xml file created by ElementTree.
        
        Positional argument:
            filePath: str -- path to xml file.
        
        Read the xml file, put a header on top, insert the missing CDATA tags,
        and replace xml entities by plain text (unescape). Overwrite the .yw7 xml file.
        Raise the "Error" exception in case of error. 
        
        Note: The path is given as an argument rather than using self.filePath. 
        So this routine can be used for yWriter-generated xml files other than .yw7 as well. 
        """
        with open(filePath, 'r', encoding='utf-8') as f:
            text = f.read()
        lines = text.split('\n')
        newlines = ['<?xml version="1.0" encoding="utf-8"?>']
        for line in lines:
            for tag in self._CDATA_TAGS:
                line = re.sub(fr'\<{tag}\>', f'<{tag}><![CDATA[', line)
                line = re.sub(fr'\<\/{tag}\>', f']]></{tag}>', line)
            newlines.append(line)
        text = '\n'.join(newlines)
        text = text.replace('[CDATA[ \n', '[CDATA[')
        text = text.replace('\n]]', ']]')
        if not self.novel.chapters:
            text = text.replace('<CHAPTERS />', '<CHAPTERS></CHAPTERS>')
            # otherwise, yWriter fails to parse the file if there are no chapters.
        text = unescape(text)
        try:
            with open(filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            raise Error(f'{_("Cannot write file")}: "{norm_path(filePath)}".')

    def _read_project(self, root):
        """Read attributes at project level from the xml element tree."""
        xmlProject = root.find('PROJECT')

        if xmlProject.find('Title') is not None:
            self.novel.title = xmlProject.find('Title').text

        if xmlProject.find('AuthorName') is not None:
            self.novel.authorName = xmlProject.find('AuthorName').text

        if xmlProject.find('Bio') is not None:
            self.novel.authorBio = xmlProject.find('Bio').text

        if xmlProject.find('Desc') is not None:
            self.novel.desc = xmlProject.find('Desc').text

        if xmlProject.find('FieldTitle1') is not None:
            self.novel.fieldTitle1 = xmlProject.find('FieldTitle1').text

        if xmlProject.find('FieldTitle2') is not None:
            self.novel.fieldTitle2 = xmlProject.find('FieldTitle2').text

        if xmlProject.find('FieldTitle3') is not None:
            self.novel.fieldTitle3 = xmlProject.find('FieldTitle3').text

        if xmlProject.find('FieldTitle4') is not None:
            self.novel.fieldTitle4 = xmlProject.find('FieldTitle4').text

        #--- Read word target data.
        if xmlProject.find('WordCountStart') is not None:
            try:
                self.novel.wordCountStart = int(xmlProject.find('WordCountStart').text)
            except:
                self.novel.wordCountStart = 0
        if xmlProject.find('WordTarget') is not None:
            try:
                self.novel.wordTarget = int(xmlProject.find('WordTarget').text)
            except:
                self.novel.wordTarget = 0

        #--- Initialize custom keyword variables.
        for fieldName in self.PRJ_KWVAR:
            self.novel.kwVar[fieldName] = None

        #--- Read project custom fields.
        for xmlProjectFields in xmlProject.findall('Fields'):
            for fieldName in self.PRJ_KWVAR:
                field = xmlProjectFields.find(fieldName)
                if field is not None:
                    self.novel.kwVar[fieldName] = field.text

        # This is for projects written with v7.6 - v7.10:
        if self.novel.kwVar['Field_LanguageCode']:
            self.novel.languageCode = self.novel.kwVar['Field_LanguageCode']
        if self.novel.kwVar['Field_CountryCode']:
            self.novel.countryCode = self.novel.kwVar['Field_CountryCode']

    def _read_locations(self, root):
        """Read locations from the xml element tree."""
        self.novel.srtLocations = []
        # This is necessary for re-reading.
        for xmlLocation in root.find('LOCATIONS'):
            lcId = xmlLocation.find('ID').text
            self.novel.srtLocations.append(lcId)
            self.novel.locations[lcId] = WorldElement()

            if xmlLocation.find('Title') is not None:
                self.novel.locations[lcId].title = xmlLocation.find('Title').text

            if xmlLocation.find('ImageFile') is not None:
                self.novel.locations[lcId].image = xmlLocation.find('ImageFile').text

            if xmlLocation.find('Desc') is not None:
                self.novel.locations[lcId].desc = xmlLocation.find('Desc').text

            if xmlLocation.find('AKA') is not None:
                self.novel.locations[lcId].aka = xmlLocation.find('AKA').text

            if xmlLocation.find('Tags') is not None:
                if xmlLocation.find('Tags').text is not None:
                    tags = string_to_list(xmlLocation.find('Tags').text)
                    self.novel.locations[lcId].tags = self._strip_spaces(tags)

            #--- Initialize custom keyword variables.
            for fieldName in self.LOC_KWVAR:
                self.novel.locations[lcId].kwVar[fieldName] = None

            #--- Read location custom fields.
            for xmlLocationFields in xmlLocation.findall('Fields'):
                for fieldName in self.LOC_KWVAR:
                    field = xmlLocationFields.find(fieldName)
                    if field is not None:
                        self.novel.locations[lcId].kwVar[fieldName] = field.text

    def _read_items(self, root):
        """Read items from the xml element tree."""
        self.novel.srtItems = []
        # This is necessary for re-reading.
        for xmlItem in root.find('ITEMS'):
            itId = xmlItem.find('ID').text
            self.novel.srtItems.append(itId)
            self.novel.items[itId] = WorldElement()

            if xmlItem.find('Title') is not None:
                self.novel.items[itId].title = xmlItem.find('Title').text

            if xmlItem.find('ImageFile') is not None:
                self.novel.items[itId].image = xmlItem.find('ImageFile').text

            if xmlItem.find('Desc') is not None:
                self.novel.items[itId].desc = xmlItem.find('Desc').text

            if xmlItem.find('AKA') is not None:
                self.novel.items[itId].aka = xmlItem.find('AKA').text

            if xmlItem.find('Tags') is not None:
                if xmlItem.find('Tags').text is not None:
                    tags = string_to_list(xmlItem.find('Tags').text)
                    self.novel.items[itId].tags = self._strip_spaces(tags)

            #--- Initialize custom keyword variables.
            for fieldName in self.ITM_KWVAR:
                self.novel.items[itId].kwVar[fieldName] = None

            #--- Read item custom fields.
            for xmlItemFields in xmlItem.findall('Fields'):
                for fieldName in self.ITM_KWVAR:
                    field = xmlItemFields.find(fieldName)
                    if field is not None:
                        self.novel.items[itId].kwVar[fieldName] = field.text

    def _read_characters(self, root):
        """Read characters from the xml element tree."""
        self.novel.srtCharacters = []
        # This is necessary for re-reading.
        for xmlCharacter in root.find('CHARACTERS'):
            crId = xmlCharacter.find('ID').text
            self.novel.srtCharacters.append(crId)
            self.novel.characters[crId] = Character()

            if xmlCharacter.find('Title') is not None:
                self.novel.characters[crId].title = xmlCharacter.find('Title').text

            if xmlCharacter.find('ImageFile') is not None:
                self.novel.characters[crId].image = xmlCharacter.find('ImageFile').text

            if xmlCharacter.find('Desc') is not None:
                self.novel.characters[crId].desc = xmlCharacter.find('Desc').text

            if xmlCharacter.find('AKA') is not None:
                self.novel.characters[crId].aka = xmlCharacter.find('AKA').text

            if xmlCharacter.find('Tags') is not None:
                if xmlCharacter.find('Tags').text is not None:
                    tags = string_to_list(xmlCharacter.find('Tags').text)
                    self.novel.characters[crId].tags = self._strip_spaces(tags)

            if xmlCharacter.find('Notes') is not None:
                self.novel.characters[crId].notes = xmlCharacter.find('Notes').text

            if xmlCharacter.find('Bio') is not None:
                self.novel.characters[crId].bio = xmlCharacter.find('Bio').text

            if xmlCharacter.find('Goals') is not None:
                self.novel.characters[crId].goals = xmlCharacter.find('Goals').text

            if xmlCharacter.find('FullName') is not None:
                self.novel.characters[crId].fullName = xmlCharacter.find('FullName').text

            if xmlCharacter.find('Major') is not None:
                self.novel.characters[crId].isMajor = True
            else:
                self.novel.characters[crId].isMajor = False

            #--- Initialize custom keyword variables.
            for fieldName in self.CRT_KWVAR:
                self.novel.characters[crId].kwVar[fieldName] = None

            #--- Read character custom fields.
            for xmlCharacterFields in xmlCharacter.findall('Fields'):
                for fieldName in self.CRT_KWVAR:
                    field = xmlCharacterFields.find(fieldName)
                    if field is not None:
                        self.novel.characters[crId].kwVar[fieldName] = field.text

    def _read_projectnotes(self, root):
        """Read project notes from the xml element tree."""
        self.novel.srtPrjNotes = []
        # This is necessary for re-reading.

        try:
            for xmlProjectnote in root.find('PROJECTNOTES'):
                if xmlProjectnote.find('ID') is not None:
                    pnId = xmlProjectnote.find('ID').text
                    self.novel.srtPrjNotes.append(pnId)
                    self.novel.projectNotes[pnId] = BasicElement()
                    if xmlProjectnote.find('Title') is not None:
                        self.novel.projectNotes[pnId].title = xmlProjectnote.find('Title').text
                    if xmlProjectnote.find('Desc') is not None:
                        self.novel.projectNotes[pnId].desc = xmlProjectnote.find('Desc').text

                #--- Initialize project note custom fields.
                for fieldName in self.PNT_KWVAR:
                    self.novel.projectNotes[pnId].kwVar[fieldName] = None

                #--- Read project note custom fields.
                for pnFields in xmlProjectnote.findall('Fields'):
                    field = pnFields.find(fieldName)
                    if field is not None:
                        self.novel.projectNotes[pnId].kwVar[fieldName] = field.text
        except:
            pass

    def _read_projectvars(self, root):
        """Read relevant project variables from the xml element tree."""
        try:
            for xmlProjectvar in root.find('PROJECTVARS'):
                if xmlProjectvar.find('Title') is not None:
                    title = xmlProjectvar.find('Title').text
                    if title == 'Language':
                        if xmlProjectvar.find('Desc') is not None:
                            self.novel.languageCode = xmlProjectvar.find('Desc').text

                    elif title == 'Country':
                        if xmlProjectvar.find('Desc') is not None:
                            self.novel.countryCode = xmlProjectvar.find('Desc').text

                    elif title.startswith('lang='):
                        try:
                            __, langCode = title.split('=')
                            if self.novel.languages is None:
                                self.novel.languages = []
                            self.novel.languages.append(langCode)
                        except:
                            pass
        except:
            pass

    def _read_scenes(self, root):
        """ Read attributes at scene level from the xml element tree."""
        for xmlScene in root.find('SCENES'):
            scId = xmlScene.find('ID').text
            self.novel.scenes[scId] = Scene()

            if xmlScene.find('Title') is not None:
                self.novel.scenes[scId].title = xmlScene.find('Title').text

            if xmlScene.find('Desc') is not None:
                self.novel.scenes[scId].desc = xmlScene.find('Desc').text

            if xmlScene.find('SceneContent') is not None:
                sceneContent = xmlScene.find('SceneContent').text
                if sceneContent is not None:
                    self.novel.scenes[scId].sceneContent = sceneContent

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

            self.novel.scenes[scId].scType = 0

            #--- Initialize custom keyword variables.
            for fieldName in self.SCN_KWVAR:
                self.novel.scenes[scId].kwVar[fieldName] = None

            for xmlSceneFields in xmlScene.findall('Fields'):
                #--- Read scene custom fields.
                for fieldName in self.SCN_KWVAR:
                    field = xmlSceneFields.find(fieldName)
                    if field is not None:
                        self.novel.scenes[scId].kwVar[fieldName] = field.text

                # Read scene type, if any.
                if xmlSceneFields.find('Field_SceneType') is not None:
                    if xmlSceneFields.find('Field_SceneType').text == '1':
                        self.novel.scenes[scId].scType = 1
                    elif xmlSceneFields.find('Field_SceneType').text == '2':
                        self.novel.scenes[scId].scType = 2
            if xmlScene.find('Unused') is not None:
                if self.novel.scenes[scId].scType == 0:
                    self.novel.scenes[scId].scType = 3

            # Export when RTF.
            if xmlScene.find('ExportCondSpecific') is None:
                self.novel.scenes[scId].doNotExport = False
            elif xmlScene.find('ExportWhenRTF') is not None:
                self.novel.scenes[scId].doNotExport = False
            else:
                self.novel.scenes[scId].doNotExport = True

            if xmlScene.find('Status') is not None:
                self.novel.scenes[scId].status = int(xmlScene.find('Status').text)

            if xmlScene.find('Notes') is not None:
                self.novel.scenes[scId].notes = xmlScene.find('Notes').text

            if xmlScene.find('Tags') is not None:
                if xmlScene.find('Tags').text is not None:
                    tags = string_to_list(xmlScene.find('Tags').text)
                    self.novel.scenes[scId].tags = self._strip_spaces(tags)

            if xmlScene.find('Field1') is not None:
                self.novel.scenes[scId].field1 = xmlScene.find('Field1').text

            if xmlScene.find('Field2') is not None:
                self.novel.scenes[scId].field2 = xmlScene.find('Field2').text

            if xmlScene.find('Field3') is not None:
                self.novel.scenes[scId].field3 = xmlScene.find('Field3').text

            if xmlScene.find('Field4') is not None:
                self.novel.scenes[scId].field4 = xmlScene.find('Field4').text

            if xmlScene.find('AppendToPrev') is not None:
                self.novel.scenes[scId].appendToPrev = True
            else:
                self.novel.scenes[scId].appendToPrev = False

            #--- Scene start.
            if xmlScene.find('SpecificDateTime') is not None:
                dateTimeStr = xmlScene.find('SpecificDateTime').text

                # Check SpecificDateTime for ISO compliance.
                try:
                    dateTime = datetime.fromisoformat(dateTimeStr)
                except:
                    self.novel.scenes[scId].date = ''
                    self.novel.scenes[scId].time = ''
                else:
                    startDateTime = dateTime.isoformat().split('T')
                    self.novel.scenes[scId].date = startDateTime[0]
                    self.novel.scenes[scId].time = startDateTime[1]
            else:
                if xmlScene.find('Day') is not None:
                    day = xmlScene.find('Day').text

                    # Check if Day represents an integer.
                    try:
                        int(day)
                    except ValueError:
                        day = ''
                    self.novel.scenes[scId].day = day

                hasUnspecificTime = False
                if xmlScene.find('Hour') is not None:
                    hour = xmlScene.find('Hour').text.zfill(2)
                    hasUnspecificTime = True
                else:
                    hour = '00'
                if xmlScene.find('Minute') is not None:
                    minute = xmlScene.find('Minute').text.zfill(2)
                    hasUnspecificTime = True
                else:
                    minute = '00'
                if hasUnspecificTime:
                    self.novel.scenes[scId].time = f'{hour}:{minute}:00'

            #--- Scene duration.
            if xmlScene.find('LastsDays') is not None:
                self.novel.scenes[scId].lastsDays = xmlScene.find('LastsDays').text

            if xmlScene.find('LastsHours') is not None:
                self.novel.scenes[scId].lastsHours = xmlScene.find('LastsHours').text

            if xmlScene.find('LastsMinutes') is not None:
                self.novel.scenes[scId].lastsMinutes = xmlScene.find('LastsMinutes').text

            if xmlScene.find('ReactionScene') is not None:
                self.novel.scenes[scId].isReactionScene = True
            else:
                self.novel.scenes[scId].isReactionScene = False

            if xmlScene.find('SubPlot') is not None:
                self.novel.scenes[scId].isSubPlot = True
            else:
                self.novel.scenes[scId].isSubPlot = False

            if xmlScene.find('Goal') is not None:
                self.novel.scenes[scId].goal = xmlScene.find('Goal').text

            if xmlScene.find('Conflict') is not None:
                self.novel.scenes[scId].conflict = xmlScene.find('Conflict').text

            if xmlScene.find('Outcome') is not None:
                self.novel.scenes[scId].outcome = xmlScene.find('Outcome').text

            if xmlScene.find('ImageFile') is not None:
                self.novel.scenes[scId].image = xmlScene.find('ImageFile').text

            if xmlScene.find('Characters') is not None:
                for characters in xmlScene.find('Characters').iter('CharID'):
                    crId = characters.text
                    if crId in self.novel.srtCharacters:
                        if self.novel.scenes[scId].characters is None:
                            self.novel.scenes[scId].characters = []
                        self.novel.scenes[scId].characters.append(crId)

            if xmlScene.find('Locations') is not None:
                for locations in xmlScene.find('Locations').iter('LocID'):
                    lcId = locations.text
                    if lcId in self.novel.srtLocations:
                        if self.novel.scenes[scId].locations is None:
                            self.novel.scenes[scId].locations = []
                        self.novel.scenes[scId].locations.append(lcId)

            if xmlScene.find('Items') is not None:
                for items in xmlScene.find('Items').iter('ItemID'):
                    itId = items.text
                    if itId in self.novel.srtItems:
                        if self.novel.scenes[scId].items is None:
                            self.novel.scenes[scId].items = []
                        self.novel.scenes[scId].items.append(itId)

    def _read_chapters(self, root):
        """Read attributes at chapter level from the xml element tree."""
        self.novel.srtChapters = []
        # This is necessary for re-reading.
        for xmlChapter in root.find('CHAPTERS'):
            chId = xmlChapter.find('ID').text
            self.novel.chapters[chId] = Chapter()
            self.novel.srtChapters.append(chId)

            if xmlChapter.find('Title') is not None:
                self.novel.chapters[chId].title = xmlChapter.find('Title').text

            if xmlChapter.find('Desc') is not None:
                self.novel.chapters[chId].desc = xmlChapter.find('Desc').text

            if xmlChapter.find('SectionStart') is not None:
                self.novel.chapters[chId].chLevel = 1
            else:
                self.novel.chapters[chId].chLevel = 0

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

            self.novel.chapters[chId].chType = 0
            if xmlChapter.find('Unused') is not None:
                yUnused = True
            else:
                yUnused = False
            if xmlChapter.find('ChapterType') is not None:
                # The file may be created with yWriter version 7.0.7.2+
                yChapterType = xmlChapter.find('ChapterType').text
                if yChapterType == '2':
                    self.novel.chapters[chId].chType = 2
                elif yChapterType == '1':
                    self.novel.chapters[chId].chType = 1
                elif yUnused:
                    self.novel.chapters[chId].chType = 3
            else:
                # The file may be created with a yWriter version prior to 7.0.7.2
                if xmlChapter.find('Type') is not None:
                    yType = xmlChapter.find('Type').text
                    if yType == '1':
                        self.novel.chapters[chId].chType = 1
                    elif yUnused:
                        self.novel.chapters[chId].chType = 3

            self.novel.chapters[chId].suppressChapterTitle = False
            if self.novel.chapters[chId].title is not None:
                if self.novel.chapters[chId].title.startswith('@'):
                    self.novel.chapters[chId].suppressChapterTitle = True

            #--- Initialize custom keyword variables.
            for fieldName in self.CHP_KWVAR:
                self.novel.chapters[chId].kwVar[fieldName] = None

            #--- Read chapter fields.
            for xmlChapterFields in xmlChapter.findall('Fields'):
                if xmlChapterFields.find('Field_SuppressChapterTitle') is not None:
                    if xmlChapterFields.find('Field_SuppressChapterTitle').text == '1':
                        self.novel.chapters[chId].suppressChapterTitle = True
                self.novel.chapters[chId].isTrash = False
                if xmlChapterFields.find('Field_IsTrash') is not None:
                    if xmlChapterFields.find('Field_IsTrash').text == '1':
                        self.novel.chapters[chId].isTrash = True
                self.novel.chapters[chId].suppressChapterBreak = False
                if xmlChapterFields.find('Field_SuppressChapterBreak') is not None:
                    if xmlChapterFields.find('Field_SuppressChapterBreak').text == '1':
                        self.novel.chapters[chId].suppressChapterBreak = True

                #--- Read chapter custom fields.
                for fieldName in self.CHP_KWVAR:
                    field = xmlChapterFields.find(fieldName)
                    if field is not None:
                        self.novel.chapters[chId].kwVar[fieldName] = field.text

            #--- Read chapter's scene list.
            self.novel.chapters[chId].srtScenes = []
            if xmlChapter.find('Scenes') is not None:
                for scn in xmlChapter.find('Scenes').findall('ScID'):
                    scId = scn.text
                    if scId in self.novel.scenes:
                        self.novel.chapters[chId].srtScenes.append(scId)

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

    def _write_element_tree(self, ywProject):
        """Write back the xml element tree to a .yw7 xml file located at filePath.
        
        Raise the "Error" exception in case of error. 
        """
        backedUp = False
        if os.path.isfile(ywProject.filePath):
            try:
                os.replace(ywProject.filePath, f'{ywProject.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(ywProject.filePath)}".')
            else:
                backedUp = True
        try:
            ywProject.tree.write(ywProject.filePath, xml_declaration=False, encoding='utf-8')
        except:
            if backedUp:
                os.replace(f'{ywProject.filePath}.bak', ywProject.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(ywProject.filePath)}".')

