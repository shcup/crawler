
import sqlite3 as lite
import sys
import traceback
import urllib
import json
import socket

import spider4



class Spider():
    name = "ToutiaoCrawler"
    start_urls = ['http://www.toutiao.com/api/pc/feed/?category=__all__&utm_source=toutiao&widen=1&max_behot_time={%s}&max_behot_time_tmp={%s}',
                  'http://www.toutiao.com/api/pc/feed/?category=news_hot&utm_source=toutiao&widen=1&max_behot_time={%s}&max_behot_time_tmp={%s}',
                  'http://www.toutiao.com/news_society/',
                  'http://www.toutiao.com/news_entertainment/']
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/50.0.2661.102 Safari/537.36'
    }

    worker_list = ['10.11.145.35', '10.11.145.39', '10.11.144.116']
    #worker_list = ['127.0.0.1']
    worker_cur = 0
    port = 51423

    con = lite.connect('toutiao.db')
    con.text_factory = str
    cur = con.cursor()

    tableName = "DocTable"

    try:
        sql = 'CREATE TABLE if not exists ' + tableName + '(id PRIMARY KEY, url, content, desc, title, body, tag, zh_category, en_category, timestamp, provider)'
        cur.execute(sql)
        cur.execute("create index if not exists doc_id_index on " + tableName + "(id);")
        cur.execute("create index if not exists doc_url_index on " + tableName + "(url);")
    except lite.IntegrityError:
        sys.stderr.write(tableName)
        sys.exit(1)

    def CheckIDExist(self, id):
        try:
            sql = "select count(*) from " + self.tableName + " where id = '" + id + "'"
            self.cur.execute(sql)
            r = self.cur.fetchall()
            if len(r) > 0 and len(r[0]) > 0:
                #for e in range(len(r)):
                #print(r[e])
                #print r[0][0]
                if (r[0][0] != 0):
                    return True
        except :
            traceback.print_exc()
        return False

    def InsertDataIntoDB(self, id, content, doc ):
        try:
            row=[0]*10
            row[0]= id
            row[1] = content
            row[2] = doc.desc
            row[3] = doc.title
            row[4] = doc.body
            row[5] = doc.tag_str
            row[6] = doc.zh_channel
            row[7] = doc.en_channel
            row[8] = doc.time
            row[9] = doc.provider
            sql = "INSERT INTO " + self.tableName + "(id, content, desc, title, body, tag, zh_category, en_category, timestamp, provider) VALUES (?,?,?,?,?,?,?,?,?,?);"
            self.cur.executemany(sql, (row,))
            self.con.commit()
        except:
            traceback.print_exc()

    def GetNextWorker(self):
        self.worker_cur = (self.worker_cur + 1) % len(self.worker_list)
        return self.worker_list[self.worker_cur ]

    def GetContentFromWorker(self, id):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = self.GetNextWorker()
        #print >> sys.stderr, "host: " + host
        s.connect((host, self.port))

        content = ""
        try:
            send_len = s.send(id)
            while 1:
                tmp = s.recv(409600)
                #print "Receive data length: " + str(len(tmp))
                if tmp and len(tmp) > 0:
                    content = content + tmp
                else:
                    break
        except:
            print "error to get data from: " + s.getpeername()
        s.close()
        return content

    def TryGetContent(self, id):
        count = 0
        content = ""
        while count < 3:
            content = self.GetContentFromWorker(id)
            if len(content) > 0:
                break;
            count = count + 1
        return content

    def Start(self):
        print "Spider start!"
        count = 0
        #for id_ in open("test.txt"):
        for id_ in sys.stdin:
            id = id_.strip()
            if self.CheckIDExist(id) == True:
                print "doc " + id + " already exist in db!"
                continue
            if count % 100 == 1:
                print "Finish : " + str(count)
            count = count + 1
            request_url = "http://www.toutiao.com/a" + id + "/"
            content = self.TryGetContent(request_url)
            if len(content) == 0:
                print >> sys.stderr, "Failed to download url: " + request_url
            doc = spider4.analy_content(content, id)
            self.InsertDataIntoDB(id, content, doc)






s = Spider()
s.Start()

