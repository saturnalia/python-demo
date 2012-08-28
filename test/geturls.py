#===========geturls.py================
#coding:utf-8

import urllib
import urlparse
import re
import socket
import threading
import sys

#定义链接正则
urlre = re.compile(r"href=[\"']?([^ >\"']+)")
titlere = re.compile(r"<title>(.*?)</title>",re.I)

#设置超时时间为10秒
timeout = 10
socket.setdefaulttimeout(timeout)

#定义最高线程数
max = 10
#定义当前线程数
current = 0

def gettitle(url):
    global current
    try:
        content = urllib.urlopen(url).read()
    except:
        current -= 1
        return
    if titlere.search(content):
        title = titlere.search(content).group(1)
        try:
            title = title.decode('gbk').encode('utf-8')
        except:
            title = title
    else:
        title = "无标题"
    print "%s: %s" % (url,title)
    current -= 1
    return

def geturls(url):
    global current,max
    ts = []
    content = urllib.urlopen(url)
    #使用set去重
    result = set()
    for eachline in content:
        if urlre.findall(eachline):
            temp = urlre.findall(eachline)
            for x in temp:
                #如果为站内链接，前面加上url
                if not x.startswith("http:"):
                    x = urlparse.urljoin(url,x)
                #不记录js和css文件
                if not x.endswith(".js") and not x.endswith(".css"):
                    result.add(x)
    threads = []
    for url in result:
        t = threading.Thread(target=gettitle,args=(url,))
        threads.append(t)
    i = 0
    while i < len(threads):
        if current < max:
            threads[i].start()
            i += 1
            current += 1
        else:
            pass


def get_url_test(url):
    global current,max
    ts = []
    content = urllib.urlopen(url)
    print content
    for eachline in content:
        print eachline



if __name__=='__main__':
    #geturls("http://www.baidu.com")
    #geturls("http://www.google.com")
    #get_url_test("http://www.google.com")
    geturls(sys.argv[1])
