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
    '''
    url like https://bcy.net/search/home?k=${SEARCH}
    '''
    img_index = 0

    def start_search_pipe(self, query):
        page = 0
        while True:
            url = f"https://bcy.net/search/home?k={query}&p={page}"
            page += 1
            rep = self.driver.request_get(url)
            if rep.status_code != 200:
                return
            pat = re.compile(r'<a href="/(item/detail/.*?)" class')
            html = rep.text
            bi = html.find('>相关内容<')
            be = html.find('关于我们')
            mats = pat.findall(html, pos=bi, endpos=be)
            if not mats:
                break
            for m in mats:
                m = f'https://bcy.net/{m}'
                if m in self.arti_cache:
                    continue
                if self.crawl_all_images_from_article(m, query):
                    self.append_arti_cache(m)


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
                if self.download(m, name=f"{BcyCrawler.img_index}.jpg", _dir=ariticle_title):
                    urls.append(m)
                    BcyCrawler.img_index += 1
                self.append_url_cache(urls)

        except:
            print(f"failed crawl images from url:{article_url}")




if __name__ == '__main__':
    argv = sys.argv
    
    ui = -1
    ki = -1
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
    if key:
        crawler.start_search_pipe(key)
    elif url:
        crawler.crawl_all_images_from_article(url)
    sys.exit(0)
    # crawler.crawl_all_images_from_article('https://bcy.net/item/detail/6361523233178558222')
    # crawler.start_search_pipe('慕羽茜')