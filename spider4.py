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
import base64
from bs4 import BeautifulSoup
import traceback
#from BeautifulSoup import BeautifulSoup
reload(sys)
sys.setdefaultencoding("utf-8")

class doc:
    def __init__(self):
        self.id = None
        self.title = None
        self.category = None
        self.tag_str = None
        self.time = None
        self.body = None
        self.desc = None
        self.provider = None
        self.en_channel = None
        self.zh_channel = None
    def to_str(self):
        return '\t'.join([self.id, self.category.encode('utf8'), self.title.encode('utf8'), self.tag_str.encode('utf8'), \
        self.time.encode('utf8'), self.body.encode('utf8')])
def analy_content(content, id):
    d = doc()
    try:
        soup = BeautifulSoup(content)
        ul = soup.find('ul', {'class':'label-list'})
        tags = set()
        if ul is None:
            print content
            print >> sys.stderr, id, " ul is None"
        else:
            for tag in ul.findAll('li', {'class':'label-item'}):
                tags.add(tag.find('a').text.replace(' ', ''))
        body = soup.find('div',{'class':'article-content'})
        time = soup.find('span',{'class':'time'})
        title = soup.find('h1',{'class':'article-title'})
        desc = soup.find('p',{'class':'pgc-description'})
        provider = soup.find('span',{'class':'src'})
        channel_info = soup.find('a',{'ga_event':'click_channel'})
        #print "\n----cid:", channel_info.attrs.get("href", None), channel_info.text
        if tags and len(tags) > 0:
            d.tag_str = ','.join(tags)
        if body:
            d.body = body.text
        if time:
            d.time = time.text
        if title:
            d.title = title.text.strip()
        if desc:
            d.desc = desc.text
            #print "desc:", d.desc
        if provider:
            d.provider = provider.text.strip()
        if channel_info:
            d.en_channel = channel_info.attrs.get("href", None)
            d.zh_channel = channel_info.text
    except:
        traceback.print_exc()
        print content
        print >> sys.stderr, "analy_content error:", id
    return d

class Spider(object):
    name = "ToutiaoCrawler"
    category_list = ['__all__', 'news_hot', 'news_finance', 'news_sports', 'news_military', 'news_comic', 'news_history', 'news_world', \
                    'news_entertainment', 'news_pet', 'news_home', 'news_house', 'news_edu', 'digital', 'news_culture', 'news_travel', \
                    'news_fashion', 'news_politics', 'news_astrology', 'news_car', 'news_game', 'news_society', 'science_all', \
                    'news_tech', 'news_baby', 'news_food', 'news_agriculture', 'emotion', 'news', 'news_psychology', 'news_story', \
                    'news_career', 'news_health', 'funny', 'news_photography', 'news_collect', 'news_beauty', 'news_essay', 'news_design', \
                    'news_geomantic']
    start_urls = ['http://www.toutiao.com/api/pc/feed/?category=%s&utm_source=toutiao&widen=1&max_behot_time=%s',
                  ]
    hd = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'}
    url_info_path = "toutiao_info1.txt"
    source_url_prefix = "http://www.toutiao.com"
    group_id_url_prefix = "http://www.toutiao.com/a"
    toutiao_info_f = None
    def __init__(self):
        cmd = "touch %s" % self.url_info_path
        os.system(cmd)
        self.group_id_set = set()
        temp_open = open(self.url_info_path, "r")
        count = 0
        for line in temp_open:
            try:
                id = line.strip().split()[0]
                self.group_id_set.add(int(id))
                count += 1
            except:
                print "error", line
        temp_open.close()
        print >> sys.stderr, "have load id:", len(self.group_id_set), count
        self.toutiao_info_f =open(self.url_info_path, 'a')
        #print >> self.toutiao_info_f, "group_id\tchinese_tag\tsource_url\ttitle"
    def __del__(self):
        self.toutiao_info_f.close()

    def down_url(self, id, doc_detail):
        group_id = str(id)
        d = self.gen_body_and_tags(group_id)
        chinese_tag = doc_detail.get('chinese_tag', None)
        #source_url = doc_detail.get('source_url', None)
        en_tag = doc_detail.get('tag', 'NULL')
        if d.tag_str and chinese_tag and d.title and d.desc and d.body and id not in self.group_id_set:
            self.group_id_set.add(id)
            print >> sys.stderr, "sucess:", group_id
            out_line = \
            "\t".join([group_id, chinese_tag.encode('utf-8') + ',' + en_tag.encode('utf-8'), self.group_id_url_prefix + group_id, \
            d.title.encode('utf-8'), \
            d.desc.encode('utf-8'), \
            d.tag_str, \
            d.time, \
            base64.b64encode(d.body.encode('utf-8'))])
            self.toutiao_info_f.write(out_line + "\n")
        else:
            print >> sys.stderr, "bad doc_detail group_id:", group_id, "\ndesc:", d.desc, 
                    #"\ntitle:", d.title, "\ndesc:", d.desc, "\nbody:",d.body



    def gen_body_and_tags(self, id):
        req_url = self.group_id_url_prefix + id
        content = None
        try:
            req = urllib2.Request(req_url, headers = self.hd)
            page = urllib2.urlopen(req_url,timeout = 20)
            content = page.read()
        except:
            print >> sys.stderr, "gen_body_and_tags error!", id
        if content:
            return self.analy_content(content)
        
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
            for category in self.category_list:
                count = 0
                be_hot_time = 0
                while count < 7:
                    req_url  = url % (category, be_hot_time)
                    count += 1
                    print >> sys.stderr, "cur url:", req_url
                    try:
                        response = urllib2.urlopen(req_url).read()
                        json_req = json.loads(response)
                        be_hot_time = json_req['next']['max_behot_time']
                    except:
                        print >> sys.stderr, "urllib2.urlopen error!"
                    self.alaly_json(json_req)
                    sleep_time = random.randint(2, 4)       #'%.2f' % random.random()
                    time.sleep(sleep_time)
                    

'''
while True:
    s = Spider()
    s.start()
    cmd = "cp %s %s" % (s.url_info_path, s.url_info_path + ".bak")
    os.system(cmd)
    sleep_time = random.randint(300, 500)
    print >> sys.stderr, "sleep and again:", sleep_time
    time.sleep(sleep_time)

'''
