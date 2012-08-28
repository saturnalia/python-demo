#!/usr/bin/python
# -*- coding: cp936 -*-
#

import os,sys



def listdir(dir,file):
    file.write(dir + '\n')
    fielnum = 0
    list = os.listdir(dir)
    for line in list:
        filepath = os.path.join(dir,line)
        if os.path.isdir(filepath):
            file.write('   ' + line + '\\'+'\n')
            listdir(filepath, file)
        elif os.path:
            file.write('   '+line + '\n') 
            fielnum = fielnum + 1
    file.write('FilePath[%s] has files=[%s] \n'%(filepath, str(fielnum)))

def main():
    dir = raw_input('please input the path:')
    myfile = open('list.txt','w')
    listdir(dir, myfile)


if __name__ == '__main__':
    main()
