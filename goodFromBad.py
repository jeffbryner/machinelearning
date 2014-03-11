#!/usr/bin/env python
import os
import sys
import re
''' ideally you get a set of good hits from QA when they release a site to production
    Most things aren't ideal, so here's a way to simply separate likely good from likely bad
    based on http status return codes
'''

inputfile=sys.argv[1]
goodfile=open('{0}.good'.format(inputfile),'wb')
badfile=open('{0}.bad'.format(inputfile),'wb')


apachequotedfieldsre=re.compile(r'''"(.*?)"''')     #get fields delimited by ""
apachestatusre=re.compile(r''' ([0-9]{3}) ''')      #get 3 digit http status field

for line in open(inputfile).readlines():
    if len(apachestatusre.findall(line))>0:
        if int(apachestatusre.findall(line)[0])<400:
            goodfile.write('{0}\n'.format(apachequotedfieldsre.findall(line)[0].replace('GET ',''))) #url only.
        else:
            #write HTTP verb, status code and url to help our machine learning.
            badfile.write('{0} {1}\n'.format( int(apachestatusre.findall(line)[0]), ' '.join(apachequotedfieldsre.findall(line)[0:1])))

goodfile.close()
badfile.close()