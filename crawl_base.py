import requests
import os

class Driver:
    def __init__(self):
        self.token = ''
        self.cookies = []
        self.proxies = { "http": "socks5://127.0.0.1:1086", "https": "socks5://127.0.0.1:1086"}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    def request_get(self, url, params=None, **kwargs):
        rep = requests.get(url, cookies=self.cookies, headers=self.headers, proxies=self.proxies)
        return rep
    

class Output:
    def write_response(self, resp, **params):
        pass
    

class FileStorager(Output):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def write_response(self, resp, name, _dir = None):
        if os.path.isabs(name):
            sname = name
        elif _dir:
            sname = os.path.join(_dir, name)
        else:
            sname = os.path.join(self.root_dir, name)

        if not os.path.isabs(sname):
            sname = os.path.join(self.root_dir, sname)
        
        _dir = os.path.dirname(sname)
        os.makedirs(_dir, exist_ok=True)
        with open(sname, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)

class Crawler:
    def __init__(self):
        self.driver = Driver()
        self.output = 'output'
        self.url_cache = {}

    def set_writer(self, writer):
        self.writer = writer

    def start_search_pipe(self, **params):
        pass

    def download(self, url, name, **params):
        for i in range(0, 3):
            result = self.driver.request_get(url)
            if result.status_code == 200:
                self.writer.write_response(result, name, **params)
                return True
            else:
                continue
        print(f"Error download:{url}")
        return False   


class ImageCrawler(Crawler):

    def crawl_all_images_from_article(self, article_url):
        pass



