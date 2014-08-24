#!/usr/bin/env python

import cgi
import cgitb
import re
import string
# https://pypi.python.org/pypi/urllib3
import urllib3

'''
e46 page crawler

Please see http://forum.e46fanatics.com/showthread.php?p=16295676 for help

By Liam Slusser / lslusser at gmail.com / 8/22/2014
'''

cgitb.enable()

class urlFetcher:
    def __init__(self):
        
        self.h = urllib3.PoolManager()
        self.maxtime = 5
        self.headers = {}
        self.type = "GET"
        self.r = None
                
    def fetch(self,url):
        self.r = self.h.urlopen(self.type,url,headers=self.headers)
        return self.r.status
    
    def returnStatus(self):
        if self.r:
            return self.r.status
    
    def returnData(self):
        if self.r:
            return self.r.data

class doSearch:
    def __init__(self,form):
        self.form = form
        self.pagecache = ""
        self.start = ""
        self.end = ""
        self.startpage = 1
        self.endpage = 0
        self.pagenumbers = 0
        self.urlfetcher = urlFetcher()
        self.urlfetcher.site = "forum.e46fanatics.com"
        self.urlfetcher.host = "forum.e46fanatics.com"
        self.urlfetcher.headers['host'] = "forum.e46fanatics.com"
        self.urlfetcher.headers['User-Agent'] = "liam821.com e46fanatics page crawler"
        self.checkParams()
        self.build()
    
    def checkParams(self):
        if "startpage" in self.form:
            self.startpage = int(self.form.getlist("startpage")[0])
        if "endpage" in self.form:
            self.endpage = int(self.form.getlist("endpage")[0])
        
    def build(self):
        # fetch page one and verify
        self.postid = int(self.form.getlist("postid")[0])
        url = """http://%s/showthread.php?t=%s&page=1""" % (self.urlfetcher.site,self.postid)
        if self.urlfetcher.fetch(url):
            self.pagecache = self.urlfetcher.returnData()
            self.start = re.findall('^.*<div id="posts">',self.pagecache,re.M|re.DOTALL)[0]
            self.end = re.findall('(<div id="lastpost".*)',self.pagecache,re.M|re.DOTALL)[0]
            self.pagenumbers = int(re.findall('Page 1 of (\d+)',self.pagecache)[0])
            if self.endpage:
                if self.endpage > self.pagenumbers:
                    self.endpage = self.pagenumbers
            else:
                self.endpage = self.pagenumbers
                
            if self.startpage:
                if self.startpage > self.pagenumbers:
                    raise Exception("Your startpage is greater than the total page numbers!")
        
            print self.start
                        
            for page in range(self.startpage,self.endpage+1):
                print "Page %s" % (page)
                if page == 1:
                    for post in re.findall('<!-- post #.*?-- / post #\d+ -->',self.pagecache,re.M|re.DOTALL):
                        if re.findall('bold" href="member.php.*[^\n]">(.*?)<',post)[0] == self.form.getlist("username")[0]:
                            print post
                else:
                    url = """http://%s/showthread.php?t=%s&page=%s""" % (self.urlfetcher.site,self.postid,page)
                    if self.urlfetcher.fetch(url):
                        self.pagecache = self.urlfetcher.returnData()
                        for post in re.findall('<!-- post #.*?-- / post #\d+ -->',self.pagecache,re.M|re.DOTALL):
                            if re.findall('bold" href="member.php.*[^\n]">(.*?)<',post)[0] == self.form.getlist("username")[0]:
                                print post
                    
            print self.end

if __name__ == "__main__":

    print "Content-Type: text/html"     # HTML is following
    print                               # blank line, end of headers

    form = cgi.FieldStorage()

    if "postid" in form and "username" in form:
        doSearch(form)
    else:
        print "<h1>You need to give me a postid and username</h1>"
        print """<br><br>See http://forum.e46fanatics.com/showthread.php?p=16295676 for help."""
        raise Exception("You need to give me a postid and username!")
