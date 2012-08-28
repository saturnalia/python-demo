#!/usr/lib/python
#
# Python script to parse XML file
#

#import library to do http requests:
import urllib2
import os
import sys

#import easy to use xml parser called minidom
from xml.dom.minidom import parseString
import xml.dom as dom

#download the file:
#file = urllib2.urlopen('http://www.somedomain.com/somexmlfile.xml')
file = open('zyang.xml','r')

#convert to string:
data = file.read()

#close file because we dont need it anymore:
file.close()

#print data

#parse the xml you downloaded
dom_data = parseString(data)

#retrieve the first xml tag (<tag>data</tag>) that the parser finds with name tagName:
xmlTag = dom_data.getElementsByTagName('tagName')[0].toxml()

#strip off the tag (<tag>data</tag>  --->   data):
xmlData=xmlTag.replace('<tagName>','').replace('</tagName>','')

#print out the xml tag and data in this format: <tag>data</tag>
print xmlTag

#just print the data
print xmlData 
