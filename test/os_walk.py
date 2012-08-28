import os

def walk_dir(dir,fileinfo,topdown=True):
    for root, dirs, files in os.walk(dir, topdown):
        for name in files:
            print(os.path.join(name))
            fileinfo.write(os.path.join(root,name) + '\n')
        for name in dirs:
            print(os.path.join(name))
            fileinfo.write('  ' + os.path.join(root,name) + '\n')

def main():
    dir = raw_input('please input the path:')
    fileinfo = open('list.txt','w')
    walk_dir(dir,fileinfo)


if __name__ == "__main__":
    main()
