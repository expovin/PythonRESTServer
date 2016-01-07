import zipfile,os.path
import sys
import os
import config
import shutil
import datetime
import logging
import argparse
import urllib.request
import time

c = config.ImportModule()
i = config.importer()
modules = []
ModProp = {}
importedModules = {}



# Logging definition
log=config.Log
logging.basicConfig(filename=log.flog, format=log.format, level=log.level)


'''
    This function download the TarBall Module file directly from GitHub
'''
def downloadFromGitHub(moduleName):
    logging.debug('Downloading Module ',moduleName)
    try:
        if not  os.path.exists('cash/Modules/'):                                          # Create the directory if not exist yet
            os.makedirs('cash/Modules/')
        sys.stdout.write('{:100s}'.format('Downloading Module, Please wait ... '))
        url = 'https://github.com/expovin/'+moduleName+'/archive/master.zip'
        urllib.request.urlretrieve(url, 'cash/Modules/'+moduleName+'-master.zip')
        sys.stdout.write('[{:2s}]\n'.format('OK'))
        return 1
    except Exception:
        logging.exception('Error while downloading the Module')
        raise


'''
    This function get as input parameter the source_filename (Module zip file) and the destination dir to unzip it.
    Return 1 if no error occurs, else return 0
'''
def unzip(source_filename, dest_dir):
    logging.debug('Unzip Modules'+source_filename+' in '+ dest_dir)
    try:
        if not  os.path.exists(i.tmpPath):                                      # Create the directory if not exist yet
            os.makedirs(i.tmpPath)
        zip_ref = zipfile.ZipFile(source_filename, 'r')
        zip_ref.extractall(dest_dir)
        zip_ref.close()
        modules.append(source_filename.split(".")[0])                           # Remove the file zip extension in the Folder name
        logging.debug('Unzip Modules'+source_filename+' successful')
        return 1
    except Exception:
        logging.exception('Error to unzip module'+source_filename)
        raise


'''
    This function check if the module.info file exist and it's valid. Add the imported date as new value and write
    back to the file the new value. This module also list on the standard output the file content. Return a list of 2
    values:
        The first value is the return code (1: OK, 0: Fail).
        The second value is the file content as dictionary

    @TODO : Verify if the mandatory fields exist
'''
def checkModuleProperties(Module):
    logging.debug('Check the module.info file content for module :'+Module)
    try:
        #Open the original file and read the content as dict
        fp = open(os.path.join(os.path.join(i.tmpPath,Module),'module.info'),'r')
        ModProp = eval(fp.read())
        fp.close()

        #Adding the current date as new value
        ModProp.update({'Imported Date':str(datetime.date.today())})

        #Write back to the same file the new value
        fp = open(os.path.join(os.path.join(i.tmpPath,Module),'module.info'),'w')
        fp.write(str(ModProp))
        fp.close()

        #List to the stdout the File content
        for p in ModProp:
            print('    {:40s} :'.format(p),ModProp[p])

        logging.debug('File module.info checked and modified correctly, for module :'+Module)
        return [1, ModProp]
    except Exception:
        logging.exception('Error while checking the module.info file for module :'+Module)
        raise

'''
    This function open the application.conf file and add the url prefix for the Methods call, then write them back to the
    original file. Return 1 as OK 0 as Fail.

    @TODO: Need to work as String and add also the Prefix to the Function call.
           For a better robustness, cross check with the module existence
'''
def checkMethodList(Module,Prefix):
    logging.debug('Check the application.conf file content for module :'+Module)
    try:
        #Open, read the file as dict. Modify the dict adding the Prefix
        fp = open(os.path.join(os.path.join(i.tmpPath,Module),'application.conf'),'r')
        cont = fp.read()
        cont = cont.replace('r/','r/'+Prefix+'/')
        fp.close()

        #Write back the new value to the original file
        fp = open(os.path.join(os.path.join(i.tmpPath,Module),'application.conf'),'w')
        fp.write(cont)
        fp.close()

        logging.debug('Check methods list verified and prefix added correctly for module :'+Module)
        return 1
    except Exception:
        logging.exception('Error while checking the Methods list for module '+Module)
        raise

'''
    This function check if the Module already exist in the RESTServer. The check is made by reading the dictionary file.
    This function return a list:
        The first value is the return code (1: OK, 0: Failed
        The second value is the file content as dictionary

    If the dictionary file does not exist yet, the function consider this module as the first and will create the file

    @TODO: This module will implement for existing module some check un the last imported date or version number to
           enable the upgrade to a newer Module version
'''
def checkIfAlreadyImported(Module):
    logging.debug('Check if the Module '+Module+' already exist')
    try:
        #Open the dictionary file and read all the imported modules
        fr = open(c.configFile,'r')
        importedModules = eval(fr.read())
        fr.close()

        #Check if the Module already exist in the dictionary. Here will be implemented the version check
        if Module in importedModules:
            logging.error('Module already exist in the dictionary. No futher action will be take a place')
            return [0, {}]

        logging.debug('Check of existence done. The module does not exist yet, will be imported')
        return [1, importedModules]
    except FileNotFoundError:
        logging.exception('Dictionary file does not exist yet. This is the first module, the dictionary will be created')
        raise

'''
    This function move the unzipped file from the temp folder to the destination folder (Modules) performing the real
    Module import. The return code is 1 : OK or 0 : Failed
    This function also print on the stdout the file moved
'''
def moveModuleFile(Modules):
    logging.debug('Moving the module file from temp dir to Modules dir, for module '+Modules)
    rootDir=os.path.join(i.tmpPath,Modules)
    try:
        for dirName, subdirList, fileList in os.walk(rootDir):
            destDir = dirName.replace('tmp','Modules')
            destDir = destDir.replace('-master','')
            os.makedirs(destDir)
            sys.stdout.write('{:60s} [{:s}]\n'.format('Importing Directory',destDir))
            for fname in fileList:
                shutil.move(os.path.join(dirName,fname), os.path.join(destDir,fname))
                sys.stdout.write('{:60s} [{:s}]\n'.format('Importing file',fname))

        logging.debug('Moving completed with no error')
        return 1
    except Exception:
        logging.exception('Error moving file modules for module '+Modules)
        raise

'''
    This function modify the RESTServer.py file adding the line for the imported module and the path in the PYTHONPATH
    system variable. The module performs also a backup copy of the original file and put it in the rollback folder with
    a timestamp as file name suffix. The suffix will be saved in the dictionary for further use. The module return
    a list of two values:
        The first value is the return code (1: OK, 0: Failed)
        The second value is the rollback file name to save in the module properties in the dictionary
'''
def modifyRESTServer(Module):
    logging.debug('Performing the RESTServer file modification for module '+Module)
    i = config.importer()
    try:
        suffix=str(datetime.datetime.now())                                      # Get the timestamp as suffix
        suffix = suffix.replace(':','')                                          # Just remove unsupported character
        suffix = suffix.replace(' ','')                                          # for file name
        rollbackName = 'RESTServer_'+suffix+'.py'

        if not  os.path.exists(i.rollbackPath):                                  # Create the directory if not exist yet
            os.makedirs(i.rollbackPath)

        shutil.move('RESTServer.py',os.path.join(i.rollbackPath,rollbackName))   # Moving the original file to rollback folder

        #fin = open(os.path.join(i.rollbackPath,rollbackName),'r')               # Open the original file
        fout = open('RESTServer.py','w')                                         # Open the new file
        fout.write('import sys\n')                                               # To be sure sys is defined before use it
        fout.write('sys.path.append ("Modules/'+Module+'")\n')                   # Add the new path as PYTHONPATH
        fout.write('import '+Module+' \n')                                       # Write the new import line in the new file

        # Open the RESTServer.py file in a list and remove the import line
        lines = [line.rstrip('\n') for line in open(os.path.join(i.rollbackPath,rollbackName))]

        for line in lines:
            if(line != 'import sys'):
                fout.write(line+'\n')

        fout.close()

        #Adding the new Module in the PYTHONPATH sysvar
        sys.path.append('Modules/'+Module)

        logging.debug('Modification of the RESTServer.py file done correctly. The original file was saved as '+rollbackName)
        return [1, rollbackName]
    except Exception:
        logging.exception('Error while modifying the RESTServer.py file for module '+Module)
        raise


'''
    This function update the RESTServer dictionary with all the information about the imported module. The input params
    are:
        dictionary   - The dictionary file content (cash/importedModule.config) to update
        ModProp      - The application.conf content file to copy into RESTServer dictionary
        rollbackName - The RESTServer.py file state before the import. This info will be added to the module info

    The function perform the RESTServer dictionary update with all the module info (coming from the application.conf file)
    Also the rollbackName info will be added for rollback the operation
    The function return 1: OK, 0: Failed
'''
def updateDictionary(dictionary,ModProp,rollbackName):
    logging.debug('Performing the dictionary update. ModProb : '+str(ModProp)+ ' rollbackName : '+rollbackName)
    try:
        Properties={}                                                 #A temp dictionary variable
        ModProp.update({'Rollback Suffix':rollbackName})              #Adding the rollbackName information
        Properties.update({ModProp['Name']:ModProp})
        dictionary.update(Properties)                                 #Perform the dictionary update

        #Write dictionary back to the file
        fw = open(c.configFile,'w')
        fw.write(str(dictionary))
        fw.close()

        logging.debug('Update dictionary performed correctly')
        return 1
    except Exception:
        logging.exception('Error to update file dictionary')
        raise


'''
    This function call all the above to perform a right Module import.
'''
def importModuleUtil(zipFile):

    logging.info('Perform import file '+str(zipFile))
    #STEP 1: Unzip the Module file in a temp directory
    sys.stdout.write('{:100s}'.format('Extracting module files ',zipFile))
    if(unzip(zipFile,i.tmpPath)):
        sys.stdout.write('[{:2s}]\n'.format('OK'))
    else:
        sys.stdout.write('[{:2s}]\n'.format('KO'))
        exit(1)

    if "/" in zipFile:
        ModuleName = zipFile.split("/")[-1:][0]
    if "\\" in ModuleName:
        ModuleName = ModuleName.split("\\")[-1:][0]

    #STEP 2: Check module properties
    sys.stdout.write('{:100s}[{:8s}]\n'.format('Check Module properties ','PROGRESS'))
    rc , ModProp = checkModuleProperties(ModuleName[:-4])
    if(rc):
        sys.stdout.write('{:100s}[{:2s}]\n'.format(' ','OK'))
    else:
        sys.stdout.write('{:100s}[{:2s}]\n'.format(' ','KO'))
        exit(1)


    #STEP 3: Check if the module already exist in the dictionery
    sys.stdout.write('{:100s}'.format('Checking if Module already exist'))
    rc, dictionary = checkIfAlreadyImported(ModProp['Name'])
    if(rc):
        sys.stdout.write('[{:2s}]\n'.format('OK'))
    else:
        sys.stdout.write('[{:2s}]\n'.format('KO'))
        print('Module already exist. Please delete before re import')
        exit(1)


    #STEP 4: Check Methods list
    sys.stdout.write('{:100s}'.format('Checking methods list'))
    if(checkMethodList(ModuleName[:-4],ModProp['Prefix'])):
        sys.stdout.write('[{:2s}]\n'.format('OK'))
    else:
        sys.stdout.write('[{:2s}]\n'.format('KO'))
        exit(1)

    #STEP 5: Moving the module file from temp folder to target folder
    if(moveModuleFile(ModuleName[:-4])):
        sys.stdout.write('[{:2s}]\n'.format('OK'))
    else:
        sys.stdout.write('[{:2s}]\n'.format('KO'))
        exit(1)

    #STEP 6 : Modify the RESTServer.py file
    sys.stdout.write('{:100s}'.format('Modify RESTServer File'))
    rc, rollbackName = modifyRESTServer(ModProp['Name'])
    if(rc):
        sys.stdout.write('[{:2s}]\n'.format('OK'))
    else:
        sys.stdout.write('[{:2s}]\n'.format('KO'))
        exit(1)


    #STEP 7 : Update RESTServer dictionary
    sys.stdout.write('{:100s}'.format('Updating dictionary'))
    if(updateDictionary(dictionary,ModProp,rollbackName )):
        sys.stdout.write('[{:2s}]\n'.format('OK'))
    else:
        sys.stdout.write('[{:2s}]\n'.format('KO'))
        exit(1)


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


if(__name__=="__main__"):
    logging.info('Start Service import')

    parser = argparse.ArgumentParser()
    #parser.add_argument('ModuleName' , help='Name of the module (or local file) to import')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="Local full path ModuleFile.zip")
    group.add_argument("-w", "--web", help="get Tarball from WEB")

    args = parser.parse_args()

    if(args.web):
        if(downloadFromGitHub(sys.argv[2])):
             importModuleUtil('cash/Modules/'+sys.argv[2]+'-master.zip')

    if(args.file):
        importModuleUtil(sys.argv[2])