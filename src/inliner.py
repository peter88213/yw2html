""" Build python scripts for the PyWriter based distributions.
        
In order to distribute single scripts without dependencies, 
this script "inlines" all modules imported from the pywriter package.

For further information see https://github.com/peter88213/PyWriter
Published under the MIT License (https://opensource.org/licenses/mit-license.php)
"""
import re
import os
from shutil import copyfile


def inline_module(file, package, packagePath, text, processedModules, copyPyWriter):
    with open(file, 'r', encoding='utf-8') as f:
        print(f'Processing "{file}"...')
        if copyPyWriter:
            target = file.replace('/../PyWriter', '')
            targetDir = os.path.split(target)[0]
            os.makedirs(targetDir, exist_ok=True)
            if not os.path.isfile(target):
                copyfile(file, target)
        lines = f.readlines()
        inSuppressedComment = False
        inHeader = True
        # document parsing always starts in the header
        for line in lines:
            if line.startswith('# do_not_inline'):
                break

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
                    text = f'{text}{line}'
            elif not inSuppressedComment:
                if package in file:
                    if 'main()' in line:
                        return(text)
                    if '__main__' in line:
                        return(text)
                if 'import' in line:
                    importModule = re.match('from (.+?) import.+', line)
                    if (importModule is not None) and (package in importModule.group(1)):
                        packageName = re.sub('\.', '\/', importModule.group(1))
                        moduleName = f'{packagePath}{packageName}'
                        if not (moduleName in processedModules):
                            processedModules.append(moduleName)
                            text = inline_module(
                                f'{moduleName}.py', package, packagePath, text, processedModules, copyPyWriter)
                    elif line.lstrip().startswith('import'):
                        moduleName = line.replace('import ', '').rstrip()
                        if not (moduleName in processedModules):
                            processedModules.append(moduleName)
                            text = f'{text}{line}'
                    else:
                        text = f'{text}{line}'
                else:
                    text = f'{text}{line}'
        return(text)


def run(sourceFile, targetFile, package, packagePath, copyPyWriter=False):
    text = ''
    processedModules = []
    text = inline_module(sourceFile, package, packagePath, text, processedModules, copyPyWriter)
    with open(targetFile, 'w', encoding='utf-8') as f:
        print(f'Writing "{targetFile}"...\n')
        f.write(text)

