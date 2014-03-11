#!/usr/bin/env python
import os
import sys
#pip install configlib
from configlib import getConfig,OptionParser
#kludge fix for macports issue: https://trac.macports.org/ticket/31891
sys.path.reverse()
from gensim import corpora, models, similarities
import re
import netaddr
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.ERROR)

apachequotedfieldsre=re.compile(r'''"(.*?)"''')     #get fields delimited by ""

def isIP(ip):
    try:
        if netaddr.valid_ipv4(ip,flags=netaddr.INET_PTON) or netaddr.valid_ipv6(ip,flags=netaddr.INET_PTON):
            return True
        else:
            return False
    except:
        return False
    
def main():
    dictionary=corpora.Dictionary()
    stoplist=set('- get http/1.0 http/1.1 302 200 404 403'.split())
    tokenDelimiters="/", r'\\', r'\\'," ","&","?"
    splitPattern = '|'.join(map(re.escape, tokenDelimiters))
    
    if not os.path.exists(options.dictionaryFile):
        #create a dictionary (id/word mapping) of all words
        texts = [[word for word in re.split(splitPattern,line.decode('ascii','ignore').lower()) if word not in stoplist]for line in open(options.goodLogFile).readlines()]
        texts += [[word for word in re.split(splitPattern,line.decode('ascii','ignore').lower()) if word not in stoplist]for line in open(options.badLogFile).readlines()]

        dictionary.add_documents(texts)
        dictionary.save(options.dictionaryFile)
        dictionary.save_as_text(options.dictionaryFile+'.txt')
    else:
        dictionary=corpora.Dictionary().load(options.dictionaryFile)
        print('loaded dictionary')
    
    #todo: save the corpus and update on dict removal or corpus removal    
    print('create the good corpus')
    #corpusGood=[dictionary.doc2bow(line.lower().split()) for line in open(options.goodLogFile).readlines() ]
    corpusGood=[dictionary.doc2bow([word for word in re.split(splitPattern,line.decode('ascii','ignore').lower()) if word not in stoplist]) for line in open(options.goodLogFile).readlines() ]
    print('creating the bad corpus')
    #corpusBad=[dictionary.doc2bow(line.lower().split()) for line in open(options.badLogFile).readlines() ]
    corpusBad=[dictionary.doc2bow([word for word in re.split(splitPattern,line.decode('ascii','ignore').lower()) if word not in stoplist]) for line in open(options.badLogFile).readlines() ]
    
    #create lsi models of the corpus
    #TODO: save these models if the building-block files haven't changed.
    print('creating models')
    modelGood = models.LsiModel(corpusGood, id2word=dictionary)
    modelBad = models.LsiModel(corpusBad, id2word=dictionary)
    
    #examine incoming log entries
    actors=dict()
    for stdinline in sys.stdin.readlines():
        ip=None
        badHit=False
        #determine source ip:
        for word in stdinline.split():
            if isIP(word):
                ip=word
                break
        
        #use only the request field for classification
        stdinline=(' '.join(apachequotedfieldsre.findall(stdinline)[0:1]) )
        #compare an incoming line against good/bad corpus for highest hit
        vecHit = dictionary.doc2bow([word for word in re.split(splitPattern,stdinline.lower()) if word not in stoplist])
        vecmodelGood = modelGood[vecHit] # convert the query to LSI space
        vecmodelBad = modelBad[vecHit]
        
        simsGood = sorted(vecmodelGood, key=lambda item: item[1])
        simsBad = sorted(vecmodelBad, key=lambda item: item[1])

        if len(simsBad)>0 and len(simsGood)==0:
            badHit=True
            #sys.stdout.write('bad hit: {0} {1} {2}\n'.format(ip,simsBad[-1],stdinline[:40]))
        elif len(simsBad)>0 and len(simsGood)>0 and (simsGood[-1][1]<simsBad[-1][1]):# and max(simsGood[-1][1],simsBad[-1][1])>.5: #good vs bad
            badHit=True
            #sys.stdout.write('bad hit: {0} {1} {2} {3}\n'.format(ip,simsGood[-1],simsBad[-1],stdinline[:40]))            

        if badHit:
            entry=('{0} {1:.2%} {2}'.format(ip,simsBad[-1][1],stdinline[:40]))
            #print(entry)
            if ip not in actors.keys():
                print('adding bad actor{0}'.format(ip))
                actors[ip]=dict()
                actors[ip]['hits']=list()
                actors[ip]['hits'].append(entry)
            else:
                actors[ip]['hits'].append(entry)

    for actor in actors:
        print(actor)
        for hit in actors[actor]['hits']:
            print('\t{0}'.format(hit))

def initConfig():
    #initialize configuration options
    options.dictionaryFile=getConfig('dictionairyFile','dictionary.dict',options.configfile)
    options.goodLogFile=getConfig('goodLogFile','good.log',options.configfile)
    options.badLogFile=getConfig('badLogFile','bad.log',options.configfile)
    
if __name__ == '__main__':
    optparser=OptionParser()
    optparser.add_option("-c", dest='configfile' , default='', help="configuration file to use")
    (options,args) = optparser.parse_args()
    initConfig()
    main()