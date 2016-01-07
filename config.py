import logging
import os


class Info():
    author='Vincenzo Esposito'
    contact='ves@qlik.com'
    version='1.0'
    build='22/12/2015'

class ImportModule():
    configFile = os.path.join('cash','importedModule.config')

class FilePath():
    fpath = 'KMLFile'
    KMLext = '.kml'


class Log():
    fpath='logs'
    file='General.log'
    flog=os.path.join(fpath,file)
    format='%(asctime)s\t%(module)s:%(funcName)s\t%(levelname)s\t%(lineno)d\t%(message)s'
    level=logging.INFO

class KMLFile():
    regionNameTAG='name'

class JSONFile():
    mostWesternInitPoint=+180.0
    mostEasterInitPoint=180.0
    mostNorthernInitPoint=-90.0
    mostSouthernInitPoint=90.0

class RESTServer():
    listenPort=8880
    genericFileName='([0-9a-zA-Z.-]+)'
    genericCoords='([0-9,.-]+)'

class Cash():
    fpath='cash'
    file='point.json'
    fcash=os.path.join(fpath,file)
    maxkey=100000

class ParseCSVforCoords():
    fpath='CSV'
    file=''

class makeHtmlHelpFile():
    fpath=os.path.join('cash','__template__')
    outPath='help'

class importer():
    tmpPath='tmp'
    modPath='Modules'
    rollbackPath = os.path.join('cash','rollback')


class reqExample():
    Example = {'ES1':
                   {
                       'KMLFileName':'regioni.kml',
                       'Region':'Lombardia',
                       'Coords':'45.002875,11.504791'
                   }

               }


if(__name__=='__main__'):
    c = Config()
    print( c.Var2)

