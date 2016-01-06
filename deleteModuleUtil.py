import logging
import sys, traceback
import config
import os
import shutil

# Logging definition
log = config.Log
logging.basicConfig(filename=log.flog, format=log.format, level=log.level)
c = config.ImportModule()

'''
    This function delete the Module entry from the dictionary file. This function also perform a check if the module
    exist before any action. Return value are:
        0 : Error generic
        1 : OK Module info removed
        2 : Error Module info does not exist
'''

def deleteDictionaryEntry(module):
    logging.debug('Deleting module '+module+' from dictionary')
    try:
        # Open the dictionary file and read it as dic
        fdic = open(c.configFile,'r')
        dic = eval(fdic.read())
        fdic.close()

        # Check if the Module to delete exist in the dictionary
        if module not in dic:
            logging.warning('Warning, module '+ module+' does not exist in dictionary')
            return 2

        # Delete the Module entry from dictionary
        dic.pop(module,None)

        # Write back to the original file
        fdic = open(c.configFile,'w')
        fdic.write(str(dic))
        fdic.close()

        logging.debug('Dictionary successfully purged')
        return 1
    except Exception:
        logging.exception('Error while purging dictionary for module '+module)
        raise

'''
    This function modify the RESTServer.py file deleting the import line for module to purge
'''
def modifyRESTServer(module):
    logging.debug('Modifying the RESTServer.py file')
    try:
        # Open the RESTServer.py file in a list and remove the import line
        lines = [line.rstrip('\n') for line in open('RESTServer.py')]

        # Open the RESTServer.py in write mode and write back the file without the imported line
        fout = open('RESTServer.py','w')
        for line in lines:
            if not((line == 'import '+module) or (line == 'sys.path.append ("Modules/'+module+'")')):
                fout.write(line+'\n')
        fout.close()

        logging.debug('RESTServer.py file correctly modified')
        return 1
    except Exception:
        tb = sys.exc_info()
        logging.error('Error while modifying the RESTServer.py file for module '+module)
        logging.error('Error : '+Exception.with_traceback(tb))
        return 0


def deleteModuleFile(module):
    logging.debug('Deleting the module file from temp dir to Modules dir, for module '+module)
    rootDir=os.path.join('Modules/',module)
    try:
        shutil.rmtree(rootDir)

        logging.debug('Module file completle removed')
        return 1
    except Exception:
        logging.error('Error while deleting module file for module '+module)
        logging.error('Error : ',str(Exception.with_traceback()))
        return 0


def deleteModuleUtil(module):
    logging.info('Deleting module '+module)

    #STEP 1 : Purge the dictionary entry
    sys.stdout.write('{:100s}'.format('Purge Dictionary'))
    if(deleteDictionaryEntry(module)):
        sys.stdout.write('{:100s}[{:2s}]\n'.format(' ','OK'))
    else:
        sys.stdout.write('{:100s}[{:2s}]\n'.format(' ','KO'))
        exit(1)

    #STEP 2: Modify the RESTServer.py file
    sys.stdout.write('{:100s}'.format('Modifying the RESTServer.py file'))
    if(modifyRESTServer(module)):
        sys.stdout.write('{:100s}[{:2s}]\n'.format(' ','OK'))
    else:
        sys.stdout.write('{:100s}[{:2s}]\n'.format(' ','KO'))
        exit(1)

    #STEP 3: Delete Module File from Modules directory
    sys.stdout.write('{:100s}'.format('Deleting module file'))
    if(deleteModuleFile(module)):
        sys.stdout.write('{:100s}[{:2s}]\n'.format(' ','OK'))
    else:
        sys.stdout.write('{:100s}[{:2s}]\n'.format(' ','KO'))
        exit(1)

if (__name__ == '__main__'):
    deleteModuleUtil(sys.argv[1])