""" Build python scripts for the PyWriter distributions.
        
In order to distribute single scripts without dependencies, 
this script "inlines" all modules imported from the pywriter package.

For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
import os


def inline_module(file, package, text, processedModules):
    with open(file, 'r', encoding='utf-8') as f:
        print('Processing "' + file + '"...')
        lines = f.readlines()
        inSuppressedComment = False
        inHeader = True
        # document parsing always starts in the header
        for line in lines:
            if (inHeader) and line.count('"""') == 1:
                # Beginning or end of a docstring
                if package in file:
                    # This is not the root script
                    # so suppress the module's docstring
                    if inSuppressedComment:
                        # docstring ends
                        inSuppressedComment = False
                        inHeader = False
                    else:
                        # docstring begins
                        inSuppressedComment = True
                else:
                    text = text + line
            elif not inSuppressedComment:
                if package in file:
                    if 'main()' in line:
                        return(text)

                    if '__main__' in line:
                        return(text)

                if 'import' in line:
                    importModule = re.match('from (.+?) import.+', line)
                    if (importModule is not None) and (package in importModule.group(1)):
                        moduleName = '../../PyWriter/src/' + re.sub(
                            '\.', '\/', importModule.group(1))
                        if not (moduleName in processedModules):
                            processedModules.append(moduleName)
                            text = inline_module(
                                moduleName + '.py', package, text, processedModules)
                    else:
                        moduleName = line.replace('import ', '').rstrip()
                        if not (moduleName in processedModules):
                            processedModules.append(moduleName)
                            text = text + line
                else:
                    text = text + line
        return(text)


def run(sourceFile, targetFile, package):
    try:
        os.remove(targetFile)
    except:
        pass
    text = ''
    processedModules = []
    text = (inline_module(sourceFile, package, text, processedModules))
    with open(targetFile, 'w', encoding='utf-8') as f:
        print('Writing "' + targetFile + '"...\n')
        f.write(text)


if __name__ == '__main__':
    pass
