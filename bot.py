import os
import re
import sys
import time
import json
import httplib
import urllib, urllib2

OMEGLE_URL = r"http://omegle.com"
UA = r"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6"
MSG_RE = '\["gotMessage", "([^"]+?)"\]\]'

def post(url, params, conn=False):
    headers = {'User-Agent' : UA, "Connection" : "keep-alive",
               "Accept" : "application/json", "Accept-Language" : "en-us,en;q=0.5",
               "Accept-Encoding" : "identity", "Accept-Charset" : "ISO-8859-1,utf-8;q=0.7,*;q=0.7",
               "Keep-Alive" : "177", "Content-Type" : "application/x-www-form-urlencoded; charset=utf-8",
               "Referer" : "http://omegle.com/", "Pragma" : "no-cache",
               "Cache-Control" : "no-cache"}
    p = urllib.urlencode(params)
    conn.request("POST", "/%s" % url, p, headers)
    res = conn.getresponse()
    return res.read()

def get(url):
    return urllib.urlopen(OMEGLE_URL + "/" + url).read()


class Player:
    def __init__(self):
        self.id = None
        self.conn1 = None
        self.conn2 = None
        
    def start(self):
        """
        Tell Omegle were here and we wanna talk. This will give us an id to send
        for each request.
        """
        #First request - just Omegle itself:
        om = get("")
        conn = httplib.HTTPConnection("omegle.com:80")
        #Get an id:
        id = post("start", {"rcs" : 1}, conn).replace('"', "")
        return id, conn

    def send_message(self, msg, id, conn):
        return post("send", {"id" : id, "msg" : msg}, conn)

    def play(self):
        first_id, self.conn1 = self.start()
        print "Got a first id: %s" % first_id
        
        second_id, self.conn2 = self.start()
        print "Got a second id: %s" % second_id
        
        #Wait for connection:
        state = post("events", {"id" : first_id}, self.conn1)
        print "Initial state:", state
        while "connected" not in state:
            state = post("events", {"id" : first_id}, self.conn1)
            print "1--", state
            
        #Wait for connection:
        state = post("events", {"id" : second_id}, self.conn2)
        print "Initial state:", state
        while "connected" not in state:
            state = post("events", {"id" : second_id}, self.conn2)
            print "2--", state
            
        ret = self.send_message("Hello, asl?", first_id, self.conn1)
        print "Win for first? ", ret
        if "win" not in ret:
            raise Exception("death!")
        
        ret = self.send_message("Hello, asl?", second_id, self.conn2)
        print "Win For second? ", ret
        if "win" not in ret:
            raise Exception("death!")
        
        
        count = 0
        while 1:
            try:
                count += 1
                print "count: ", count
                
                fs = post("events", {"id" : first_id}, self.conn1)
                jfs = json.loads(fs)
                ss = post("events", {"id" : second_id}, self.conn2)
                jss = json.loads(ss)
                
                #print "1===", fs, "|", jfs
                #print "2===", ss, "|", jss
                               
                if "strangerDisconnected" in (fs + ss):
                    print "Disconnect:"
                    print "1: ", fs
                    print "2: ", ss
                    break
                
                if "gotMessage" in ss:
                    for i in jss:
                        if len(i) == 2:
                            msg = i[1]
                            print "2___", msg.encode("ascii","ignore")
                            ret = self.send_message(msg, first_id, self.conn1)
                
                if "gotMessage" in fs:
                    for i in jfs:
                        if len(i) == 2:
                            msg = i[1]
                            print "1___", msg.encode("ascii","ignore")
                            ret = self.send_message(msg, second_id, self.conn2)
                    
                
                if count % 7 == 1:
                    fs = post("typing", {"id" : first_id}, self.conn1)
                    ss = post("typing", {"id" : second_id}, self.conn2)
                
                if count % 5 == 1:
                    self.conn1.close()
                    self.conn1 = httplib.HTTPConnection("omegle.com:80")
                    self.conn2.close()
                    self.conn2 = httplib.HTTPConnection("omegle.com:80")

                
                
                    
            except Exception, error:
                print
                import traceback
                traceback.print_exc()
                break

for i in xrange(10000):
    try:
        print "-" * 20
        print i
        print "-" * 20
        p = Player()
        p.play()
        time.sleep(10)
    except:
        pass



