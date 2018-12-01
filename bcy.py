# -*- coding: utf-8 -*-
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests
import re
import shutil
import os
import json
import argparse
import traceback
import random
from crawl_base import ImageCrawler
from crawl_base import FileStorager
import sys

class BcyCrawler(ImageCrawler):
    def __init__(self):
        super(BcyCrawler, self).__init__()
        self.img_index = 0
        self.user_search = False
        self.query = ''
    '''
    url like https://bcy.net/search/home?k=${SEARCH}
    '''

    def start_search_pipe(self, query):
        self.query = query
        page = 0
        while True:
            url = f"https://bcy.net/search/home?k={query}&p={page}"
            page += 1
            rep = self.driver.request_get(url)
            if rep.status_code != 200:
                return
            html = rep.text
            if self.user_search :
                if not self.pipe_user_search_page(html):
                    break
            else:
                if self.pipe_content_search_page(html):
                    self.append_arti_cache(url)
                else:
                    break


    def pipe_user_search_page(self, html):
        pat = re.compile(r'<a href="/(u/\d*?)">')
        bi = html.find('>相关用户<')
        be = html.find('相关内容')
        mats = pat.findall(html, pos=bi, endpos=be)
        if not mats:
            return 0
        for m in mats:
            m = f'https://bcy.net/{m}/post'
            rep = self.driver.request_get(m)
            if rep.status_code != 200:
                return
            self.pipe_user_zone_page(rep.text)  
        return len(mats)

    def pipe_user_zone_page(self, html):
        pat = re.compile(r'JSON.parse\("(.*)"\);')
        mats = pat.findall(html)
        if not mats:
            return
        jsd = self.htmljsontext_to_json(mats[0])
        meta = json.loads(jsd)
        items = meta['post_data']['list']
        for item in items:
            if item['tl_type'] == 'item':
                item_id = item['item_detail']['item_id']
                durl = f"https://bcy.net/item/detail/{item_id}"
                self.crawl_all_images_from_article(durl, self.query)
        return 0

    def pipe_content_search_page(self, html):
        pat = re.compile(r'<a href="/(item/detail/.*?)" class')
        bi = html.find('>相关内容<')
        be = html.find('关于我们')
        mats = pat.findall(html, pos=bi, endpos=be)
        if not mats:
            return 0
        for m in mats:
            m = f'https://bcy.net/{m}'
            if m in self.arti_cache:
                continue
            if self.crawl_all_images_from_article(m, self.query):
                self.append_arti_cache(m)
        return len(mats)

    def crawl_all_images_from_article(self, article_url, ariticle_title = ''):
        '''
        url like: https://bcy.net/item/detail/6587526384006988046
        '''        
        
        pat0 = re.compile(r'<title>(.*?)</title>', re.S)
        pat = re.compile(r'<img src="(https://.*?.jpg)')
        pat2 = re.compile(r'JSON.parse\("(.*?)"\);\n')
        urls = []
        try:
            rep = self.driver.request_get(article_url)
            if rep.status_code != 200:
                return
            html = rep.text
            if not ariticle_title:
                ariticle_title = pat0.findall(html)[0].strip()
                ariticle_title = ariticle_title.replace('/', '_').replace('\\', '_')
            jsd = self.htmljsontext_to_json(pat2.findall(html)[0])
            meta = json.loads(jsd)
            items = meta['detail']['post_data']['multi']
            
            for it in items:
                m = it['original_path']
                if m in self.url_cache:
                    continue
                if self.download(m, name=f"{self.img_index}.jpg", _dir=ariticle_title):
                    urls.append(m)
                    self.img_index += 1
                self.append_url_cache(urls)

        except Exception as e:
            print(f"failed crawl images from url:{article_url} ==> {e}")

# if __name__ == "__main__":
#     crawler = BcyCrawler()
#     crawler.set_writer(FileStorager('bcy_output'))
#     crawler.user_search = True
#     key = '茶可柚'
#     if key:
#         crawler.start_search_pipe(key)
#     elif url:
#         crawler.crawl_all_images_from_article(url)
#     sys.exit(0)


if __name__ == '__main__':
    argv = sys.argv
    
    ui = -1
    ki = -1
    useri = -1
    if '-u' in argv:
        ui = argv.index('-u')
    if '-url' in argv:
        ui = argv.index('-url')
    url = ''
    if ui >= 0:
        url = argv[ui + 1]
    key = ''
    if '-k' in argv:
        ki = argv.index('-k')
    if '-key' in argv:
        ki = argv.index('-key')
    
    if ki >= 0:
        key = argv[ki + 1]

    if not key and not url:
        print("usage for url: bcy [-url/-u] url \n \t or search: bcy [-key/-k] keyword to search")
        sys.exit(1)
    
    crawler = BcyCrawler()
    crawler.set_writer(FileStorager('bcy_output'))
    crawler.user_search = '-user' in argv

    if key:
        crawler.start_search_pipe(key)
    elif url:
        crawler.crawl_all_images_from_article(url)
    sys.exit(0)
    # crawler.crawl_all_images_from_article('https://bcy.net/item/detail/6361523233178558222')
    # crawler.start_search_pipe('慕羽茜')