# PythonRESTServer
Package v 0.6

GENERAL DESCRIPTION

PythonRESTServer (or PRS) is a framework which allow the publication of any Python code as REST Service. PRS doesn't offer a full end user functions, instead share a number of common services for a REST Server such as logging, configuration, documentation as well as some basic facilities to import new modules. A module is a Python project developed following specific guidelines in order to be imported into PRS. 

PREREQUISITE

The prerequisite for PRS are
   Python 3.x  --> https://www.python.org/download/releases/3.4.0/
   
   Tornado 4.3 --> http://www.tornadoweb.org/en/stable/

INSTALLATION

To install PRS just download the project and unzip it in an appropriate folder. PRS is designed to work on both Windows and UNIX-like OS.
 To start PRS cd into the Project main folder and execute RESTServer.py start
 To stop the service just kill the related process

INSTALL A MODULE

To install a module use the InstallModule.py utility. You have two possibilities
  1) Download the module zip file and run the install utility pointing the file. InstallModule.py -f <localfile.zip>
  
  2) Tell to installer to download the module from the network. InstallModule.py -w <ModuleName>

Eg. To install the KMLRegionRetriver module, just type
    InstallModule.py -w KMLRegionRetriver

UTILITY 

RSCmdUtil.py : Call the importModuleUtil.py and deleteModuleUtil.py to import, verify and delete Modules
importModuleUtil.py : Import the Modules from local disk or from the network
deleteModuleUtil.py : Delete the Modules

KNOW ISSUE AND LIMITS

Because the is the very first shareable versions, a number of know limits will be addressed in further release such as

  1) Implement a correct stop service function
  
  2) Improve stability and check during the import (version and Prefix)
  
  3) Centralize the different utility (ImportModule, deleteModule) in just one script file
  
  4) Implement the upgrade based on the Module version
  
  5) Implement log rotation
  

For a complete and more up to date version of improvements refer to issues section
