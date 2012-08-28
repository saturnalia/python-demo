#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# To read a file and output the line number.

import os
import sys
import re

global lns

def parselines(lines):
    lns = 0
    if lines == '':
        return lns

    # create regular expression
    pattern = re.compile(r"[^\n]*\n")
    #pattern = re.compile(r"^\n")

    #
    # re.findall works
    #
    result = re.findall(pattern, lines)
    for item in result:
        lns += 1
        #print "re.findall item[%d]=[%s]"%(lns, item)
    print "Total lines of re.findall =" + repr(lns) + "\n"

    #
    # re.search
    #
    #result = re.search(pattern, lines)    
    #print "search result=%s"%(result)

    #
    # re.split works
    #
    # In total lines, re.split = re.findall + 1
    #
    result = re.split(pattern, lines)
    lns = 0
    for item in result:
        #print "item[%d]=[%s]"%(lns, item)
        lns = lns + 1    
    lns = len(result)
    print "Length of re.split result=%d\n"%(lns)

    #
    # re.match
    #
    lns = 0
    result = re.match(pattern, lines)
    for item in result.groups():
        lns = lns + 1
        print "re.match result=%s"%(item)
            
    print "Length of re.match result=%d\n"%(lns)

#
# Param: input_file : the input file id
#
# Return: Number of file lines in the given file
#
def check_lines(input_file):
    f = input_file
    lns = 0
    while True:
        line = f.readline(2048)
        if line == EOF:
            break
        lns += 1
    return lns


def main():
    #inputfile = raw_input("Please input file name:")
    #inputfile = repr(sys.argv[1])
    
    try:
        #myfile = open(inputfile, 'r')
        print sys.argv[0]
        print sys.argv[1]
        myfile = open(sys.argv[1], 'r')
        #num = check_lines(myfile)
        #print "num=" + num

        data = myfile.read()

        parselines(data)
        
    #except:
    #    print "Unknown file open [%s] error \n"%(sys.argv[1])
    finally:
        pass




if __name__ == '__main__':
    main()

