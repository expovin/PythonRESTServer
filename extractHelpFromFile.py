import config
import os


def readFile (FileName):
    inFile = open(FileName,'r')
    buffer={}
    isComment=0
    isHeader=0
    methodName=''
    methodDesc=''
    header={'Header':'[]'}
    funcContainer={'Functions':{}}
    headerContent=[]
    Desc=[]

    for line in inFile:
        if line.startswith("'''"):    #Trovato commento
            isComment  = not isComment

        if(isComment) and (line != '\'\'\'\n'):
            try:
                methodName , Meta = line.split(":")
                functionName, Method, returnFormat = Meta.split(" - ")
                returnFormat = returnFormat[:-1]
                methodName = methodName.strip()

            except:
                Name = FileName.split("/")[-1]
                if(Name.startswith(line[:-1].strip())):
                    isHeader=1
                else:
                    if(isHeader):
                        headerContent.append(line[:-1].strip())
                    else:
                        Desc.append(line[:-1].strip())

        else:
            if(isHeader):
                header['Header']=headerContent
                buffer.update(header)
            else:
                try:
                    if functionName not in funcContainer['Functions']:
                        Func={functionName:{'Method':methodName,'Call':Method,'Return Format':returnFormat,'Description':Desc}}
                        funcContainer['Functions'].update(Func)
                        buffer.update(funcContainer)
                        Desc=[]
                except:
                    continue
            #if(not isHeader):
                #Desc=[]
            isHeader=0


    inFile.close()
    return buffer

def buildHelpPage(FileName,host,prefix,index):
    c = config.makeHtmlHelpFile()

    if (index):
        methodList = index
        NomeModulo = 'Index'
    else:
        tmp = FileName.split("/")[-1]
        NomeModulo=tmp[:-3]
        methodList = readFile(FileName)

    fout = open(os.path.join(c.outPath,NomeModulo+'.html'),'w')

    fin = open(os.path.join(c.fpath,'help0TempFile.preHtml'))
    inBuffer = fin.read()
    fin.close()

    outBuffer = inBuffer.replace('<%NomeModulo%>',NomeModulo)

    fout.write(outBuffer)

    fin = open(os.path.join(c.fpath,'help1TempFile.preHtml'))
    inBuffer = fin.read()
    fin.close()
    for func in methodList['Functions']:
        outBuffer = inBuffer.replace('<%NomeFunzione%>',func)
        fout.write(outBuffer)

    fin = open(os.path.join(c.fpath,'help2TempFile.preHtml'))
    inBuffer = fin.read()
    fin.close()
    outBuffer = inBuffer.replace('<%NomeModulo%>',NomeModulo)
    buff=''
    for line in methodList['Header']:
        buff = buff + line
    outBuffer = outBuffer.replace('<%DescModulo%>',buff)
    fout.write(outBuffer)

    fin = open(os.path.join(c.fpath,'help3TempFile.preHtml'))
    inBuffer = fin.read()
    fin.close()
    for func in methodList['Functions']:
        outBuffer = inBuffer.replace('<%NomeFunzione%>',func)
        outBuffer = outBuffer.replace('<%Method%>',methodList['Functions'][func]['Method'])
        tmp = methodList['Functions'][func]['Call'].replace('<','&lt;')
        tmp = tmp.replace('>','&gt;')
        outBuffer = outBuffer.replace('<%Call%>','/'+prefix+tmp)
        exCall = makeExampleCall('/'+prefix+methodList['Functions'][func]['Call'])
        outBuffer = outBuffer.replace('<%ReturnFormat%>',methodList['Functions'][func]['Return Format'])
        outBuffer = outBuffer.replace('<%Href%>','http://'+host+exCall)
        buf=''
        for line in methodList['Functions'][func]['Description']:
            buf = buf + line
        outBuffer = outBuffer.replace('<%DescFunzione%>',buf)

        fout.write(outBuffer)


    fin = open(os.path.join(c.fpath,'help4TempFile.preHtml'))
    inBuffer = fin.read()
    fin.close()
    fout.write(inBuffer)

    fout.close()

def makeExampleCall(call):
    ex = config.reqExample()
    for v in ex.Example['ES1']:
        call = call.replace('<'+v+'>',ex.Example['ES1'][v])
    return call


if(__name__=='__main__'):

    rc = buildHelpPage('RESTServer.py','localhost:8880')
    print(rc)

