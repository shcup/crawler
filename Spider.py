
import sqlite3 as lite
import sys
import traceback
import urllib
import json
import socket



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
    worker_cur = 0
    port = 51423

    con = lite.connect('toutiao.db')
    con.text_factory = str
    cur = con.cursor()

    tableName = "DocTable"

    try:
        sql = 'CREATE TABLE if not exists ' + tableName + '(id PRIMARY KEY, url, desc, title, body, tag, category, timestamp)'
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

    def InsertDataIntoDB(self, id):
        try:
            row=[0]*3
            row[0]= id
            row[1] = "title"
            row[2] = "body"
            sql = "INSERT INTO " + self.tableName + "(id, title, body) VALUES (?,?, ?);"
            self.cur.executemany(sql, (row,))
            self.con.commit()
        except:
            traceback.print_exc()

    def GetNextWorker(self):
        self.worker_cur = (self.worker_cur + 1) % 3
        return self.worker_list[self.worker_cur ]

    def GetContentFromWorker(self, id):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.GetNextWorker(), self.port))

        content = ""
        try:
            send_len = s.send(id)
            content = s.recv(4096000)
        except:
            print "error to get data from: " + s.getpeername()
        s.close()
        return content

    def TryGetContent(self, id):
        count = 0
        content = ""
        while count < 3:
            content = self.GetContentFromWorker(id)
            if len(content) == 0:
                break;
            count = count + 1
        return content

    def Start(self):
        print "Spider start!"
        for id_ in open("test.txt"):
            id = id_.strip()
            if self.CheckIDExist(id) == True:
                print "doc " + id + " already exist in db!"
                continue
            request_url = "http://www.toutiao.com/a" + id + "/"
            content = self.TryGetContent(request_url)
            self.InsertDataIntoDB(id)






s = Spider()
s.Start()

