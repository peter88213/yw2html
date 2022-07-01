#!/usr/bin/env python3
"""Export yWriter project to html. 

Version @release
Requires Python 3.6+
Copyright (c) 2022 Peter Triesberger
For further information see https://github.com/peter88213/yw2html
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import os
import argparse
ERROR = '!'
import sys


class Ui:
    """Base class for UI facades, implementing a 'silent mode'.
    
    Public methods:
        ask_yes_no(text) -- return True or False.
        set_info_what(message) -- show what the converter is going to do.
        set_info_how(message) -- show how the converter is doing.
        start() -- launch the GUI, if any.
        
    Public instance variables:
        infoWhatText -- buffer for general messages.
        infoHowText -- buffer for error/success messages.
    """

    def __init__(self, title):
        """Initialize text buffers for messaging.
        
        Positional arguments:
            title -- application title.
        """
        self.infoWhatText = ''
        self.infoHowText = ''

    def ask_yes_no(self, text):
        """Return True or False.
        
        Positional arguments:
            text -- question to be asked. 
            
        This is a stub used for "silent mode".
        The application may use a subclass for confirmation requests.    
        """
        return True

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be buffered. 
        """
        self.infoWhatText = message

    def set_info_how(self, message):
        """Show how the converter is doing.
        
        Positional arguments:
            message -- message to be buffered.
            
        Print the message to stderr, replacing the error marker, if any.
        """
        if message.startswith(ERROR):
            message = f'FAIL: {message.split(ERROR, maxsplit=1)[1].strip()}'
            sys.stderr.write(message)
        self.infoHowText = message

    def start(self):
        """Launch the GUI, if any.
        
        To be overridden by subclasses requiring
        special action to launch the user interaction.
        """


class UiCmd(Ui):
    """Ui subclass implementing a console interface.
    
    Public methods:
        ask_yes_no(text) -- query yes or no at the console.
        set_info_what(message) -- show what the converter is going to do.
        set_info_how(message) -- show how the converter is doing.
    """

    def __init__(self, title):
        """Print the title.
        
        Positional arguments:
            title -- application title to be displayed at the console.
        
        Extends the superclass constructor.
        """
        super().__init__(title)
        print(title)

    def ask_yes_no(self, text):
        """Query yes or no at the console.
        
        Positional arguments:
            text -- question to be asked at the console. 
            
        Overrides the superclass method.       
        """
        result = input(f'WARNING: {text} (y/n)')
        if result.lower() == 'y':
            return True
        else:
            return False

    def set_info_what(self, message):
        """Show what the converter is going to do.
        
        Positional arguments:
            message -- message to be printed at the console. 
            
        Print the message.
        Overrides the superclass method.
        """
        print(message)

    def set_info_how(self, message):
        """Show how the converter is doing.

        Positional arguments:
            message -- message to be printed at the console. 
            
        Print the message, replacing the error marker, if any.
        Overrides the superclass method.
        """
        if message.startswith(ERROR):
            message = f'FAIL: {message.split(ERROR, maxsplit=1)[1].strip()}'
        self.infoHowText = message
        print(message)


def open_document(document):
    """Open a document with the operating system's standard application."""
    try:
        os.startfile(os.path.normpath(document))
        # Windows
    except:
        try:
            os.system('xdg-open "%s"' % os.path.normpath(document))
            # Linux
        except:
            try:
                os.system('open "%s"' % os.path.normpath(document))
                # Mac
            except:
                pass


class YwCnv:
    """Base class for Novel file conversion.

    Public methods:
        convert(sourceFile, targetFile) -- Convert sourceFile into targetFile.
    """

    def convert(self, source, target):
        """Convert source into target and return a message.

        Positional arguments:
            source, target -- Novel subclass instances.

        Operation:
        1. Make the source object read the source file.
        2. Make the target object merge the source object's instance variables.
        3. Make the target object write the target file.
        Return a message beginning with the ERROR constant in case of error.

        Error handling:
        - Check if source and target are correctly initialized.
        - Ask for permission to overwrite target.
        - Pass the error messages of the called methods of source and target.
        - The success message comes from target.write(), if called.       
        """
        if source.filePath is None:
            return f'{ERROR}Source "{os.path.normpath(source.filePath)}" is not of the supported type.'

        if not os.path.isfile(source.filePath):
            return f'{ERROR}"{os.path.normpath(source.filePath)}" not found.'

        if target.filePath is None:
            return f'{ERROR}Target "{os.path.normpath(target.filePath)}" is not of the supported type.'

        if os.path.isfile(target.filePath) and not self._confirm_overwrite(target.filePath):
            return f'{ERROR}Action canceled by user.'

        message = source.read()
        if message.startswith(ERROR):
            return message

        message = target.merge(source)
        if message.startswith(ERROR):
            return message

        return target.write()

    def _confirm_overwrite(self, fileName):
        """Return boolean permission to overwrite the target file.
        
        Positional argument:
            fileName -- path to the target file.
        
        This is a stub to be overridden by subclass methods.
        """
        return True


class YwCnvUi(YwCnv):
    """Base class for Novel file conversion with user interface.

    Public methods:
        export_from_yw(sourceFile, targetFile) -- Convert from yWriter project to other file format.
        create_yw(sourceFile, targetFile) -- Create target from source.
        import_to_yw(sourceFile, targetFile) -- Convert from any file format to yWriter project.

    Instance variables:
        ui -- Ui (can be overridden e.g. by subclasses).
        newFile -- str: path to the target file in case of success.   
    """

    def __init__(self):
        """Define instance variables."""
        self.ui = Ui('')
        # Per default, 'silent mode' is active.
        self.newFile = None
        # Also indicates successful conversion.

    def export_from_yw(self, source, target):
        """Convert from yWriter project to other file format.

        Positional arguments:
            source -- YwFile subclass instance.
            target -- Any Novel subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            f'Input: {source.DESCRIPTION} "{os.path.normpath(source.filePath)}"\nOutput: {target.DESCRIPTION} "{os.path.normpath(target.filePath)}"')
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath

    def create_yw7(self, source, target):
        """Create target from source.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Save the new file pathname.

        Error handling:
        - Tf target already exists as a file, the conversion is cancelled,
          an error message is sent to the UI.
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            f'Create a yWriter project file from {source.DESCRIPTION}\nNew project: "{os.path.normpath(target.filePath)}"')
        if os.path.isfile(target.filePath):
            self.ui.set_info_how(f'{ERROR}"{os.path.normpath(target.filePath)}" already exists.')
        else:
            message = self.convert(source, target)
            self.ui.set_info_how(message)
            if message.startswith(ERROR):
                self.newFile = None
            else:
                self.newFile = target.filePath

    def import_to_yw(self, source, target):
        """Convert from any file format to yWriter project.

        Positional arguments:
            source -- Any Novel subclass instance.
            target -- YwFile subclass instance.

        Operation:
        1. Send specific information about the conversion to the UI.
        2. Convert source into target.
        3. Pass the message to the UI.
        4. Delete the temporay file, if exists.
        5. Save the new file pathname.

        Error handling:
        - If the conversion fails, newFile is set to None.
        """
        self.ui.set_info_what(
            f'Input: {source.DESCRIPTION} "{os.path.normpath(source.filePath)}"\nOutput: {target.DESCRIPTION} "{os.path.normpath(target.filePath)}"')
        message = self.convert(source, target)
        self.ui.set_info_how(message)
        self._delete_tempfile(source.filePath)
        if message.startswith(ERROR):
            self.newFile = None
        else:
            self.newFile = target.filePath

    def _confirm_overwrite(self, filePath):
        """Return boolean permission to overwrite the target file.
        
        Positional arguments:
            fileName -- path to the target file.
        
        Overrides the superclass method.
        """
        return self.ui.ask_yes_no(f'Overwrite existing file "{os.path.normpath(filePath)}"?')

    def _delete_tempfile(self, filePath):
        """Delete filePath if it is a temporary file no longer needed."""
        if filePath.endswith('.html'):
            # Might it be a temporary text document?
            if os.path.isfile(filePath.replace('.html', '.odt')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass
        elif filePath.endswith('.csv'):
            # Might it be a temporary spreadsheet document?
            if os.path.isfile(filePath.replace('.csv', '.ods')):
                # Does a corresponding Office document exist?
                try:
                    os.remove(filePath)
                except:
                    pass

    def _open_newFile(self):
        """Open the converted file for editing and exit the converter script."""
        open_document(self.newFile)
        sys.exit(0)


class FileFactory:
    """Base class for conversion object factory classes.
    """

    def __init__(self, fileClasses=[]):
        """Write the parameter to a "private" instance variable.

        Optional arguments:
            _fileClasses -- list of classes from which an instance can be returned.
        """
        self._fileClasses = fileClasses


class ExportSourceFactory(FileFactory):
    """A factory class that instantiates a yWriter object to read.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion from a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: a YwFile subclass instance, or None in case of error
        - targetFile: None
        """
        __, fileExtension = os.path.splitext(sourcePath)
        for fileClass in self._fileClasses:
            if fileClass.EXTENSION == fileExtension:
                sourceFile = fileClass(sourcePath, **kwargs)
                return 'Source object created.', sourceFile, None
            
        return f'{ERROR}File type of "{os.path.normpath(sourcePath)}" not supported.', None, None


class ExportTargetFactory(FileFactory):
    """A factory class that instantiates a document object to write.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion from a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Optional arguments:
            suffix -- str: an indicator for the target file type.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: None
        - targetFile: a FileExport subclass instance, or None in case of error 
        """
        fileName, __ = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX == suffix:
                if suffix is None:
                    suffix = ''
                targetFile = fileClass(f'{fileName}{suffix}{fileClass.EXTENSION}', **kwargs)
                return 'Target object created.', None, targetFile

        return f'{ERROR}Export type "{suffix}" not supported.', None, None


class ImportSourceFactory(FileFactory):
    """A factory class that instantiates a documente object to read.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a source object for conversion to a yWriter project.       

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: a Novel subclass instance, or None in case of error
        - targetFile: None
        """
        for fileClass in self._fileClasses:
            if fileClass.SUFFIX is not None:
                if sourcePath.endswith(f'{fileClass.SUFFIX }{fileClass.EXTENSION}'):
                    sourceFile = fileClass(sourcePath, **kwargs)
                    return 'Source object created.', sourceFile, None

        return f'{ERROR}This document is not meant to be written back.', None, None


class ImportTargetFactory(FileFactory):
    """A factory class that instantiates a yWriter object to write.

    Public methods:
        make_file_objects(self, sourcePath, **kwargs) -- return conversion objects.
    """

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to a yWriter project.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Optional arguments:
            suffix -- str: an indicator for the source file type.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: None
        - targetFile: a YwFile subclass instance, or None in case of error
        """
        fileName, __ = os.path.splitext(sourcePath)
        sourceSuffix = kwargs['suffix']
        if sourceSuffix:
            ywPathBasis = fileName.split(sourceSuffix)[0]
        else:
            ywPathBasis = fileName

        # Look for an existing yWriter project to rewrite.
        for fileClass in self._fileClasses:
            if os.path.isfile(f'{ywPathBasis}{fileClass.EXTENSION}'):
                targetFile = fileClass(f'{ywPathBasis}{fileClass.EXTENSION}', **kwargs)
                return 'Target object created.', None, targetFile
            
        return f'{ERROR}No yWriter project to write.', None, None


class YwCnvFf(YwCnvUi):
    """Class for Novel file conversion using factory methods to create target and source classes.

    Public methods:
        run(sourcePath, **kwargs) -- create source and target objects and run conversion.

    Class constants:
        EXPORT_SOURCE_CLASSES -- list of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- list of FileExport subclasses to which export is possible.
        IMPORT_SOURCE_CLASSES -- list of Novel subclasses from which can be imported.
        IMPORT_TARGET_CLASSES -- list of YwFile subclasses to which import is possible.

    All lists are empty and meant to be overridden by subclasses.

    Instance variables:
        exportSourceFactory -- ExportSourceFactory.
        exportTargetFactory -- ExportTargetFactory.
        importSourceFactory -- ImportSourceFactory.
        importTargetFactory -- ImportTargetFactory.
        newProjectFactory -- FileFactory (a stub to be overridden by subclasses).
    """
    EXPORT_SOURCE_CLASSES = []
    EXPORT_TARGET_CLASSES = []
    IMPORT_SOURCE_CLASSES = []
    IMPORT_TARGET_CLASSES = []

    def __init__(self):
        """Create strategy class instances.
        
        Extends the superclass constructor.
        """
        super().__init__()
        self.exportSourceFactory = ExportSourceFactory(self.EXPORT_SOURCE_CLASSES)
        self.exportTargetFactory = ExportTargetFactory(self.EXPORT_TARGET_CLASSES)
        self.importSourceFactory = ImportSourceFactory(self.IMPORT_SOURCE_CLASSES)
        self.importTargetFactory = ImportTargetFactory(self.IMPORT_TARGET_CLASSES)
        self.newProjectFactory = FileFactory()

    def run(self, sourcePath, **kwargs):
        """Create source and target objects and run conversion.

        Positional arguments: 
            sourcePath -- str: the source file path.
        
        Required keyword arguments: 
            suffix -- str: target file name suffix.

        This is a template method that calls superclass methods as primitive operations by case.
        """
        self.newFile = None
        if not os.path.isfile(sourcePath):
            self.ui.set_info_how(f'{ERROR}File "{os.path.normpath(sourcePath)}" not found.')
            return
        
        message, source, __ = self.exportSourceFactory.make_file_objects(sourcePath, **kwargs)
        if message.startswith(ERROR):
            # The source file is not a yWriter project.
            message, source, __ = self.importSourceFactory.make_file_objects(sourcePath, **kwargs)
            if message.startswith(ERROR):
                # A new yWriter project might be required.
                message, source, target = self.newProjectFactory.make_file_objects(sourcePath, **kwargs)
                if message.startswith(ERROR):
                    self.ui.set_info_how(message)
                else:
                    self.create_yw7(source, target)
            else:
                # Try to update an existing yWriter project.
                kwargs['suffix'] = source.SUFFIX
                message, __, target = self.importTargetFactory.make_file_objects(sourcePath, **kwargs)
                if message.startswith(ERROR):
                    self.ui.set_info_how(message)
                else:
                    self.import_to_yw(source, target)
        else:
            # The source file is a yWriter project.
            message, __, target = self.exportTargetFactory.make_file_objects(sourcePath, **kwargs)
            if message.startswith(ERROR):
                self.ui.set_info_how(message)
            else:
                self.export_from_yw(source, target)
import re
from html import unescape
import xml.etree.ElementTree as ET
from urllib.parse import quote


class Chapter:
    """yWriter chapter representation.
    
    Public instance variables:
        title -- str: chapter title (may be the heading).
        desc -- str: chapter description in a single string.
        chLevel -- int: chapter level (part/chapter).
        oldType -- int: chapter type (Chapter/Other).
        chType -- int: chapter type yWriter 7.0.7.2+ (Normal/Notes/Todo).
        isUnused -- bool: True, if the chapter is marked "Unused".
        suppressChapterTitle -- bool: uppress chapter title when exporting.
        isTrash -- bool: True, if the chapter is the project's trash bin.
        suppressChapterBreak -- bool: Suppress chapter break when exporting.
        srtScenes -- list of str: the chapter's sorted scene IDs.        
    """

    def __init__(self):
        """Initialize instance variables."""
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

        self.oldType = None
        # int
        # xml: <Type>
        # 0 = chapter type (marked "Chapter")
        # 1 = other type (marked "Other")
        # Applies to projects created by a yWriter version prior to 7.0.7.2.

        self.chType = None
        # int
        # xml: <ChapterType>
        # 0 = Normal
        # 1 = Notes
        # 2 = Todo
        # Applies to projects created by yWriter version 7.0.7.2+.

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

        self.suppressChapterBreak = None
        # bool
        # xml: <Fields><Field_SuppressChapterBreak> 0

        self.srtScenes = []
        # list of str
        # xml: <Scenes><ScID>
        # The chapter's scene IDs. The order of its elements
        # corresponds to the chapter's order of the scenes.

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.


class Scene:
    """yWriter scene representation.
    
    Public instance variables:
        title -- str: scene title.
        desc -- str: scene description in a single string.
        sceneContent -- str: scene content (property with getter and setter).
        rtfFile -- str: RTF file name (yWriter 5).
        wordCount - int: word count (derived; updated by the sceneContent setter).
        letterCount - int: letter count (derived; updated by the sceneContent setter).
        isUnused -- bool: True if the scene is marked "Unused". 
        isNotesScene -- bool: True if the scene type is "Notes".
        isTodoScene -- bool: True if the scene type is "Todo". 
        doNotExport -- bool: True if the scene is not to be exported to RTF.
        status -- int: scene status (Outline/Draft/1st Edit/2nd Edit/Done).
        sceneNotes -- str: scene notes in a single string.
        tags -- list of scene tags. 
        field1 -- int: scene ratings field 1.
        field2 -- int: scene ratings field 2.
        field3 -- int: scene ratings field 3.
        field4 -- int: scene ratings field 4.
        appendToPrev -- bool: if True, append the scene without a divider to the previous scene.
        isReactionScene -- bool: if True, the scene is "reaction". Otherwise, it's "action". 
        isSubPlot -- bool: if True, the scene belongs to a sub-plot. Otherwise it's main plot.  
        goal -- str: the main actor's scene goal. 
        conflict -- str: what hinders the main actor to achieve his goal.
        outcome -- str: what comes out at the end of the scene.
        characters -- list of character IDs related to this scene.
        locations -- list of location IDs related to this scene. 
        items -- list of item IDs related to this scene.
        date -- str: specific start date in ISO format (yyyy-mm-dd).
        time -- str: specific start time in ISO format (hh:mm).
        minute -- str: unspecific start time: minutes.
        hour -- str: unspecific start time: hour.
        day -- str: unspecific start time: day.
        lastsMinutes -- str: scene duration: minutes.
        lastsHours -- str: scene duration: hours.
        lastsDays -- str: scene duration: days. 
        image -- str:  path to an image related to the scene. 
    """
    STATUS = (None, 'Outline', 'Draft', '1st Edit', '2nd Edit', 'Done')
    # Emulate an enumeration for the scene status
    # Since the items are used to replace text,
    # they may contain spaces. This is why Enum cannot be used here.

    ACTION_MARKER = 'A'
    REACTION_MARKER = 'R'
    NULL_DATE = '0001-01-01'
    NULL_TIME = '00:00:00'

    def __init__(self):
        """Initialize instance variables."""
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

        self.rtfFile = None
        # str
        # xml: <RTFFile>
        # Name of the file containing the scene in yWriter 5.

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

        self.isNotesScene = None
        # bool
        # xml: <Fields><Field_SceneType> 1

        self.isTodoScene = None
        # bool
        # xml: <Fields><Field_SceneType> 2

        self.doNotExport = None
        # bool
        # xml: <ExportCondSpecific><ExportWhenRTF>

        self.status = None
        # int
        # xml: <Status>
        # 1 - Outline
        # 2 - Draft
        # 3 - 1st Edit
        # 4 - 2nd Edit
        # 5 - Done
        # See also the STATUS list for conversion.

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

        self.image = None
        # str
        # xml: <ImageFile>

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.

    @property
    def sceneContent(self):
        return self._sceneContent

    @sceneContent.setter
    def sceneContent(self, text):
        """Set sceneContent updating word count and letter count."""
        self._sceneContent = text
        text = re.sub('--|—|–', ' ', text)
        # Make dashes separate words
        text = re.sub('\[.+?\]|\/\*.+?\*\/|\.|\,|-', '', text)
        # Remove comments and yWriter raw markup for word count; make hyphens join words
        wordList = text.split()
        self.wordCount = len(wordList)
        text = re.sub('\[.+?\]|\/\*.+?\*\/', '', self._sceneContent)
        # Remove yWriter raw markup for letter count
        text = text.replace('\n', '')
        text = text.replace('\r', '')
        self.letterCount = len(text)


class WorldElement:
    """Story world element representation (may be location or item).
    
    Public instance variables:
        title -- str: title (name).
        image -- str: image file path.
        desc -- str: description.
        tags -- list of tags.
        aka -- str: alternate name.
    """

    def __init__(self):
        """Initialize instance variables."""
        self.title = None
        # str
        # xml: <Title>

        self.image = None
        # str
        # xml: <ImageFile>

        self.desc = None
        # str
        # xml: <Desc>

        self.tags = None
        # list of str
        # xml: <Tags>

        self.aka = None
        # str
        # xml: <AKA>

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.


class Character(WorldElement):
    """yWriter character representation.

    Public instance variables:
        notes -- str: character notes.
        bio -- str: character biography.
        goals -- str: character's goals in the story.
        fullName -- str: full name (the title inherited may be a short name).
        isMajor -- bool: True, if it's a major character.
    """
    MAJOR_MARKER = 'Major'
    MINOR_MARKER = 'Minor'

    def __init__(self):
        """Extends the superclass constructor by adding instance variables."""
        super().__init__()

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


class Novel:
    """Abstract yWriter project file representation.

    This class represents a file containing a novel with additional 
    attributes and structural information (a full set or a subset
    of the information included in an yWriter project file).

    Public methods:
        read() -- parse the file and get the instance variables.
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the file.

    Public instance variables:
        title -- str: title.
        desc -- str: description in a single string.
        authorName -- str: author's name.
        author bio -- str: information about the author.
        fieldTitle1 -- str: scene rating field title 1.
        fieldTitle2 -- str: scene rating field title 2.
        fieldTitle3 -- str: scene rating field title 3.
        fieldTitle4 -- str: scene rating field title 4.
        chapters -- dict: (key: ID; value: chapter instance).
        scenes -- dict: (key: ID, value: scene instance).
        srtChapters -- list: the novel's sorted chapter IDs.
        locations -- dict: (key: ID, value: WorldElement instance).
        srtLocations -- list: the novel's sorted location IDs.
        items -- dict: (key: ID, value: WorldElement instance).
        srtItems -- list: the novel's sorted item IDs.
        characters -- dict: (key: ID, value: character instance).
        srtCharacters -- list: the novel's sorted character IDs.
        filePath -- str: path to the file (property with getter and setter). 
    """
    DESCRIPTION = 'Novel'
    EXTENSION = None
    SUFFIX = None
    # To be extended by subclass methods.

    CHAPTER_CLASS = Chapter
    SCENE_CLASS = Scene
    CHARACTER_CLASS = Character
    WE_CLASS = WorldElement

    def __init__(self, filePath, **kwargs):
        """Initialize instance variables.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Optional arguments:
            kwargs -- keyword arguments to be used by subclasses.            
        """
        self.title = None
        # str
        # xml: <PROJECT><Title>

        self.desc = None
        # str
        # xml: <PROJECT><Desc>

        self.authorName = None
        # str
        # xml: <PROJECT><AuthorName>

        self.authorBio = None
        # str
        # xml: <PROJECT><Bio>

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
        # key = chapter ID, value = Chapter instance.
        # The order of the elements does not matter (the novel's order of the chapters is defined by srtChapters)

        self.scenes = {}
        # dict
        # xml: <SCENES><SCENE><ID>
        # key = scene ID, value = Scene instance.
        # The order of the elements does not matter (the novel's order of the scenes is defined by
        # the order of the chapters and the order of the scenes within the chapters)

        self.srtChapters = []
        # list of str
        # The novel's chapter IDs. The order of its elements corresponds to the novel's order of the chapters.

        self.locations = {}
        # dict
        # xml: <LOCATIONS>
        # key = location ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtLocations = []
        # list of str
        # The novel's location IDs. The order of its elements
        # corresponds to the XML project file.

        self.items = {}
        # dict
        # xml: <ITEMS>
        # key = item ID, value = WorldElement instance.
        # The order of the elements does not matter.

        self.srtItems = []
        # list of str
        # The novel's item IDs. The order of its elements corresponds to the XML project file.

        self.characters = {}
        # dict
        # xml: <CHARACTERS>
        # key = character ID, value = Character instance.
        # The order of the elements does not matter.

        self.srtCharacters = []
        # list of str
        # The novel's character IDs. The order of its elements corresponds to the XML project file.

        self._filePath = None
        # str
        # Path to the file. The setter only accepts files of a supported type as specified by EXTENSION.

        self._projectName = None
        # str
        # URL-coded file name without suffix and extension.

        self._projectPath = None
        # str
        # URL-coded path to the project directory.

        self.filePath = filePath

        self.kwVar = {}
        # dictionary
        # Optional key/value instance variables for customization.

    @property
    def filePath(self):
        return self._filePath

    @filePath.setter
    def filePath(self, filePath):
        """Setter for the filePath instance variable.
                
        - Format the path string according to Python's requirements. 
        - Accept only filenames with the right suffix and extension.
        """
        if self.SUFFIX is not None:
            suffix = self.SUFFIX
        else:
            suffix = ''
        if filePath.lower().endswith(f'{suffix}{self.EXTENSION}'.lower()):
            self._filePath = filePath
            head, tail = os.path.split(os.path.realpath(filePath))
            self.projectPath = quote(head.replace('\\', '/'), '/:')
            self.projectName = quote(tail.replace(f'{suffix}{self.EXTENSION}', ''))

    def read(self):
        """Parse the file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Read method is not implemented.'

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Merge method is not implemented.'

    def write(self):
        """Write instance variables to the file.
        
        Return a message beginning with the ERROR constant in case of error.
        This is a stub to be overridden by subclass methods.
        """
        return f'{ERROR}Write method is not implemented.'

    def _convert_to_yw(self, text):
        """Return text, converted from source format to yw7 markup.
        
        Positional arguments:
            text -- string to convert.
        
        This is a stub to be overridden by subclass methods.
        """
        return text

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        This is a stub to be overridden by subclass methods.
        """
        return text


class Splitter:
    """Helper class for scene and chapter splitting.
    
    When importing scenes to yWriter, they may contain manuallyinserted scene and chapter dividers.
    The Splitter class updates a Novel instance by splitting such scenes and creating new chapters and scenes. 
    
    Public methods:
        split_scenes(novel) -- Split scenes by inserted chapter and scene dividers.
        
    Public class constants:
        PART_SEPARATOR -- marker indicating the beginning of a new part, splitting a scene.
        CHAPTER_SEPARATOR -- marker indicating the beginning of a new chapter, splitting a scene.
        DESC_SEPARATOR -- marker separating title and description of a chapter or scene.
    """
    PART_SEPARATOR = '#'
    CHAPTER_SEPARATOR = '##'
    SCENE_SEPARATOR = '###'
    DESC_SEPARATOR = '|'
    _CLIP_TITLE = 20
    # Maximum length of newly generated scene titles.

    def split_scenes(self, novel):
        """Split scenes by inserted chapter and scene dividers.
        
        Update a Novel instance by generating new chapters and scenes 
        if there are dividers within the scene content.
        
        Positional argument: 
            novel -- Novel instance to update.
        """

        def create_chapter(chapterId, title, desc, level):
            """Create a new chapter and add it to the novel.
            
            Positional arguments:
                chapterId -- str: ID of the chapter to create.
                title -- str: title of the chapter to create.
                desc -- str: description of the chapter to create.
                level -- int: chapter level (part/chapter).           
            """
            newChapter = novel.CHAPTER_CLASS()
            newChapter.title = title
            newChapter.desc = desc
            newChapter.chLevel = level
            newChapter.chType = 0
            novel.chapters[chapterId] = newChapter

        def create_scene(sceneId, parent, splitCount, title, desc):
            """Create a new scene and add it to the novel.
            
            Positional arguments:
                sceneId -- str: ID of the scene to create.
                parent -- Scene instance: parent scene.
                splitCount -- int: number of parent's splittings.
                title -- str: title of the scene to create.
                desc -- str: description of the scene to create.
            """
            WARNING = ' (!) '

            # Mark metadata of split scenes.
            newScene = novel.SCENE_CLASS()
            if title:
                newScene.title = title
            elif parent.title:
                if len(parent.title) > self._CLIP_TITLE:
                    title = f'{parent.title[:self._CLIP_TITLE]}...'
                else:
                    title = parent.title
                newScene.title = f'{title} Split: {splitCount}'
            else:
                newScene.title = f'New scene Split: {splitCount}'
            if desc:
                newScene.desc = desc
            if parent.desc and not parent.desc.startswith(WARNING):
                parent.desc = f'{WARNING}{parent.desc}'
            if parent.goal and not parent.goal.startswith(WARNING):
                parent.goal = f'{WARNING}{parent.goal}'
            if parent.conflict and not parent.conflict.startswith(WARNING):
                parent.conflict = f'{WARNING}{parent.conflict}'
            if parent.outcome and not parent.outcome.startswith(WARNING):
                parent.outcome = f'{WARNING}{parent.outcome}'

            # Reset the parent's status to Draft, if not Outline.
            if parent.status > 2:
                parent.status = 2
            newScene.status = parent.status
            newScene.isNotesScene = parent.isNotesScene
            newScene.isUnused = parent.isUnused
            newScene.isTodoScene = parent.isTodoScene
            newScene.date = parent.date
            newScene.time = parent.time
            newScene.day = parent.day
            newScene.hour = parent.hour
            newScene.minute = parent.minute
            newScene.lastsDays = parent.lastsDays
            newScene.lastsHours = parent.lastsHours
            newScene.lastsMinutes = parent.lastsMinutes
            novel.scenes[sceneId] = newScene

        # Get the maximum chapter ID and scene ID.
        chIdMax = 0
        scIdMax = 0
        for chId in novel.srtChapters:
            if int(chId) > chIdMax:
                chIdMax = int(chId)
        for scId in novel.scenes:
            if int(scId) > scIdMax:
                scIdMax = int(scId)

        # Process chapters and scenes.
        srtChapters = []
        for chId in novel.srtChapters:
            srtChapters.append(chId)
            chapterId = chId
            srtScenes = []
            for scId in novel.chapters[chId].srtScenes:
                srtScenes.append(scId)
                if not novel.scenes[scId].sceneContent:
                    continue

                sceneId = scId
                lines = novel.scenes[scId].sceneContent.split('\n')
                newLines = []
                inScene = True
                sceneSplitCount = 0

                # Search scene content for dividers.
                for line in lines:
                    heading = line.strip('# ').split(self.DESC_SEPARATOR)
                    title = heading[0]
                    try:
                        desc = heading[1]
                    except:
                        desc = ''
                    if line.startswith(self.SCENE_SEPARATOR):
                        # Split the scene.
                        novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                        newLines = []
                        sceneSplitCount += 1
                        scIdMax += 1
                        sceneId = str(scIdMax)
                        create_scene(sceneId, novel.scenes[scId], sceneSplitCount, title, desc)
                        srtScenes.append(sceneId)
                        inScene = True
                    elif line.startswith(self.CHAPTER_SEPARATOR):
                        # Start a new chapter.
                        if inScene:
                            novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                            newLines = []
                            sceneSplitCount = 0
                            inScene = False
                        novel.chapters[chapterId].srtScenes = srtScenes
                        srtScenes = []
                        chIdMax += 1
                        chapterId = str(chIdMax)
                        if not title:
                            title = 'New chapter'
                        create_chapter(chapterId, title, desc, 0)
                        srtChapters.append(chapterId)
                    elif line.startswith(self.PART_SEPARATOR):
                        # start a new part.
                        if inScene:
                            novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
                            newLines = []
                            sceneSplitCount = 0
                            inScene = False
                        novel.chapters[chapterId].srtScenes = srtScenes
                        srtScenes = []
                        chIdMax += 1
                        chapterId = str(chIdMax)
                        if not title:
                            title = 'New part'
                        create_chapter(chapterId, title, desc, 1)
                        srtChapters.append(chapterId)
                    elif not inScene:
                        # Append a scene without heading to a new chapter or part.
                        newLines.append(line)
                        sceneSplitCount += 1
                        scIdMax += 1
                        sceneId = str(scIdMax)
                        create_scene(sceneId, novel.scenes[scId], sceneSplitCount, '', '')
                        srtScenes.append(sceneId)
                        inScene = True
                    else:
                        newLines.append(line)
                novel.scenes[sceneId].sceneContent = '\n'.join(newLines)
            novel.chapters[chapterId].srtScenes = srtScenes
        novel.srtChapters = srtChapters


def indent(elem, level=0):
    """xml pretty printer

    Kudos to to Fredrik Lundh. 
    Source: http://effbot.org/zone/element-lib.htm#prettyprint
    """
    i = f'\n{level * "  "}'
    if elem:
        if not elem.text or not elem.text.strip():
            elem.text = f'{i}  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


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
    """
    DESCRIPTION = 'yWriter 7 project'
    EXTENSION = '.yw7'
    _CDATA_TAGS = ['Title', 'AuthorName', 'Bio', 'Desc',
                   'FieldTitle1', 'FieldTitle2', 'FieldTitle3',
                   'FieldTitle4', 'LaTeXHeaderFile', 'Tags',
                   'AKA', 'ImageFile', 'FullName', 'Goals',
                   'Notes', 'RTFFile', 'SceneContent',
                   'Outcome', 'Goal', 'Conflict']
    # Names of xml elements containing CDATA.
    # ElementTree.write omits CDATA tags, so they have to be inserted afterwards.

    _PRJ_KWVAR = ()
    _CHP_KWVAR = ()
    _SCN_KWVAR = ()
    _CRT_KWVAR = ()
    _LOC_KWVAR = ()
    _ITM_KWVAR = ()
    # Keyword variables for custom fields in the .yw7 XML file.

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

        #--- Initialize custom keyword variables.
        for field in self._PRJ_KWVAR:
            self.kwVar[field] = None

    def read(self):
        """Parse the yWriter xml file and get the instance variables.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if self.is_locked():
            return f'{ERROR}yWriter seems to be open. Please close first.'
        try:
            self.tree = ET.parse(self.filePath)
        except:
            return f'{ERROR}Can not process "{os.path.normpath(self.filePath)}".'

        root = self.tree.getroot()

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
                    tags = loc.find('Tags').text.split(';')
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
                    tags = itm.find('Tags').text.split(';')
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
                    tags = crt.find('Tags').text.split(';')
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

        #--- Read attributes at novel level from the xml element tree.
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

            if chp.find('Type') is not None:
                self.chapters[chId].oldType = int(chp.find('Type').text)

            if chp.find('ChapterType') is not None:
                self.chapters[chId].chType = int(chp.find('ChapterType').text)

            if chp.find('Unused') is not None:
                self.chapters[chId].isUnused = True
            else:
                self.chapters[chId].isUnused = False
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

            self.chapters[chId].srtScenes = []
            if chp.find('Scenes') is not None:
                for scn in chp.find('Scenes').findall('ScID'):
                    scId = scn.text
                    self.chapters[chId].srtScenes.append(scId)

        #--- Read attributes at scene level from the xml element tree.
        for scn in root.iter('SCENE'):
            scId = scn.find('ID').text
            self.scenes[scId] = self.SCENE_CLASS()

            if scn.find('Title') is not None:
                self.scenes[scId].title = scn.find('Title').text

            if scn.find('Desc') is not None:
                self.scenes[scId].desc = scn.find('Desc').text

            if scn.find('RTFFile') is not None:
                self.scenes[scId].rtfFile = scn.find('RTFFile').text

            # This is relevant for yW5 files with no SceneContent:
            if scn.find('WordCount') is not None:
                self.scenes[scId].wordCount = int(
                    scn.find('WordCount').text)

            if scn.find('LetterCount') is not None:
                self.scenes[scId].letterCount = int(
                    scn.find('LetterCount').text)

            if scn.find('SceneContent') is not None:
                sceneContent = scn.find('SceneContent').text
                if sceneContent is not None:
                    self.scenes[scId].sceneContent = sceneContent

            if scn.find('Unused') is not None:
                self.scenes[scId].isUnused = True
            else:
                self.scenes[scId].isUnused = False
            self.scenes[scId].isNotesScene = False
            self.scenes[scId].isTodoScene = False

            #--- Initialize custom keyword variables.
            for fieldName in self._SCN_KWVAR:
                self.scenes[scId].kwVar[fieldName] = None

            #--- Read scene fields.
            for scFields in scn.findall('Fields'):
                self.scenes[scId].isTodoScene = False
                if scFields.find('Field_SceneType') is not None:
                    if scFields.find('Field_SceneType').text == '1':
                        self.scenes[scId].isNotesScene = True
                    if scFields.find('Field_SceneType').text == '2':
                        self.scenes[scId].isTodoScene = True

                #--- Read scene custom fields.
                for fieldName in self._SCN_KWVAR:
                    field = scFields.find(fieldName)
                    if field is not None:
                        self.scenes[scId].kwVar[fieldName] = field.text

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
                    tags = scn.find('Tags').text.split(';')
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

        # Make sure that ToDo, Notes, and Unused type is inherited from the chapter.
        for chId in self.chapters:
            if self.chapters[chId].chType == 2:
                # Chapter is "ToDo" type.
                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isTodoScene = True
                    self.scenes[scId].isUnused = True
            elif self.chapters[chId].chType == 1:
                # Chapter is "Notes" type.
                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isNotesScene = True
                    self.scenes[scId].isUnused = True
            elif self.chapters[chId].isUnused:
                for scId in self.chapters[chId].srtScenes:
                    self.scenes[scId].isUnused = True
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
            for i in range(len(srcLst)):
                if not srcLst[i] in tgtLst:
                    tgtLst.insert(j, srcLst[i])
                    j += 1
                else:
                    j = tgtLst.index(srcLst[i]) + 1

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
                        self.locations[lcId].kwVar[fieldName] = temploc[lcId].kwVar[fieldName]

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
                        self.items[itId].kwVar[fieldName] = tempitm[itId].kwVar[fieldName]

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
                        self.characters[crId].kwVar[fieldName] = tempchr[crId].kwVar[fieldName]

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
            if source.scenes[scId].isUnused is not None:
                self.scenes[scId].isUnused = source.scenes[scId].isUnused
            if source.scenes[scId].isNotesScene is not None:
                self.scenes[scId].isNotesScene = source.scenes[scId].isNotesScene
            if source.scenes[scId].isTodoScene is not None:
                self.scenes[scId].isTodoScene = source.scenes[scId].isTodoScene
            if source.scenes[scId].status is not None:
                self.scenes[scId].status = source.scenes[scId].status
            if source.scenes[scId].sceneNotes is not None:
                self.scenes[scId].sceneNotes = source.scenes[scId].sceneNotes
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
            if source.chapters[chId].oldType is not None:
                self.chapters[chId].oldType = source.chapters[chId].oldType
            if source.chapters[chId].chType is not None:
                self.chapters[chId].chType = source.chapters[chId].chType
            if source.chapters[chId].isUnused is not None:
                self.chapters[chId].isUnused = source.chapters[chId].isUnused
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
            sceneSplitter.split_scenes(self)
        return 'yWriter project data updated or created.'

    def write(self):
        """Write instance variables to the yWriter xml file.
        
        Open the yWriter xml file located at filePath and replace the instance variables 
        not being None. Create new XML elements if necessary.
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if self.is_locked():
            return f'{ERROR}yWriter seems to be open. Please close first.'

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

            if prjScn.isUnused:
                if xmlScn.find('Unused') is None:
                    ET.SubElement(xmlScn, 'Unused').text = '-1'
            elif xmlScn.find('Unused') is not None:
                xmlScn.remove(xmlScn.find('Unused'))

            #--- Write scene fields.
            scFields = xmlScn.find('Fields')
            if prjScn.isNotesScene:
                if scFields is None:
                    scFields = ET.SubElement(xmlScn, 'Fields')
                try:
                    scFields.find('Field_SceneType').text = '1'
                except(AttributeError):
                    ET.SubElement(scFields, 'Field_SceneType').text = '1'
            elif scFields is not None:
                if scFields.find('Field_SceneType') is not None:
                    if scFields.find('Field_SceneType').text == '1':
                        scFields.remove(scFields.find('Field_SceneType'))

            if prjScn.isTodoScene:
                if scFields is None:
                    scFields = ET.SubElement(xmlScn, 'Fields')
                try:
                    scFields.find('Field_SceneType').text = '2'
                except(AttributeError):
                    ET.SubElement(scFields, 'Field_SceneType').text = '2'
            elif scFields is not None:
                if scFields.find('Field_SceneType') is not None:
                    if scFields.find('Field_SceneType').text == '2':
                        scFields.remove(scFields.find('Field_SceneType'))

            #--- Write scene custom fields.
            for field in self._SCN_KWVAR:
                if field in self.scenes[scId].kwVar and self.scenes[scId].kwVar[field]:
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

            if prjScn.sceneNotes is not None:
                try:
                    xmlScn.find('Notes').text = prjScn.sceneNotes
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Notes').text = prjScn.sceneNotes

            if prjScn.tags is not None:
                try:
                    xmlScn.find('Tags').text = ';'.join(prjScn.tags)
                except(AttributeError):
                    ET.SubElement(xmlScn, 'Tags').text = ';'.join(prjScn.tags)

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

            # Characters/locations/items
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

            if prjChp.oldType is not None:
                try:
                    xmlChp.find('Type').text = str(prjChp.oldType)
                except(AttributeError):
                    ET.SubElement(xmlChp, 'Type').text = str(prjChp.oldType)

            if prjChp.chType is not None:
                try:
                    xmlChp.find('ChapterType').text = str(prjChp.chType)
                except(AttributeError):
                    ET.SubElement(xmlChp, 'ChapterType').text = str(prjChp.chType)

            if prjChp.isUnused:
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
                if field in self.chapters[chId].kwVar and self.chapters[chId].kwVar[field]:
                    if chFields is None:
                        chFields = ET.SubElement(xmlChp, 'Fields')
                    try:
                        chFields.find(field).text = self.chapters[chId].kwVar[field]
                    except(AttributeError):
                        ET.SubElement(chFields, field).text = self.chapters[chId].kwVar[field]
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
            ET.SubElement(xmlLoc, 'ID').text = lcId
            if prjLoc.title is not None:
                ET.SubElement(xmlLoc, 'Title').text = prjLoc.title

            if prjLoc.image is not None:
                ET.SubElement(xmlLoc, 'ImageFile').text = prjLoc.image

            if prjLoc.desc is not None:
                ET.SubElement(xmlLoc, 'Desc').text = prjLoc.desc

            if prjLoc.aka is not None:
                ET.SubElement(xmlLoc, 'AKA').text = prjLoc.aka

            if prjLoc.tags is not None:
                ET.SubElement(xmlLoc, 'Tags').text = ';'.join(prjLoc.tags)

            ET.SubElement(xmlLoc, 'SortOrder').text = str(sortOrder)

            #--- Write location custom fields.
            lcFields = xmlLoc.find('Fields')
            for field in self._LOC_KWVAR:
                if field in self.locations[lcId].kwVar and self.locations[lcId].kwVar[field]:
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

        def build_item_subtree(xmlItm, prjItm, sortOrder):
            ET.SubElement(xmlItm, 'ID').text = itId

            if prjItm.title is not None:
                ET.SubElement(xmlItm, 'Title').text = prjItm.title

            if prjItm.image is not None:
                ET.SubElement(xmlItm, 'ImageFile').text = prjItm.image

            if prjItm.desc is not None:
                ET.SubElement(xmlItm, 'Desc').text = prjItm.desc

            if prjItm.aka is not None:
                ET.SubElement(xmlItm, 'AKA').text = prjItm.aka

            if prjItm.tags is not None:
                ET.SubElement(xmlItm, 'Tags').text = ';'.join(prjItm.tags)

            ET.SubElement(xmlItm, 'SortOrder').text = str(sortOrder)

            #--- Write item custom fields.
            itFields = xmlItm.find('Fields')
            for field in self._ITM_KWVAR:
                if field in self.items[itId].kwVar and self.items[itId].kwVar[field]:
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
            ET.SubElement(xmlCrt, 'ID').text = crId

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
                ET.SubElement(xmlCrt, 'Tags').text = ';'.join(prjCrt.tags)

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
                if field in self.characters[crId].kwVar and self.characters[crId].kwVar[field]:
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

            #--- Write project custom fields.
            prjFields = xmlPrj.find('Fields')
            for field in self._PRJ_KWVAR:
                setting = self.kwVar[field]
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
            scenes = root.find('SCENES')
            chapters = root.find('CHAPTERS')
        except(AttributeError):
            # Build a new tree.
            root = ET.Element(TAG)
            xmlPrj = ET.SubElement(root, 'PROJECT')
            locations = ET.SubElement(root, 'LOCATIONS')
            items = ET.SubElement(root, 'ITEMS')
            characters = ET.SubElement(root, 'CHARACTERS')
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
            build_character_subtree(xmlCrt, self.characters[crId], sortOrder)

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
            return f'{ERROR}Cannot write "{os.path.normpath(ywProject.filePath)}".'

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
            return f'{ERROR}Can not write "{os.path.normpath(filePath)}".'

        return f'"{os.path.normpath(filePath)}" written.'

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
            if self.kwVar[field]:
                self.kwVar[field] = ''
                hasChanged = True
        for chId in self.chapters:
            for field in self._CHP_KWVAR:
                if self.chapters[chId].kwVar[field]:
                    self.chapters[chId].kwVar[field] = ''
                    hasChanged = True
        for scId in self.scenes:
            for field in self._SCN_KWVAR:
                if self.scenes[scId].kwVar[field]:
                    self.scenes[scId].kwVar[field] = ''
                    hasChanged = True
        return hasChanged




def read_html_file(filePath):
    """Open a html file being encoded utf-8 or ANSI.
    
    Return a tuple:
    message = Message beginning with the ERROR constant in case of error.
    content = The file content in a single string. None in case of error.
    """
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        # HTML files exported by a word processor may be ANSI encoded.
        try:
            with open(filePath, 'r') as f:
                content = (f.read())
        except(FileNotFoundError):
            return f'{ERROR}"{os.path.normpath(filePath)}" not found.', None

    return 'HTML data read in.', content
from string import Template


class Filter:
    """Filter an entity (chapter/scene/character/location/item) by filter criteria.
    
    Public methods:
        accept(source, eId) -- check whether an entity matches the filter criteria.
    
    Strategy class, implementing filtering criteria for template-based export.
    This is a stub with no filter criteria specified.
    """

    def accept(self, source, eId):
        """Check whether an entity matches the filter criteria.
        
        Positional arguments:
            source -- Novel instance holding the entity to check.
            eId -- ID of the entity to check.       
        
        Return True if the entity is not to be filtered out.
        This is a stub to be overridden by subclass methods implementing filters.
        """
        return True


class FileExport(Novel):
    """Abstract yWriter project file exporter representation.
    
    Public methods:
        merge(source) -- update instance variables from a source instance.
        write() -- write instance variables to the export file.
    
    This class is generic and contains no conversion algorithm and no templates.
    """
    SUFFIX = ''
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _notesPartTemplate = ''
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

    def __init__(self, filePath, **kwargs):
        """Initialize filter strategy class instances.
        
        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
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

    def merge(self, source):
        """Update instance variables from a source instance.
        
        Positional arguments:
            source -- Novel subclass instance to merge.
        
        Return a message beginning with the ERROR constant in case of error.
        Overrides the superclass method.
        """
        if source.title is not None:
            self.title = source.title
        else:
            self.title = ''

        if source.desc is not None:
            self.desc = source.desc
        else:
            self.desc = ''

        if source.authorName is not None:
            self.authorName = source.authorName
        else:
            self.authorName = ''

        if source.authorBio is not None:
            self.authorBio = source.authorBio
        else:
            self.authorBio = ''

        if source.fieldTitle1 is not None:
            self.fieldTitle1 = source.fieldTitle1
        else:
            self.fieldTitle1 = 'Field 1'

        if source.fieldTitle2 is not None:
            self.fieldTitle2 = source.fieldTitle2
        else:
            self.fieldTitle2 = 'Field 2'

        if source.fieldTitle3 is not None:
            self.fieldTitle3 = source.fieldTitle3
        else:
            self.fieldTitle3 = 'Field 3'

        if source.fieldTitle4 is not None:
            self.fieldTitle4 = source.fieldTitle4
        else:
            self.fieldTitle4 = 'Field 4'

        if source.srtChapters:
            self.srtChapters = source.srtChapters

        if source.scenes is not None:
            self.scenes = source.scenes

        if source.chapters is not None:
            self.chapters = source.chapters

        if source.srtCharacters:
            self.srtCharacters = source.srtCharacters
            self.characters = source.characters

        if source.srtLocations:
            self.srtLocations = source.srtLocations
            self.locations = source.locations

        if source.srtItems:
            self.srtItems = source.srtItems
            self.items = source.items
        return 'Export data updated from novel.'

    def _get_fileHeaderMapping(self):
        """Return a mapping dictionary for the project section.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        projectTemplateMapping = dict(
            Title=self._convert_from_yw(self.title, True),
            Desc=self._convert_from_yw(self.desc),
            AuthorName=self._convert_from_yw(self.authorName, True),
            AuthorBio=self._convert_from_yw(self.authorBio, True),
            FieldTitle1=self._convert_from_yw(self.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.fieldTitle4, True),
        )
        return projectTemplateMapping

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section.
        
        Positional arguments:
            chId -- str: chapter ID.
            chapterNumber -- int: chapter number.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if chapterNumber == 0:
            chapterNumber = ''

        chapterMapping = dict(
            ID=chId,
            ChapterNumber=chapterNumber,
            Title=self._convert_from_yw(self.chapters[chId].title, True),
            Desc=self._convert_from_yw(self.chapters[chId].desc),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return chapterMapping

    def _get_sceneMapping(self, scId, sceneNumber, wordsTotal, lettersTotal):
        """Return a mapping dictionary for a scene section.
        
        Positional arguments:
            scId -- str: scene ID.
            sceneNumber -- int: scene number to be displayed.
            wordsTotal -- int: accumulated wordcount.
            lettersTotal -- int: accumulated lettercount.
        
        This is a template method that can be extended or overridden by subclasses.
        """

        #--- Create a comma separated tag list.
        if sceneNumber == 0:
            sceneNumber = ''
        if self.scenes[scId].tags is not None:
            tags = self._get_string(self.scenes[scId].tags)
        else:
            tags = ''

        #--- Create a comma separated character list.
        try:
            # Note: Due to a bug, yWriter scenes might hold invalid
            # viepoint characters
            sChList = []
            for chId in self.scenes[scId].characters:
                sChList.append(self.characters[chId].title)
            sceneChars = self._get_string(sChList)
            viewpointChar = sChList[0]
        except:
            sceneChars = ''
            viewpointChar = ''

        #--- Create a comma separated location list.
        if self.scenes[scId].locations is not None:
            sLcList = []
            for lcId in self.scenes[scId].locations:
                sLcList.append(self.locations[lcId].title)
            sceneLocs = self._get_string(sLcList)
        else:
            sceneLocs = ''

        #--- Create a comma separated item list.
        if self.scenes[scId].items is not None:
            sItList = []
            for itId in self.scenes[scId].items:
                sItList.append(self.items[itId].title)
            sceneItems = self._get_string(sItList)
        else:
            sceneItems = ''

        #--- Create A/R marker string.
        if self.scenes[scId].isReactionScene:
            reactionScene = Scene.REACTION_MARKER
        else:
            reactionScene = Scene.ACTION_MARKER

        #--- Create a combined scDate information.
        if self.scenes[scId].date is not None and self.scenes[scId].date != Scene.NULL_DATE:
            scDay = ''
            scDate = self.scenes[scId].date
            cmbDate = self.scenes[scId].date
        else:
            scDate = ''
            if self.scenes[scId].day is not None:
                scDay = self.scenes[scId].day
                cmbDate = f'Day {self.scenes[scId].day}'
            else:
                scDay = ''
                cmbDate = ''

        #--- Create a combined time information.
        if self.scenes[scId].time is not None and self.scenes[scId].date != Scene.NULL_DATE:
            scHour = ''
            scMinute = ''
            scTime = self.scenes[scId].time
            cmbTime = self.scenes[scId].time.rsplit(':', 1)[0]
        else:
            scTime = ''
            if self.scenes[scId].hour or self.scenes[scId].minute:
                if self.scenes[scId].hour:
                    scHour = self.scenes[scId].hour
                else:
                    scHour = '00'
                if self.scenes[scId].minute:
                    scMinute = self.scenes[scId].minute
                else:
                    scMinute = '00'
                cmbTime = f'{scHour.zfill(2)}:{scMinute.zfill(2)}'
            else:
                scHour = ''
                scMinute = ''
                cmbTime = ''

        #--- Create a combined duration information.
        if self.scenes[scId].lastsDays is not None and self.scenes[scId].lastsDays != '0':
            lastsDays = self.scenes[scId].lastsDays
            days = f'{self.scenes[scId].lastsDays}d '
        else:
            lastsDays = ''
            days = ''
        if self.scenes[scId].lastsHours is not None and self.scenes[scId].lastsHours != '0':
            lastsHours = self.scenes[scId].lastsHours
            hours = f'{self.scenes[scId].lastsHours}h '
        else:
            lastsHours = ''
            hours = ''
        if self.scenes[scId].lastsMinutes is not None and self.scenes[scId].lastsMinutes != '0':
            lastsMinutes = self.scenes[scId].lastsMinutes
            minutes = f'{self.scenes[scId].lastsMinutes}min'
        else:
            lastsMinutes = ''
            minutes = ''
        duration = f'{days}{hours}{minutes}'

        sceneMapping = dict(
            ID=scId,
            SceneNumber=sceneNumber,
            Title=self._convert_from_yw(self.scenes[scId].title, True),
            Desc=self._convert_from_yw(self.scenes[scId].desc),
            WordCount=str(self.scenes[scId].wordCount),
            WordsTotal=wordsTotal,
            LetterCount=str(self.scenes[scId].letterCount),
            LettersTotal=lettersTotal,
            Status=Scene.STATUS[self.scenes[scId].status],
            SceneContent=self._convert_from_yw(self.scenes[scId].sceneContent),
            FieldTitle1=self._convert_from_yw(self.fieldTitle1, True),
            FieldTitle2=self._convert_from_yw(self.fieldTitle2, True),
            FieldTitle3=self._convert_from_yw(self.fieldTitle3, True),
            FieldTitle4=self._convert_from_yw(self.fieldTitle4, True),
            Field1=self.scenes[scId].field1,
            Field2=self.scenes[scId].field2,
            Field3=self.scenes[scId].field3,
            Field4=self.scenes[scId].field4,
            Date=scDate,
            Time=scTime,
            Day=scDay,
            Hour=scHour,
            Minute=scMinute,
            ScDate=cmbDate,
            ScTime=cmbTime,
            LastsDays=lastsDays,
            LastsHours=lastsHours,
            LastsMinutes=lastsMinutes,
            Duration=duration,
            ReactionScene=reactionScene,
            Goal=self._convert_from_yw(self.scenes[scId].goal),
            Conflict=self._convert_from_yw(self.scenes[scId].conflict),
            Outcome=self._convert_from_yw(self.scenes[scId].outcome),
            Tags=self._convert_from_yw(tags, True),
            Image=self.scenes[scId].image,
            Characters=sceneChars,
            Viewpoint=viewpointChar,
            Locations=sceneLocs,
            Items=sceneItems,
            Notes=self._convert_from_yw(self.scenes[scId].sceneNotes),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return sceneMapping

    def _get_characterMapping(self, crId):
        """Return a mapping dictionary for a character section.
        
        Positional arguments:
            crId -- str: character ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.characters[crId].tags is not None:
            tags = self._get_string(self.characters[crId].tags)
        else:
            tags = ''
        if self.characters[crId].isMajor:
            characterStatus = Character.MAJOR_MARKER
        else:
            characterStatus = Character.MINOR_MARKER

        characterMapping = dict(
            ID=crId,
            Title=self._convert_from_yw(self.characters[crId].title, True),
            Desc=self._convert_from_yw(self.characters[crId].desc),
            Tags=self._convert_from_yw(tags),
            Image=self.characters[crId].image,
            AKA=self._convert_from_yw(self.characters[crId].aka, True),
            Notes=self._convert_from_yw(self.characters[crId].notes),
            Bio=self._convert_from_yw(self.characters[crId].bio),
            Goals=self._convert_from_yw(self.characters[crId].goals),
            FullName=self._convert_from_yw(self.characters[crId].fullName, True),
            Status=characterStatus,
            ProjectName=self._convert_from_yw(self.projectName),
            ProjectPath=self.projectPath,
        )
        return characterMapping

    def _get_locationMapping(self, lcId):
        """Return a mapping dictionary for a location section.
        
        Positional arguments:
            lcId -- str: location ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.locations[lcId].tags is not None:
            tags = self._get_string(self.locations[lcId].tags)
        else:
            tags = ''

        locationMapping = dict(
            ID=lcId,
            Title=self._convert_from_yw(self.locations[lcId].title, True),
            Desc=self._convert_from_yw(self.locations[lcId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.locations[lcId].image,
            AKA=self._convert_from_yw(self.locations[lcId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return locationMapping

    def _get_itemMapping(self, itId):
        """Return a mapping dictionary for an item section.
        
        Positional arguments:
            itId -- str: item ID.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        if self.items[itId].tags is not None:
            tags = self._get_string(self.items[itId].tags)
        else:
            tags = ''

        itemMapping = dict(
            ID=itId,
            Title=self._convert_from_yw(self.items[itId].title, True),
            Desc=self._convert_from_yw(self.items[itId].desc),
            Tags=self._convert_from_yw(tags, True),
            Image=self.items[itId].image,
            AKA=self._convert_from_yw(self.items[itId].aka, True),
            ProjectName=self._convert_from_yw(self.projectName, True),
            ProjectPath=self.projectPath,
        )
        return itemMapping

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

    def _get_scenes(self, chId, sceneNumber, wordsTotal, lettersTotal, doNotExport):
        """Process the scenes.
        
        Positional arguments:
            chId -- str: chapter ID.
            sceneNumber -- int: number of previously processed scenes.
            wordsTotal -- int: accumulated wordcount of the previous scenes.
            lettersTotal -- int: accumulated lettercount of the previous scenes.
            doNotExport -- bool: scene belongs to a chapter that is not to be exported.
        
        Iterate through a sorted scene list and apply the templates, 
        substituting placeholders according to the scene mapping dictionary.
        Skip scenes not accepted by the scene filter.
        
        Return a tuple:
            lines -- list of strings: the lines of the processed scene.
            sceneNumber -- int: number of all processed scenes.
            wordsTotal -- int: accumulated wordcount of all processed scenes.
            lettersTotal -- int: accumulated lettercount of all processed scenes.
        
        This is a template method that can be extended or overridden by subclasses.
        """
        lines = []
        firstSceneInChapter = True
        for scId in self.chapters[chId].srtScenes:
            dispNumber = 0
            if not self._sceneFilter.accept(self, scId):
                continue
            # The order counts; be aware that "Todo" and "Notes" scenes are
            # always unused.
            if self.scenes[scId].isTodoScene:
                if self._todoSceneTemplate:
                    template = Template(self._todoSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].isNotesScene:
                # Scene is "Notes" type.
                if self._notesSceneTemplate:
                    template = Template(self._notesSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].isUnused or self.chapters[chId].isUnused:
                if self._unusedSceneTemplate:
                    template = Template(self._unusedSceneTemplate)
                else:
                    continue

            elif self.chapters[chId].oldType == 1:
                # Scene is "Info" type (old file format).
                if self._notesSceneTemplate:
                    template = Template(self._notesSceneTemplate)
                else:
                    continue

            elif self.scenes[scId].doNotExport or doNotExport:
                if self._notExportedSceneTemplate:
                    template = Template(self._notExportedSceneTemplate)
                else:
                    continue

            else:
                sceneNumber += 1
                dispNumber = sceneNumber
                wordsTotal += self.scenes[scId].wordCount
                lettersTotal += self.scenes[scId].letterCount
                template = Template(self._sceneTemplate)
                if not firstSceneInChapter and self.scenes[scId].appendToPrev and self._appendedSceneTemplate:
                    template = Template(self._appendedSceneTemplate)
            if not (firstSceneInChapter or self.scenes[scId].appendToPrev):
                lines.append(self._sceneDivider)
            if firstSceneInChapter and self._firstSceneTemplate:
                template = Template(self._firstSceneTemplate)
            lines.append(template.safe_substitute(self._get_sceneMapping(
                        scId, dispNumber, wordsTotal, lettersTotal)))
            firstSceneInChapter = False
        return lines, sceneNumber, wordsTotal, lettersTotal

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
        for chId in self.srtChapters:
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
            for scId in self.chapters[chId].srtScenes:
                sceneCount += 1
                if self.scenes[scId].doNotExport:
                    notExportCount += 1
            if sceneCount > 0 and notExportCount == sceneCount:
                doNotExport = True
            if self.chapters[chId].chType == 2:
                # Chapter is "ToDo" type (implies "unused").
                if self._todoChapterTemplate:
                    template = Template(self._todoChapterTemplate)
            elif self.chapters[chId].chType == 1:
                # Chapter is "Notes" type (implies "unused").
                if self.chapters[chId].chLevel == 1:
                    # Chapter is "Notes Part" type.
                    if self._notesPartTemplate:
                        template = Template(self._notesPartTemplate)
                elif self._notesChapterTemplate:
                    template = Template(self._notesChapterTemplate)
            elif self.chapters[chId].isUnused:
                # Chapter is "really" unused.
                if self._unusedChapterTemplate:
                    template = Template(self._unusedChapterTemplate)
            elif self.chapters[chId].oldType == 1:
                # Chapter is "Info" type (old file format).
                if self._notesChapterTemplate:
                    template = Template(self._notesChapterTemplate)
            elif doNotExport:
                if self._notExportedChapterTemplate:
                    template = Template(self._notExportedChapterTemplate)
            elif self.chapters[chId].chLevel == 1 and self._partTemplate:
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
            if self.chapters[chId].chType == 2:
                if self._todoChapterEndTemplate:
                    template = Template(self._todoChapterEndTemplate)
            elif self.chapters[chId].chType == 1:
                if self._notesChapterEndTemplate:
                    template = Template(self._notesChapterEndTemplate)
            elif self.chapters[chId].isUnused:
                if self._unusedChapterEndTemplate:
                    template = Template(self._unusedChapterEndTemplate)
            elif self.chapters[chId].oldType == 1:
                if self._notesChapterEndTemplate:
                    template = Template(self._notesChapterEndTemplate)
            elif doNotExport:
                if self._notExportedChapterEndTemplate:
                    template = Template(self._notExportedChapterEndTemplate)
            elif self._chapterEndTemplate:
                template = Template(self._chapterEndTemplate)
            if template is not None:
                lines.append(template.safe_substitute(self._get_chapterMapping(chId, dispNumber)))
        return lines

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
        for crId in self.srtCharacters:
            if self._characterFilter.accept(self, crId):
                lines.append(template.safe_substitute(self._get_characterMapping(crId)))
        return lines

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
        for lcId in self.srtLocations:
            if self._locationFilter.accept(self, lcId):
                lines.append(template.safe_substitute(self._get_locationMapping(lcId)))
        return lines

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
        for itId in self.srtItems:
            if self._itemFilter.accept(self, itId):
                lines.append(template.safe_substitute(self._get_itemMapping(itId)))
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
        lines.append(self._fileFooter)
        return ''.join(lines)

    def write(self):
        """Write instance variables to the export file.
        
        Create a template-based output file. 
        Return a message beginning with the ERROR constant in case of error.
        """
        text = self._get_text()
        backedUp = False
        if os.path.isfile(self.filePath):
            try:
                os.replace(self.filePath, f'{self.filePath}.bak')
                backedUp = True
            except:
                return f'{ERROR}Cannot overwrite "{os.path.normpath(self.filePath)}".'

        try:
            with open(self.filePath, 'w', encoding='utf-8') as f:
                f.write(text)
        except:
            if backedUp:
                os.replace(f'{self.filePath}.bak', self.filePath)
            return f'{ERROR}Cannot write "{os.path.normpath(self.filePath)}".'

        return f'"{os.path.normpath(self.filePath)}" written.'

    def _get_string(self, elements):
        """Join strings from a list.
        
        Return a string which is the concatenation of the 
        members of the list of strings "elements", separated by 
        a comma plus a space. The space allows word wrap in 
        spreadsheet cells.
        """
        text = (', ').join(elements)
        return text

    def _convert_from_yw(self, text, quick=False):
        """Return text, converted from yw7 markup to target format.
        
        Positional arguments:
            text -- string to convert.
        
        Optional arguments:
            quick -- bool: if True, apply a conversion mode for one-liners without formatting.
        
        Overrides the superclass method.
        """
        if text is None:
            text = ''
        return(text)


class HtmlExport(FileExport):
    """HTML file representation.
    
    Provide basid HTML templates for exporting chapters and scenes.
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

    def _get_chapterMapping(self, chId, chapterNumber):
        """Return a mapping dictionary for a chapter section. 

        Positional arguments:
            chId -- str: chapter ID.
            chapterNumber -- int: chapter number.

        Extends the superclass method.
        """
        ROMAN = [
            (1000, "M"),
            (900, "CM"),
            (500, "D"),
            (400, "CD"),
            (100, "C"),
            (90, "XC"),
            (50, "L"),
            (40, "XL"),
            (10, "X"),
            (9, "IX"),
            (5, "V"),
            (4, "IV"),
            (1, "I"),
        ]

        def number_to_roman(n):
            """Return n as a Roman number.
            
            Credit goes to the user 'Aristide' on stack overflow.
            https://stackoverflow.com/a/47713392
            """
            result = []
            for (arabic, roman) in ROMAN:
                (factor, n) = divmod(n, arabic)
                result.append(roman * factor)
                if n == 0:
                    break

            return "".join(result)

        TENS = {30: 'thirty', 40: 'forty', 50: 'fifty',
                60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninety'}
        ZERO_TO_TWENTY = (
            'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty'
        )

        def number_to_english(n):
            """Return n as a number written out in English.

            Credit goes to the user 'Hunter_71' on stack overflow.
            https://stackoverflow.com/a/51849443
            """
            if any(not x.isdigit() for x in str(n)):
                return ''

            if n <= 20:
                return ZERO_TO_TWENTY[n]

            elif n < 100 and n % 10 == 0:
                return TENS[n]

            elif n < 100:
                return f'{number_to_english(n - (n % 10))} {number_to_english(n % 10)}'

            elif n < 1000 and n % 100 == 0:
                return f'{number_to_english(n / 100)} hundred'

            elif n < 1000:
                return f'{number_to_english(n / 100)} hundred {number_to_english(n % 100)}'

            elif n < 1000000:
                return f'{number_to_english(n / 1000)} thousand {number_to_english(n % 1000)}'

            return ''

        chapterMapping = super()._get_chapterMapping(chId, chapterNumber)
        if chapterNumber:
            chapterMapping['ChNumberEnglish'] = number_to_english(chapterNumber).capitalize()
            chapterMapping['ChNumberRoman'] = number_to_roman(chapterNumber)
        else:
            chapterMapping['ChNumberEnglish'] = ''
            chapterMapping['ChNumberRoman'] = ''
        if self.chapters[chId].suppressChapterTitle:
            chapterMapping['Title'] = ''
        return chapterMapping

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
        try:
            for yw, htm in HTML_REPLACEMENTS:
                text = text.replace(yw, htm)

            # Remove highlighting, alignment,
            # strikethrough, and underline tags.
            text = re.sub('\[\/*[h|c|r|s|u]\d*\]', '', text)
        except AttributeError:
            text = ''
        return(text)

class HtmlTemplatefileExport(HtmlExport):
    """Export content or metadata from a yWriter project to a HTML file.
    
    Public methods:
        write() -- write instance variables to the export file.
    
    Read the templates from external HTML flies.
    """

    # Reset default templates.
    _fileHeader = ''
    _partTemplate = ''
    _chapterTemplate = ''
    _sceneTemplate = ''
    _sceneDivider = ''
    _fileFooter = ''

    # Define template files.
    _HTML_HEADER = 'html_header'
    _CHARACTER_TEMPLATE = 'character_template'
    _LOCATION_TEMPLATE = 'location_template'
    _ITEM_TEMPLATE = 'item_template'
    _HTML_FOOTER = 'html_footer'
    _PART_TEMPLATE = 'part_template'
    _CHAPTER_TEMPLATE = 'chapter_template'
    _CHAPTER_END_TEMPLATE = 'chapter_end_template'
    _UNUSED_CHAPTER_TEMPLATE = 'unused_chapter_template'
    _UNUSED_CHAPTER_END_TEMPLATE = 'unused_chapter_end_template'
    _NOTES_CHAPTER_TEMPLATE = 'notes_chapter_template'
    _NOTES_CHAPTER_END_TEMPLATE = 'notes_chapter_end_template'
    _TODO_CHAPTER_TEMPLATE = 'todo_chapter_template'
    _TODO_CHAPTER_END_TEMPLATE = 'todo_chapter_end_template'
    _SCENE_TEMPLATE = 'scene_template'
    _FIRST_SCENE_TEMPLATE = 'first_scene_template'
    _UNUSED_SCENE_TEMPLATE = 'unused_scene_template'
    _NOTES_SCENE_TEMPLATE = 'notes_scene_template'
    _TODO_SCENE_TEMPLATE = 'todo_scene_template'
    _SCENE_DIVIDER = 'scene_divider'
    _TEMPLATE_CHAPTER_TITLE = 'html templates'

    def __init__(self, filePath, **kwargs):
        """Read templates from files, if any.

        Positional arguments:
            filePath -- str: path to the file represented by the Novel instance.
            
        Required keyword arguments:
            template_path -- str: template directory path.
        
        Extends the superclass constructor.
        """
        super().__init__(filePath)
        templatePath = kwargs['template_path']

        # Project level.
        __, content = read_html_file(f'{templatePath}/{self._HTML_HEADER}{self.EXTENSION}')
        if content is not None:
            self._fileHeader = content
        __, content = read_html_file(f'{templatePath}/{self._CHARACTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._characterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._LOCATION_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._locationTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._ITEM_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._itemTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._HTML_FOOTER}{self.EXTENSION}')
        if content is not None:
            self._fileFooter = content

        # Chapter level.
        __, content = read_html_file(f'{templatePath}/{self._PART_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._partTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._CHAPTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._chapterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._CHAPTER_END_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._chapterEndTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._UNUSED_CHAPTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._unusedChapterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._UNUSED_CHAPTER_END_TEMPLATE}{self.EXTENSION}')

        if content is not None:
            self._unusedChapterEndTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._NOTES_CHAPTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._notesChapterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._NOTES_CHAPTER_END_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._notesChapterEndTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._TODO_CHAPTER_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._todoChapterTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._TODO_CHAPTER_END_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._todoChapterEndTemplate = content

        # Scene level.
        __, content = read_html_file(f'{templatePath}/{self._SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._sceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._FIRST_SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._firstSceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._UNUSED_SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._unusedSceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._NOTES_SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._notesSceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._TODO_SCENE_TEMPLATE}{self.EXTENSION}')
        if content is not None:
            self._todoSceneTemplate = content
        __, content = read_html_file(f'{templatePath}/{self._SCENE_DIVIDER}{self.EXTENSION}')
        if content is not None:
            self._sceneDivider = content

    def write(self):
        """Read templates from the source file, if any.

        Extends the superclass constructor.
        """
        
        def get_template(scId, title):
            """Retrieve a template from a yWriter scene.
            
            Return scene content if title matches. Otherwise return None.
            """
            if self.scenes[scId].title == title:
                content = self.scenes[scId].sceneContent 
            else: 
                content = None 
            return content
        
        # Find template chapter.
        for chId in self.chapters:
            if not self.chapters[chId].isUnused:
                continue
                
            if self.chapters[chId].title != self._TEMPLATE_CHAPTER_TITLE:
                continue
                     
            for scId in self.chapters[chId].srtScenes:
        
                # Project level.
                content = get_template(scId, self._HTML_HEADER)
                if content is not None:
                    self._fileHeader = content
                content = get_template(scId, self._CHARACTER_TEMPLATE)
                if content is not None:
                    self._characterTemplate = content
                content = get_template(scId, self._LOCATION_TEMPLATE)
                if content is not None:
                    self._locationTemplate = content
                content = get_template(scId, self._ITEM_TEMPLATE)
                if content is not None:
                    self._itemTemplate = content
                content = get_template(scId, self._HTML_FOOTER)
                if content is not None:
                    self._fileFooter = content
        
                # Chapter level.
        
                content = get_template(scId, self._PART_TEMPLATE)
                if content is not None:
                    self._partTemplate = content
                content = get_template(scId, self._CHAPTER_TEMPLATE)
                if content is not None:
                    self._chapterTemplate = content
                content = get_template(scId, self._CHAPTER_END_TEMPLATE)
                if content is not None:
                    self._chapterEndTemplate = content
                content = get_template(scId, self._UNUSED_CHAPTER_TEMPLATE)
                if content is not None:
                    self._unusedChapterTemplate = content
                content = get_template(scId, self._UNUSED_CHAPTER_END_TEMPLATE)
                if content is not None:
                    self._unusedChapterEndTemplate = content
                content = get_template(scId, self._NOTES_CHAPTER_TEMPLATE)
                if content is not None:
                    self._notesChapterTemplate = content
                content = get_template(scId, self._NOTES_CHAPTER_END_TEMPLATE)
                if content is not None:
                    self._notesChapterEndTemplate = content
                content = get_template(scId, self._TODO_CHAPTER_TEMPLATE)
                if content is not None:
                    self._todoChapterTemplate = content
                content = get_template(scId, self._TODO_CHAPTER_END_TEMPLATE)
                if content is not None:
                    self._todoChapterEndTemplate = content
        
                # Scene level.
                content = get_template(scId, self._SCENE_TEMPLATE)
                if content is not None:
                    self._sceneTemplate = content
                content = get_template(scId, self._FIRST_SCENE_TEMPLATE)
                if content is not None:
                    self._firstSceneTemplate = content
                content = get_template(scId, self._UNUSED_SCENE_TEMPLATE)
                if content is not None:
                    self._unusedSceneTemplate = content
                content = get_template(scId, self._NOTES_SCENE_TEMPLATE)
                if content is not None:
                    self._notesSceneTemplate = content
                content = get_template(scId, self._TODO_SCENE_TEMPLATE)
                if content is not None:
                    self._todoSceneTemplate = content
                content = get_template(scId, self._SCENE_DIVIDER)
                if content is not None:
                    self._sceneDivider = content
        return (super().write())


class ExportAnyTargetFactory(FileFactory):
    """A factory class that instantiates an export target file object."""

    def make_file_objects(self, sourcePath, **kwargs):
        """Instantiate a target object for conversion to any format.

        Positional arguments:
            sourcePath -- str: path to the source file to convert.

        Optional arguments:
            suffix -- str: an indicator for the target file type.

        Required keyword arguments: 
            suffix -- str: target file name suffix.

        Return a tuple with three elements:
        - A message beginning with the ERROR constant in case of error
        - sourceFile: None
        - targetFile: a FileExport subclass instance, or None in case of error 
        """
        fileName, __ = os.path.splitext(sourcePath)
        suffix = kwargs['suffix']
        for fileClass in self._fileClasses:
            if suffix is None:
                suffix = ''
            targetFile = fileClass(f'{fileName}{suffix}{fileClass.EXTENSION}', **kwargs)
            return 'Target object created.', None, targetFile

        return f'{ERROR}File type of "{os.path.normpath(sourcePath)}" not supported.', None, None

class HtmlExporter(YwCnvFf):
    """A converter class for html export.

    Class constants:
        EXPORT_SOURCE_CLASSES -- List of YwFile subclasses from which can be exported.
        EXPORT_TARGET_CLASSES -- List of FileExport subclasses to which export is possible.
    """
    EXPORT_SOURCE_CLASSES = [Yw7File]
    EXPORT_TARGET_CLASSES = [HtmlTemplatefileExport]

    def __init__(self):
        """Extends the superclass constructor.

        Delegate the exportTargetFactory to a project
        specific class that accepts all suffixes.
        Extends the superclass constructor.
        """
        super().__init__()
        self.exportTargetFactory = ExportAnyTargetFactory(self.EXPORT_TARGET_CLASSES)




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
