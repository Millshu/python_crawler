import requests
import json
from bs4  import BeautifulSoup
from urllib import request
import os
import threading
import time

def geturl(item,page_start,page_end,mkdir_name="toboo_img"):
    url = 'https://search.taobao.tw/catalog/?q=%s_keyori=ss&from=input&spm=a2w01.homepage.search.go.81fc55aaLDrY6H&page=%s' % (item.replace(
        "'", ''),page_start)
    for d in range(page_start,page_end+1):
        print(url)
        if not os.path.exists(r'./%s' % mkdir_name):  # r+字串:特殊字元,反斜線等無效
            os.mkdir(r'./%s' % mkdir_name)

        headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36',
                       }
        res=requests.get(url,headers=headers)
        soup=BeautifulSoup(res.text,'html.parser')
        b=soup.select('script[type="application/ld+json"]')[1].text
        json_soup=json.loads(b)
        url_select=json_soup['itemListElement']
        Marks = ['\\','/',':','*','?',"'",'<','>','|']
        #range(len(url_select))
        for i in range(len(url_select)):
            print(url_select[i]['url'])
            print(url_select[i]['name'])
            title = url_select[i]['name']
            for mark in Marks:
                if mark in title:
                    title=title.replace(mark,'')
            if not os.path.exists(r'./%s/%s' % (mkdir_name,title)):
                os.mkdir(r'./%s/%s' % (mkdir_name,title))

            try:
                res_2=requests.get((url_select[i]['url']),headers=headers)
                soup_2=BeautifulSoup(res_2.text,'html.parser')
                select_json_2=soup_2.select('script')[-5].text.split('app.run(')[1].split('\n')[0][:-2]
                soup_2_json=json.loads(select_json_2)
            except:
                print("找不到此網站的soup")
            img = img_select=soup_2_json['data']['root']['fields']['skuGalleries']['0']
            for l in range(len(img_select)):
                img_select=img[l]['poster']
                print(img_select)
                try:
                    request.urlretrieve(img_select, r'./%s/%s/%s' % (mkdir_name,title, title+str(l))+'.jpeg')
                except:
                    print("有錯誤")
            time.sleep(2)
        page=1+int(d)
        url='https://search.taobao.tw/catalog/?q=%s_keyori=ss&from=input&spm=a2w01.homepage.search.go.81fc55aaLDrY6H' % item.replace("'", '')
        url = url + '&page=' + str(page)
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>下一頁')




def json_uncode(a):
    b = a.encode('UTF-8')
    c = str(b)
    d = c.split("b'")[1].replace('\\', '%').replace('x', '').upper() + "&"
    return d

def job():
  for i in range(5):
    print("Child thread:", i)
    time.sleep(1)


''''''
start_page=int(input("輸入要爬的起始頁數:"))
end_page = int(input("輸入要爬到的頁數:"))
#url='https://search.taobao.tw/catalog/?q=%E4%B8%8A%E8%A1%A3&_keyori=ss&from=input&spm=a2w01.homepage.search.go.81fc55aaLDrY6H'  geturl(json_uncode('上衣'),start_page,end_page,mkdir_name='上衣')
url='https://search.taobao.tw/catalog/?q=%E7%A9%BF%E6%90%AD&_keyori=ss&from=input&spm=..search.go.'
a=input('請輸入你想查的產品關鍵字:')
search , mkdir = [(json_uncode('上衣'),'上衣'),(json_uncode('男裝'),'男裝')]
for i , d in search ,mkdir:
    t = threading.Thread(target=geturl,args=(i,start_page,end_page,d))
    t.start()

''''''
#t = threading.Thread(target = geturl,args=(json_uncode('上衣'),start_page,end_page,'上衣'))

geturl(json_uncode(a),start_page,end_page,mkdir_name=a)

t.join()