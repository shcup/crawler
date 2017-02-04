#!/usr/bin/env python
#-*-coding:utf-8-*-
#!Author:jiaokeke1@letv.com
# Modified: 20170116.

import urllib2
import random
import time
import sys
import json
import random
import os
from BeautifulSoup import BeautifulSoup
reload(sys)
sys.setdefaultencoding("utf-8")

class doc:
    def __init__(self):
        self.id = ""
        self.tag_str = "NULL"


class Spider(object):
    name = "ToutiaoCrawler"
    start_urls = ['http://www.toutiao.com/api/pc/feed/?category=__all__&utm_source=toutiao&widen=1&max_behot_time=%s',
                  'http://www.toutiao.com/api/pc/feed/?category=news_hot&utm_source=toutiao&widen=1&max_behot_time=%s'
                  #'http://www.toutiao.com/news_society/',
                  #'http://www.toutiao.com/news_entertainment/'
                  ]
    hd = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    group_id_set = set()
    url_info_path = "toutiao_info.txt"
    source_url_prefix = "http://www.toutiao.com"
    group_id_url_prefix = "http://www.toutiao.com/a"
    toutiao_info_f = None
    def __init__(self):
        self.toutiao_info_f =open(self.url_info_path, 'w')
        #print >> self.toutiao_info_f, "group_id\tchinese_tag\tsource_url\ttitle"
    def __del__(self):
        self.toutiao_info_f.close()

    def down_url(self, id, doc_detail):
        group_id = str(id)
        tag_str, body = self.gen_body_and_tags(group_id)
        chinese_tag = doc_detail.get('chinese_tag', None)
        source_url = doc_detail.get('source_url', None)
        title = doc_detail.get('title', None).encode('utf-8')
        if tag_str and chinese_tag and source_url and title:
            self.group_id_set.add(group_id)
            print >> self.toutiao_info_f, \
            "\t".join([group_id, chinese_tag.encode('utf-8'), self.source_url_prefix + source_url, title.encode('utf-8'), tag_str, body.encode('utf-8')])
        else:
            print >> sys.stderr, "bad doc_detail group_id:", group_id

    def gen_body_and_tags(self, id):
        req_url = self.group_id_url_prefix + id
        body = "NULL"
        try:
            req = urllib2.Request(req_url, headers = self.hd)
            page = urllib2.urlopen(req_url,timeout = 20)
            content = page.read()
            soup = BeautifulSoup(content)
            ul = soup.find('ul', {'class':'label-list'})
            if ul is None:
                print >> sys.stderr, id, " ul is None"
                return None, body
            tags = set()
            for tag in ul.findAll('li', {'class':'label-item'}):
                tags.add(tag.find('a').text.replace(' ', ''))
            body = soup.find('div',{'class':'article-content'})
            if not body:
                body = "NULL"
            if tags:
                return ','.join(tags), body
            else:
                return None, body
        except:
            print >> sys.stderr, "bad id have no tags:", id
            return None, body
        
    def alaly_json(self, json_req):
        doc_list = json_req.get('data', [])
        for doc_detail in doc_list:
            group_id = int(doc_detail.get('group_id', 0))
            if group_id == 0 or group_id in self.group_id_set:
                print >> sys.stderr, "repetitive group_id:", group_id
                continue
            else:
                self.down_url(group_id, doc_detail)

    def start(self):
        for url in self.start_urls:
            count = 0
            be_hot_time = 0
            while count < 10:
                req_url  = url % (be_hot_time)
                count += 1
                try:
                    response = urllib2.urlopen(req_url).read()
                    json_req = json.loads(response)
                    be_hot_time = json_req['next']['max_behot_time']
                except:
                    print >> sys.stderr, "urllib2.urlopen error!"
                self.alaly_json(json_req)
                sleep_time = random.randint(3, 8)       #'%.2f' % random.random()
                time.sleep(float(sleep_time))





s = Spider()
s.start()

