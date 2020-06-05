import requests
from urllib import request
from bs4 import BeautifulSoup as bs
import os
import time
import threading
from queue import Queue
import random
import check_photo

crawl_list = []
parse_list = []
subcrawl_list = []
subparse_list = []
save_list = []
gender_list = ['MEN', 'WOMEN']


class CrawlThread(threading.Thread):
    def __init__(self, name, product_queue, main_html_queue):
        super(CrawlThread, self).__init__()
        self.name = name
        self.product_queue = product_queue
        self.main_html_queue = main_html_queue
        self.main_url = 'https://www.lativ.com.tw/{}/tops/{}'
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    def run(self):
        while 1:
            time.sleep(random.random()*5)
            print('-------{}啟動-------'.format(self.name))
            if self.product_queue.empty():
                #print("product_queue already empty")
                break
            else:
                #print("product_queue not yet empty")
                pass
            product = self.product_queue.get()
            for gender in gender_list:
                main_url = self.main_url.format(gender, product)
                #print(main_url)
                res = requests.get(main_url, headers=self.headers)
                self.main_html_queue.put(res.text)
            # print('主內容'+res.text)
        print('-------{}結束-------'.format(self.name))


class ParseThread(threading.Thread):
    def __init__(self, name, main_html_queue, main_url_queue):
        super(ParseThread, self).__init__()
        self.name = name
        self.main_html_queue = main_html_queue
        self.main_url_queue = main_url_queue

    def run(self):
        while 1:
            if self.main_html_queue.empty():
                time.sleep(30)
            else:
                #print("main_html_queue not yet empty")
                print('-------{}啟動-------'.format(self.name))
                main_html = self.main_html_queue.get()
                self.main_content(main_html)

            if self.main_html_queue.empty():
                #print("main_html_queue already empty")
                break
            else:
                pass

        print('-------{}結束-------'.format(self.name))


    def main_content(self, main_html):
        main_html_soup = bs(main_html, 'html.parser')
        every_product_list = main_html_soup.select('a[class="imgd"]')
        for every_product_id in range(len(every_product_list)):
            product_id = every_product_list[every_product_id]['href']
            self.main_url_queue.put(product_id)
            #print(product_id)


class SubCrawlThread(threading.Thread):
    def __init__(self, name, main_url_queue, sub_html_queue):
        super(SubCrawlThread, self).__init__()
        self.name = name
        self.main_url_queue = main_url_queue
        self.sub_html_queue = sub_html_queue
        self.every_product_url = 'https://www.lativ.com.tw{}'
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    def run(self):
        while 1:
            time.sleep(random.random()*5)
            if self.main_url_queue.empty():
                time.sleep(30)
            else:
                #print("main_url_queue not yet empty")
                # try:
                #     product_url = self.main_url_queue.get(True, 10)
                # except:
                #     break
                print('-------{}啟動-------'.format(self.name))
                product_id = self.main_url_queue.get()
                sub_url = self.every_product_url.format(product_id)
                #print('商品URL:' + sub_url)
                sub_res = requests.get(sub_url, headers=self.headers)
                self.sub_html_queue.put(sub_res.text)
                # print(sub_res.text)

            if self.main_url_queue.empty():
                #print("main_url_queue already empty")
                break
            else:
                pass
        print('-------{}結束-------'.format(self.name))

class SubParseThread(threading.Thread):
    def __init__(self, name, sub_html_queue, sub_url_queue):
        super(SubParseThread, self).__init__()
        self.name = name
        self.sub_html_queue = sub_html_queue
        self.sub_url_queue = sub_url_queue

    def run(self):
        while 1:
            print('-------{}啟動-------'.format(self.name))
            if self.sub_html_queue.empty():
                time.sleep(30)
            else:
                #print("sub_html_queue not yet empty")
                # try:
                #     every_product_data = self.sub_url_queue.get(True,10)
                # except:
                #     break
                sub_html = self.sub_html_queue.get()
                self.sub_content(sub_html)

            if self.sub_html_queue.empty():
                #print("sub_html_queue already empty")
                break
            else:
                pass
        print('-------{}結束-------'.format(self.name))

    def sub_content(self, sub_html):
        sub_html_soup = bs(sub_html, 'html.parser')
        every_product_img_list = sub_html_soup.select('div[class="oldPic show"] img')
        for num in range(len(every_product_img_list)):
            every_product_im_url= every_product_img_list[num]['data-original']
            #print('個別商品URL:' + every_product_im_url)
            self.sub_url_queue.put(every_product_im_url)


class SaveThread(threading.Thread):
    def __init__(self, name, sub_url_queue,lock):
        super(SaveThread, self).__init__()
        self.name = name
        self.sub_url_queue = sub_url_queue
        self.lock = lock

    def run(self):
        print('-------{}啟動-------'.format(self.name))
        while 1:
            if self.sub_url_queue.empty():
                time.sleep(30)
            else:
                #print("sub_url_queue not yet empty")
                img_url = self.sub_url_queue.get()
                id = img_url.split("/")[-1].split(".")[0]
                #print(id)
                print(img_url)
                self.lock.acquire()
                local = os.path.join('C:\\Users\\Big data\PycharmProjects\work2\lativ\head\{}.jpg'.format(id))
                try:
                    request.urlretrieve(img_url, local)
                    self.lock.release()
                except:
                    pass

            if self.sub_url_queue.empty():
                #print("sub_url_queue already empty".format(self.sub_url_queue))

                break
            else:
                pass
        print('-------{}結束-------'.format(self.name))

def mkdir_data(path=r'C:\Users\Big data\PycharmProjects\work2\lativ\head'):  # 創建資料夾path(為所要創建資料夾的路徑)
    if not os.path.exists(path):
        os.mkdir(path)


def create_queue():
    product_list = ['short_graphic_tee', 'long_graphic_tee', 'short_sleeves', 'long_sleeves', 'stand_collar', 'knit', 'polo', 'pima_m','pima_w', 'casual_shirt', 'business_shirt', 'flannel', 'sweats', 'fleece']
    product_queue = Queue()
    for product in product_list:
        product_queue.put(product)

    main_html_queue = Queue()
    main_url_queue = Queue()
    sub_html_queue = Queue()
    sub_url_queue = Queue()
    return product_queue, main_html_queue, main_url_queue, sub_html_queue, sub_url_queue


def create_crawl_thread(product_queue, main_html_queue):
    crawl_name = ['取得主網HTML:1號']
    for name in crawl_name:
        tcrawl = CrawlThread(name, product_queue, main_html_queue)
        crawl_list.append(tcrawl)


def create_parse_thread(main_html_queue, main_url_queue):
    parse_name = ['取得主網URL:1號', '取得主網URL:2號']
    for name in parse_name:
        tparse = ParseThread(name, main_html_queue, main_url_queue)
        parse_list.append(tparse)


def create_subcrawl_thread(main_url_queue, sub_html_queue):
    crawl_name = ['取得子網HTML:1號', '取得子網HTML:2號', '取得子HTML:3號', '取得子網HTML:4號', '取得子網HTML:5號']
    for name in crawl_name:
        sub_tcrawl = SubCrawlThread(name, main_url_queue, sub_html_queue)
        subcrawl_list.append(sub_tcrawl)


def create_subparse_thread(sub_html_queue, sub_url_queue):
    parse_name = ['取得子網URL:1號', '取得子網URL:2號']
    for name in parse_name:
        sub_tparse = SubParseThread(name, sub_html_queue, sub_url_queue)
        subparse_list.append(sub_tparse)

def create_save_thread(sub_url_queue,lock):
    save_name = ['儲存圖片:1號']
    for name in save_name:
        tsave = SaveThread(name, sub_url_queue,lock)
        save_list.append(tsave)

def main():
    start_time = time.time()
    mkdir_data()
    lock = threading.Lock()
    # 創建列隊
    product_queue, main_html_queue, main_url_queue, sub_html_queue, sub_url_queue = create_queue()

    # 創建執行緒
    create_crawl_thread(product_queue, main_html_queue)
    create_parse_thread(main_html_queue, main_url_queue)
    create_subcrawl_thread(main_url_queue, sub_html_queue)
    create_subparse_thread(sub_html_queue, sub_url_queue)
    create_save_thread(sub_url_queue, lock)

    # 啟動執行緒
    for tcrawl in crawl_list:
        tcrawl.start()
    time.sleep(2)
    for tparse in parse_list:
        tparse.start()
    time.sleep(2)
    for sub_tcrawl in subcrawl_list:
        sub_tcrawl.start()

    # 等待執行緒結束
    for tcrawl in crawl_list:
        tcrawl.join()
    for tparse in parse_list:
        tparse.join()
    for sub_tcrawl in subcrawl_list:
        sub_tcrawl.join()

    # 啟動執行緒
    for sub_tparse in subparse_list:
        sub_tparse.start()
    time.sleep(2)
    for tsave in save_list:
        tsave.start()

    # 等待執行緒結束

    for sub_tparse in subparse_list:
        sub_tparse.join()
    for tsave in save_list:
        tsave.join()
    check_photo.main()
    print('Complete')
    total_time = time.time() - start_time
    print(total_time)


if __name__ == '__main__':
    main()
