"""Provide a generic class for template-based file export.

All file representations with template-based write methods inherit from this class.

Copyright (c) 2023 Peter Triesberger
For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import re
from string import Template
from pywriter.pywriter_globals import *
from pywriter.model.character import Character
from pywriter.model.scene import Scene
from pywriter.file.file import File
from pywriter.file.filter import Filter


class FileExport(File):
    """Abstract yWriter project file exporter representation.
    
    Public methods:
        write() -- write instance variables to the export file.
    
    This class is generic and contains no conversion algorithm and no templates.
    """
    SUFFIX = ''
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _notesPartTemplate = ''
    _todoPartTemplate = ''
    _notesChapterTemplate = ''
    _todoChapterTemplate = ''
    _unusedChapterTemplate = ''
    _notExportedChapterTemplate = ''
    _sceneTemplate = ''
    _firstSceneTemplate = ''
    _appendedSceneTemplate = ''
    _notesSceneTemplate = ''
    _todoSceneTemplate = ''
    _unusedSceneTemplate = ''
    _notExportedSceneTemplate = ''
    _sceneDivider = ''
    _chapterEndTemplate = ''
    _unusedChapterEndTemplate = ''
    _notExportedChapterEndTemplate = ''
    _notesChapterEndTemplate = ''
    _todoChapterEndTemplate = ''
    _characterSectionHeading = ''
    _characterTemplate = ''
    _locationSectionHeading = ''
    _locationTemplate = ''
    _itemSectionHeading = ''
    _itemTemplate = ''
    _fileFooter = ''
    _projectNoteTemplate = ''

    _DIVIDER = ', '

    def __init__(self, filePath, **kwargs):
        """Initialize filter strategy class instances.
        
        Positional arguments:
            filePath: str -- path to the file represented by the File instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            

        Extends the superclass constructor.
        """
        super().__init__(filePath, **kwargs)
        self._sceneFilter = Filter()
        self._chapterFilter = Filter()
        self._characterFilter = Filter()
        self._locationFilter = Filter()
        self._itemFilter = Filter()

    def write(self):
        """Write instance variables to the export file.
        
        Create a template-based output file. 
        Return a message in case of success.
        Raise the "Error" exception in case of error. 
        """
        text = self._get_text()
        backedUp = False
        if os.path.isfile(self.filePath):
            try:
                os.replace(self.filePath, f'{self.filePath}.bak')
            except:
                raise Error(f'{_("Cannot overwrite file")}: "{norm_path(self.filePath)}".')
            else:
                backedUp = True
        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            raise Error(f'{_("Cannot write file")}: "{norm_path(self.filePath)}".')

    def _get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        projectTemplateMapping = dict(
            Title=self._convert_from_yw(self.novel.title, True),
            Desc=self._convert_from_yw(self.novel.desc),
            AuthorName=self._convert_from_yw(self.novel.authorName, True),
            AuthorBio=self._convert_from_yw(self.novel.authorBio, True),
            FieldTitle1=self._convert_from_yw(self.novel.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.novel.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.novel.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.novel.fieldTitle4, True),
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
        )
        return projectTemplateMapping

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick: bool -- if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if text is None:
            text = ''
        return(text)

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section.
        
        Positional arguments:
            chId: str -- chapter ID.
            chapterNumber: int -- chapter number.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if chapterNumber == 0:
            chapterNumber = ''

        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self._convert_from_yw(self.novel.chapters[chId].title, True),
            Desc=self._convert_from_yw(self.novel.chapters[chId].desc),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
        )
        return chapterMapping

    def _get_chapters(self):
        """Process the chapters and nested scenes.
        
        Iterate through the sorted chapter list and apply the templates, 
        substituting placeholders according to the chapter mapping dictionary.
        For each chapter call the processing of its included scenes.
        Skip chapters not accepted by the chapter filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        chapterNumber = 0
        sceneNumber = 0
        wordsTotal = 0
        lettersTotal = 0
        for chId in self.novel.srtChapters:
            dispNumber = 0
            if not self._chapterFilter.accept(self, chId):
                continue

            # The order counts; be aware that "Todo" and "Notes" chapters are
            # always unused.
            # Has the chapter only scenes not to be exported?
            sceneCount = 0
            notExportCount = 0
            doNotExport = False
            template = None
            for scId in self.novel.chapters[chId].srtScenes:
                sceneCount += 1
                if self.novel.scenes[scId].doNotExport:
                    notExportCount += 1
            if sceneCount > 0 and notExportCount == sceneCount:
                doNotExport = True
            if self.novel.chapters[chId].chType == 2:
                # Chapter is "Todo" type.
                if self.novel.chapters[chId].chLevel == 1:
                    # Chapter is "Todo Part" type.
                    if self._todoPartTemplate:
                        template = Template(self._todoPartTemplate)
                elif self._todoChapterTemplate:
                    template = Template(self._todoChapterTemplate)
            elif self.novel.chapters[chId].chType == 1:
                # Chapter is "Notes" type.
                if self.novel.chapters[chId].chLevel == 1:
                    # Chapter is "Notes Part" type.
                    if self._notesPartTemplate:
                        template = Template(self._notesPartTemplate)
                elif self._notesChapterTemplate:
                    template = Template(self._notesChapterTemplate)
            elif self.novel.chapters[chId].chType == 3:
                # Chapter is "unused" type.
                if self._unusedChapterTemplate:
                    template = Template(self._unusedChapterTemplate)
            elif doNotExport:
                if self._notExportedChapterTemplate:
                    template = Template(self._notExportedChapterTemplate)
            elif self.novel.chapters[chId].chLevel == 1 and self._partTemplate:
                template = Template(self._partTemplate)
            else:
                template = Template(self._chapterTemplate)
                chapterNumber += 1
                dispNumber = chapterNumber
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))

            #--- Process scenes.
            sceneLines, sceneNumber, wordsTotal, lettersTotal = self._get_scenes(
                chId, sceneNumber, wordsTotal, lettersTotal, doNotExport)
            lines.extend(sceneLines)

            #--- Process chapter ending.
            template = None
            if self.novel.chapters[chId].chType == 2:
                if self._todoChapterEndTemplate:
                    template = Template(self._todoChapterEndTemplate)
            elif self.novel.chapters[chId].chType == 1:
                if self._notesChapterEndTemplate:
                    template = Template(self._notesChapterEndTemplate)
            elif self.novel.chapters[chId].chType == 3:
                if self._unusedChapterEndTemplate:
                    template = Template(self._unusedChapterEndTemplate)
            elif doNotExport:
                if self._notExportedChapterEndTemplate:
                    template = Template(self._notExportedChapterEndTemplate)
            elif self._chapterEndTemplate:
                template = Template(self._chapterEndTemplate)
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))
        return lines

    def _get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section.
        
        Positional arguments:
            crId: str -- character ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.characters[crId].tags is not None:
            tags = list_to_string(self.novel.characters[crId].tags, divider=self._DIVIDER)
        else:
            tags = ''
        if self.novel.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER
        else:
            characterStatus = Character.MINOR_MARKER

        characterMapping = dict(
            ID=crId,
            Title=self._convert_from_yw(self.novel.characters[crId].title, True),
            Desc=self._convert_from_yw(self.novel.characters[crId].desc),
            Tags=self._convert_from_yw(tags),
            Image=self.novel.characters[crId].image,
            AKA=self._convert_from_yw(self.novel.characters[crId].aka, True),
            Notes=self._convert_from_yw(self.novel.characters[crId].notes),
            Bio=self._convert_from_yw(self.novel.characters[crId].bio),
            Goals=self._convert_from_yw(self.novel.characters[crId].goals),
            FullName=self._convert_from_yw(self.novel.characters[crId].fullName, True),
            Status=characterStatus,
            ProjectName=self._convert_from_yw(self.projectName),
            ProjectPath=self.projectPath,
        )
        return characterMapping

    def _get_characters(self):
        """Process the characters.
        
        Iterate through the sorted character list and apply the template, 
        substituting placeholders according to the character mapping dictionary.
        Skip characters not accepted by the character filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._characterSectionHeading:
            lines = [self._characterSectionHeading]
        else:
            lines = []
        template = Template(self._characterTemplate)
        for crId in self.novel.srtCharacters:
            if self._characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(self._get_characterMapping(crId)))
        return lines

    def _get_fileHeader(self):
        """Process the file header.
        
        Apply the file header template, substituting placeholders 
        according to the file header mapping dictionary.
        Return a list of strings.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._fileHeader)
        lines.append(template.safe_substitute(self._get_fileHeaderMapping()))
        return lines

    def _get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section.
        
        Positional arguments:
            itId: str -- item ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.items[itId].tags is not None:
            tags = list_to_string(self.novel.items[itId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self._convert_from_yw(self.novel.items[itId].title, True),
            Desc=self._convert_from_yw(self.novel.items[itId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.novel.items[itId].image,
            AKA=self._convert_from_yw(self.novel.items[itId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def _get_items(self):
        """Process the items. 
        
        Iterate through the sorted item list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._itemSectionHeading:
            lines = [self._itemSectionHeading]
        else:
            lines = []
        template = Template(self._itemTemplate)
        for itId in self.novel.srtItems:
            if self._itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(self._get_itemMapping(itId)))
        return lines

    def _get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section.
        
        Positional arguments:
            lcId: str -- location ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.novel.locations[lcId].tags is not None:
            tags = list_to_string(self.novel.locations[lcId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self._convert_from_yw(self.novel.locations[lcId].title, True),
            Desc=self._convert_from_yw(self.novel.locations[lcId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.novel.locations[lcId].image,
            AKA=self._convert_from_yw(self.novel.locations[lcId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return locationMapping

    def _get_locations(self):
        """Process the locations.
        
        Iterate through the sorted location list and apply the template, 
        substituting placeholders according to the location mapping dictionary.
        Skip locations not accepted by the location filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        if self._locationSectionHeading:
            lines = [self._locationSectionHeading]
        else:
            lines = []
        template = Template(self._locationTemplate)
        for lcId in self.novel.srtLocations:
            if self._locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(self._get_locationMapping(lcId)))
        return lines

    def _get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):
        """Return a mapping dictionary for a scene section.
        
        Positional arguments:
            scId: str -- scene ID.
            sceneNumber: int -- scene number to be displayed.
            wordsTotal: int -- accumulated wordcount.
            lettersTotal: int -- accumulated lettercount.
        
        This is a template method that can be extended or overridden by subclasses.
        """

        #--- Create a comma separated tag list.
        if sceneNumber == 0:
            sceneNumber = ''
        if self.novel.scenes[scId].tags is not None:
            tags = list_to_string(self.novel.scenes[scId].tags, divider=self._DIVIDER)
        else:
            tags = ''

        #--- Create a comma separated character list.
        try:
            # Note: Due to a bug, yWriter scenes might hold invalid
            # viepoint characters
            sChList = []
            for crId in self.novel.scenes[scId].characters:
                sChList.append(self.novel.characters[crId].title)
            sceneChars = list_to_string(sChList, divider=self._DIVIDER)
            viewpointChar = sChList[0]
        except:
            sceneChars = ''
            viewpointChar = ''

        #--- Create a comma separated location list.
        if self.novel.scenes[scId].locations is not None:
            sLcList = []
            for lcId in self.novel.scenes[scId].locations:
                sLcList.append(self.novel.locations[lcId].title)
            sceneLocs = list_to_string(sLcList, divider=self._DIVIDER)
        else:
            sceneLocs = ''

        #--- Create a comma separated item list.
        if self.novel.scenes[scId].items is not None:
            sItList = []
            for itId in self.novel.scenes[scId].items:
                sItList.append(self.novel.items[itId].title)
            sceneItems = list_to_string(sItList, divider=self._DIVIDER)
        else:
            sceneItems = ''

        #--- Create A/R marker string.
        if self.novel.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER
        else:
            reactionScene = Scene.ACTION_MARKER

        #--- Date or day.
        if self.novel.scenes[scId].date is not None and self.novel.scenes[scId].date != Scene.NULL_DATE:
            scDay = ''
            scDate = self.novel.scenes[scId].date
            cmbDate = self.novel.scenes[scId].date
        else:
            scDate = ''
            if self.novel.scenes[scId].day is not None:
                scDay = self.novel.scenes[scId].day
                cmbDate = f'Day {self.novel.scenes[scId].day}'
            else:
                scDay = ''
                cmbDate = ''

        #--- Time.
        if self.novel.scenes[scId].time is not None:
            scTime = self.novel.scenes[scId].time.rsplit(':', 1)[0]
            # remove seconds
        else:
            scTime = ''

        #--- Create a combined duration information.
        if self.novel.scenes[scId].lastsDays is not None and self.novel.scenes[scId].lastsDays != '0':
            lastsDays = self.novel.scenes[scId].lastsDays
            days = f'{self.novel.scenes[scId].lastsDays}d '
        else:
            lastsDays = ''
            days = ''
        if self.novel.scenes[scId].lastsHours is not None and self.novel.scenes[scId].lastsHours != '0':
            lastsHours = self.novel.scenes[scId].lastsHours
            hours = f'{self.novel.scenes[scId].lastsHours}h '
        else:
            lastsHours = ''
            hours = ''
        if self.novel.scenes[scId].lastsMinutes is not None and self.novel.scenes[scId].lastsMinutes != '0':
            lastsMinutes = self.novel.scenes[scId].lastsMinutes
            minutes = f'{self.novel.scenes[scId].lastsMinutes}min'
        else:
            lastsMinutes = ''
            minutes = ''
        duration = f'{days}{hours}{minutes}'

        sceneMapping = dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self._convert_from_yw(self.novel.scenes[scId].title, True),
            Desc=self._convert_from_yw(self.novel.scenes[scId].desc),
            WordCount=str(self.novel.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.novel.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.novel.scenes[scId].status],
            SceneContent=self._convert_from_yw(self.novel.scenes[scId].sceneContent),
            FieldTitle1=self._convert_from_yw(self.novel.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.novel.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.novel.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.novel.fieldTitle4, True),
            Field1=self.novel.scenes[scId].field1,
            Field2=self.novel.scenes[scId].field2,
            Field3=self.novel.scenes[scId].field3,
            Field4=self.novel.scenes[scId].field4,
            Date=scDate,
            Time=scTime,
            Day=scDay,
            ScDate=cmbDate,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            ReactionScene=reactionScene,
            Goal=self._convert_from_yw(self.novel.scenes[scId].goal),
            Conflict=self._convert_from_yw(self.novel.scenes[scId].conflict),
            Outcome=self._convert_from_yw(self.novel.scenes[scId].outcome),
            Tags=self._convert_from_yw(tags, True),
            Image=self.novel.scenes[scId].image,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self._convert_from_yw(self.novel.scenes[scId].notes),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
            Language=self.novel.languageCode,
            Country=self.novel.countryCode,
        )
        return sceneMapping

    def _get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        """Process the scenes.
        
        Positional arguments:
            chId: str -- chapter ID.
            sceneNumber: int -- number of previously processed scenes.
            wordsTotal: int -- accumulated wordcount of the previous scenes.
            lettersTotal: int -- accumulated lettercount of the previous scenes.
            doNotExport: bool -- scene belongs to a chapter that is not to be exported.
        
        Iterate through a sorted scene list and apply the templates, 
        substituting placeholders according to the scene mapping dictionary.
        Skip scenes not accepted by the scene filter.
        
        Return a tuple:
            lines: list of strings -- the lines of the processed scene.
            sceneNumber: int -- number of all processed scenes.
            wordsTotal: int -- accumulated wordcount of all processed scenes.
            lettersTotal: int -- accumulated lettercount of all processed scenes.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        firstSceneInChapter = True
        for scId in self.novel.chapters[chId].srtScenes:
            dispNumber = 0
            if not self._sceneFilter.accept(self, scId):
                continue

            sceneContent = self.novel.scenes[scId].sceneContent
            if sceneContent is None:
                sceneContent = ''

            # The order counts; be aware that "Todo" and "Notes" scenes are
            # always unused.
            if self.novel.scenes[scId].scType == 2:
                if self._todoSceneTemplate:
                    template = Template(self._todoSceneTemplate)
                else:
                    continue

            elif self.novel.scenes[scId].scType == 1:
                # Scene is "Notes" type.
                if self._notesSceneTemplate:
                    template = Template(self._notesSceneTemplate)
                else:
                    continue

            elif self.novel.scenes[scId].scType == 3 or self.novel.chapters[chId].chType == 3:
                if self._unusedSceneTemplate:
                    template = Template(self._unusedSceneTemplate)
                else:
                    continue

            elif self.novel.scenes[scId].doNotExport or doNotExport:
                if self._notExportedSceneTemplate:
                    template = Template(self._notExportedSceneTemplate)
                else:
                    continue

            elif sceneContent.startswith('<HTML>'):
                continue

            elif sceneContent.startswith('<TEX>'):
                continue

            else:
                sceneNumber += 1
                dispNumber = sceneNumber
                wordsTotal += self.novel.scenes[scId].wordCount
                lettersTotal += self.novel.scenes[scId].letterCount
                template = Template(self._sceneTemplate)
                if not firstSceneInChapter and self.novel.scenes[scId].appendToPrev and self._appendedSceneTemplate:
                    template = Template(self._appendedSceneTemplate)
            if not (firstSceneInChapter or self.novel.scenes[scId].appendToPrev):
                lines.append(self._sceneDivider)
            if firstSceneInChapter and self._firstSceneTemplate:
                template = Template(self._firstSceneTemplate)
            lines.append(template.safe_substitute(self._get_sceneMapping(
                        scId, dispNumber, wordsTotal, lettersTotal)))
            firstSceneInChapter = False
        return lines, sceneNumber, wordsTotal, lettersTotal

    def _get_prjNoteMapping(self, pnId):
        """Return a mapping dictionary for a project note.
        
        Positional arguments:
            pnId: str -- project note ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        itemMapping = dict(
            ID=pnId,
            Title=self._convert_from_yw(self.novel.projectNotes[pnId].title, True),
            Desc=self._convert_from_yw(self.novel.projectNotes[pnId].desc, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

    def _get_projectNotes(self):
        """Process the project notes. 
        
        Iterate through the sorted project note list and apply the template, 
        substituting placeholders according to the item mapping dictionary.
        Skip items not accepted by the item filter.
        Return a list of strings.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        template = Template(self._projectNoteTemplate)
        for pnId in self.novel.srtPrjNotes:
            map = self._get_prjNoteMapping(pnId)
            lines.append(template.safe_substitute(map))
        return lines

    def _get_text(self):
        """Call all processing methods.
        
        Return a string to be written to the output file.
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = self._get_fileHeader()
        lines.extend(self._get_chapters())
        lines.extend(self._get_characters())
        lines.extend(self._get_locations())
        lines.extend(self._get_items())
        lines.extend(self._get_projectNotes())
        lines.append(self._fileFooter)
        return ''.join(lines)

    def _remove_inline_code(self, text):
        """Remove inline raw code from text and return the result."""
        if text:
            text = text.replace('<RTFBRK>', '')
            YW_SPECIAL_CODES = ('HTM', 'TEX', 'RTF', 'epub', 'mobi', 'rtfimg')
            for specialCode in YW_SPECIAL_CODES:
                text = re.sub(f'\<{specialCode} .+?\/{specialCode}\>', '', text)
        else:
            text = ''
        return text
