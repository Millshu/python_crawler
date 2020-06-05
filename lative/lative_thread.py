import requests
from urllib import request
from bs4 import BeautifulSoup as bs
import os
import time
import threading
from queue import Queue

crawl_list = []
parse_list = []
subcrawl_list = []
subparse_list = []


class CrawlThread(threading.Thread):#整頁的原始碼
    def __init__(self, name, product_queue, data_queue):
        super(CrawlThread, self).__init__()
        self.name = name
        self.product_queue = product_queue
        self.data_queue = data_queue
        self.url = 'https://www.lativ.com.tw/MEN/tops/{}'
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    def run(self):
        print('-------{}啟動-------'.format(self.name))
        while 1:
            if self.product_queue.empty():
                break
            product = self.product_queue.get()
            product_url = self.url.format(product)
            res = requests.get(product_url, headers=self.headers)
            self.data_queue.put(res.text)
            # print('主內容'+res.text)
        print('-------{}結束-------'.format(self.name))


class ParseThread(threading.Thread):#每張照片的url的網址
    def __init__(self, name, data_queue, every_product_queue):
        super(ParseThread, self).__init__()
        self.name = name
        self.data_queue = data_queue
        self.every_product_queue = every_product_queue


    def run(self):
        print('-------{}啟動-------'.format(self.name))
        while 1:
            product_data = self.data_queue.get()
            self.product_content(product_data)

    def product_content(self, product_data):
        product_soup = bs(product_data, 'html.parser')
        every_product_list = product_soup.select('a[class="imgd"]')
        for every_product_id in range(len(every_product_list)):
            product_id = every_product_list[every_product_id]['href']
            self.every_product_queue.put(product_id)
            print(product_id)


class SubCrawlThread(threading.Thread):#讀這網址的Url原始碼 進去每個商品的原始碼
    def __init__(self, name, every_product_queue, every_data_queue):
        super(SubCrawlThread, self).__init__()
        self.name = name
        self.every_product_queue = every_product_queue
        self.every_data_queue = every_data_queue
        self.every_url = 'https://www.lativ.com.tw{}'
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    def run(self):
        print('-------{}啟動-------'.format(self.name))
        while 1:
            every_product = self.every_product_queue.get()
            every_product_url = self.every_url.format(every_product)
            print('我是商品URL:' + every_product_url)
            sub_res = requests.get(every_product_url, headers=self.headers)
            time.sleep(1)
            self.every_data_queue.put(sub_res.text)
            # print(sub_res.text)
        print('-------{}結束-------'.format(self.name))


class SubParseThread(threading.Thread):#抓顏色的圖片
    def __init__(self, name, every_data_queue, lock):
        super(SubParseThread, self).__init__()
        self.name = name
        self.every_data_queue = every_data_queue
        self.lock = lock

    def run(self):
        print('-------{}啟動-------'.format(self.name))
        while 1:
            every_product_data = self.every_data_queue.get()
            self.every_product_content(every_product_data)

    def every_product_content(self, every_product_data):
        every_product_soup = bs(every_product_data, 'html.parser')
        every_product_color_url_temp = every_product_soup.select('img[id="productImg"]')[0]['src']
        every_product_id = every_product_color_url_temp[26:31]
        print('個別商品URL:' + every_product_color_url_temp)
        temp1 = every_product_id + '0{}1'
        temp2 = every_product_id + '0{}_500.jpg'
        every_product_color_url_model =every_product_color_url_temp.split('{}'.format(every_product_id))[0] + every_product_id + '/' + temp1 + '/' + temp2
        self.lock.acquire()
        for i in range(1, 5):
            every_product_color_url = every_product_color_url_model.format(i, i)
            # print(every_product_color_url)
            id = every_product_color_url[-24:-16]
            local = os.path.join('C:\\Users\\user\PycharmProjects\\finalhomework\image\{}.jpg'.format(id))
            try:
                request.urlretrieve(every_product_color_url, local)
            except:
                pass
        self.lock.release()


def mkdir_data(path='C:\\Users\\user\PycharmProjects\\finalhomework\image'):  # 創建資料夾path(為所要創建資料夾的路徑)
    if not os.path.exists(path):
        os.mkdir(path)


def create_queue():
    product_list = ['short_graphic_tee']
    product_queue = Queue()
    for product in product_list:
        product_queue.put(product)

    data_queue = Queue()
    every_product_queue = Queue()
    every_data_queue = Queue()
    return product_queue, data_queue, every_product_queue, every_data_queue


def create_crawl_thread(product_queue, data_queue):
    crawl_name = ['主網爬蟲1號']
    for name in crawl_name:
        tcrawl = CrawlThread(name, product_queue, data_queue)
        crawl_list.append(tcrawl)


def create_parse_thread(data_queue, every_product_queue):
    parse_name = ['取得商品1號']
    for name in parse_name:
        tparse = ParseThread(name, data_queue, every_product_queue)
        parse_list.append(tparse)


def create_subcrawl_thread(every_product_queue, every_data_queue):
    crawl_name = ['子網爬蟲1號']
    for name in crawl_name:
        sub_tcrawl = SubCrawlThread(name, every_product_queue, every_data_queue)
        subcrawl_list.append(sub_tcrawl)


def create_subparse_thread(every_data_queue,lock):
    parse_name = ['子網商品1號', '子網商品2號']
    for name in parse_name:
        sub_tparse = SubParseThread(name, every_data_queue, lock)
        subparse_list.append(sub_tparse)


def main():
    mkdir_data()
    lock = threading.Lock()
    # 創建列隊
    product_queue, data_queue, every_product_queue, every_data_queue = create_queue()
    # 創建執行緒
    create_crawl_thread(product_queue, data_queue)
    create_parse_thread(data_queue, every_product_queue)
    create_subcrawl_thread(every_product_queue, every_data_queue)
    create_subparse_thread(every_data_queue, lock)

    # 啟動執行緒
    for tcrawl in crawl_list:
        tcrawl.start()
    time.sleep(2)
    for tparse in parse_list:
        tparse.start()
    time.sleep(2)
    for sub_tcrawl in subcrawl_list:
        sub_tcrawl.start()
    time.sleep(2)
    for sub_tparse in subparse_list:
        sub_tparse.start()

    # 等待執行緒結束
    for tcrawl in crawl_list:
        tcrawl.join()
    for tparse in parse_list:
        tparse.join()
    for sub_tcrawl in subcrawl_list:
        sub_tcrawl.join()
    for sub_tparse in subparse_list:
        sub_tparse.join()
    print('Complete')


if __name__ == '__main__':
    main()
