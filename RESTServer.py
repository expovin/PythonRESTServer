import sys
sys.path.append ("Modules/KMLRegionRetriver")
import KMLRegionRetriver 


import tornado.escape
import tornado.ioloop
import tornado.web
import logging
import config

import RSCmdUtil as H
import extractHelpFromFile
import os
import socket

log=config.Log
logging.basicConfig(filename=log.flog, format=log.format, level=log.level)

'''
    RESTServer
    This service enable a full REST Server API which allow to call the API via REST protocol. By default
    all file having extensions kml in "/KMLFiles" directory will be read
'''


'''
    GET:info - info - JSON
    Just return some info about the RESTServer such as version, author and last build date
'''

class VersionHandler(tornado.web.RequestHandler):
    def get(self):
        i=config.Info
        response = { 'author':i.author,
                     'contact':i.contact,
                     'last build':i.build,
                     'version': i.version
                   }
        self.write(response)

'''
    GET:getImportedModules - getImportedModules - JSON
    This method return the list of all imported modules
'''

class getImportedModules(tornado.web.RequestHandler):
    def get(self):
        response = { 'Method':'getImportedModules',
                     'Modules':H.getImportedModules()
                   }
        self.write(response)

class getRESTServerHelp(tornado.web.RequestHandler):
    def get(self,page):
        c = config.makeHtmlHelpFile()
        Nome = sys.argv[0].split("/")[-1]
        htmlFileName = os.path.join(c.outPath,Nome[:-3]+'.html')
        fh = open(htmlFileName,'r')
        #self.write(fh.read())
        self.render(os.path.join(c.outPath,page))





c = config.RESTServer
i = config.Cash

application = tornado.web.Application([
    (r"/info", VersionHandler),
    (r"/getImportedModules", getImportedModules),
    (r"/help/([0-9a-zA-Z.-]+)", getRESTServerHelp)
])

try:
    fapp = open(os.path.join(i.fpath,'importedModule.config'),'r')
    app = eval(fapp.read())
    fapp.close()
    for a in app:
        fapp = open(os.path.join(os.path.join('Modules',a),'application.conf'),'r')
        appDict = {}
        buff = fapp.read()
        appDict = eval(buff)

        for l in appDict['Application']:
            prefApp = ('/'+app[a]['Prefix']+l[0],l[1])
            application.add_handlers(r".*$",[prefApp,])

except FileNotFoundError:
    print('No Module loaded')


def startTornado():
    logging.info('Start REST Server on port '+str(c.listenPort))
    application.listen(c.listenPort)
    tornado.ioloop.IOLoop.instance().start()

def stopTornado():
    tornado.ioloop.IOLoop.instance().stop()

if __name__ == "__main__":
    bufferIndex = {'Header':'Test','Functions':{}}
    host = socket.gethostname()+':'+str(c.listenPort)
    extractHelpFromFile.buildHelpPage(sys.argv[0],host,'',{})
    fmod = open(os.path.join('cash','importedModule.config'),'r')
    mod = eval(fmod.read())
    for m in mod:
        buff = extractHelpFromFile.readFile('Modules/'+m+'/'+m+'.py')
        tmp = {m:{'Call':m+'.html','Method':'GET/POST','Return Format':'JSON','Description':buff['Header']}}
        bufferIndex['Functions'].update(tmp)
        extractHelpFromFile.buildHelpPage('Modules/'+m+'/'+m+'.py',host,mod[m]['Prefix'],{})

    extractHelpFromFile.buildHelpPage('',host,'help/',bufferIndex)

    if(sys.argv[1] == 'start'):
        startTornado()

    if(sys.argv[1] == 'stop'):
        stopTornado()

    print('Usage : ',sys.argv[0],' [start | stop]')
