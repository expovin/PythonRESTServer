import argparse
import config
import os
import sys
import importModuleUtil
import importModuleUtil
import deleteModuleUtil


c = config.Cash()
'''
    RESTServerHelper [command] [Args]:

        Commands:
            import : Import a Module in RESTServer, need to specify the module file name
            list   : List all module already imported

'''



def getImportedModules():
    fmod = open(os.path.join(c.fpath,'importedModule.config'),'r')
    mod = eval(fmod.read())
    fmod.close()
    return mod


if(__name__=='__main__'):

    parser = argparse.ArgumentParser()
    parser.add_argument('command' , nargs='+', help='Command should be import, list or export')
    args = parser.parse_args()

    if(len(sys.argv)<2):
        parser.print_help()
    else:

        if(args.command == 'import'):
            importModuleUtil.importModuleUtil(sys.argv[2])

        if(args.command == 'list'):
            print(getImportedModules())

        if(args.command == 'delete'):
            deleteModuleUtil.deleteModuleUtil(sys.argv[2])


