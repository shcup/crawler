import sqlite3 as lite
import sys
import base64
import traceback

def run():
    con = lite.connect('toutiao.db')
    con.text_factory = str
    cur = con.cursor()

    f = open("dump.txt", "w")

    try:
        sql = "select id, title, body, zh_category, tag from DocTable where title is not null and body is not null";
        cur.execute(sql)
        r = cur.fetchall()

        for e in range(len(r)):
            print >> f, '\t'.join([r[e][0], r[e][1], base64.b64encode(r[e][2]), str(r[e][3]), str(r[e][4])])
    except:
        traceback.print_exc()
    f.close()
    return False


run()

