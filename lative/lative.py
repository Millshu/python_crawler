import requests
import json
from urllib import request
import os
import multiprocessing as mp
import time

def mkdir_data (path='E:\專題\lativ\man_hotsale'):#創建資料夾path(為所要創建資料夾的路徑)
    if not os.path.exists(path):
        os.mkdir(path)

def mkdir_second(first_path,your_path_name):#創建第二個資料夾,第一個參數為你放置的第一個資料夾位置,第二個為你第二個資料夾的名字
    a=mkdir_data(first_path)
    second_path = first_path+ r'/' +your_path_name
    path = second_path#第二個資料夾的路徑位置
    if not os.path.exists(second_path):
        os.mkdir(second_path)
    return second_path

def replace_illegal_characters(string):
    list =['*','|','\\',':','\"','<','>','?','/']
    for c in list:
        string = string.replace(c, '')

    return string

def get_url (url ,headers,page_code=0):#拜訪網頁,如果url字串中有%s的話帶入page_code參數
    format_list=r'%s'
    if format_list in url:
        url = url % (page_code)
    res = requests.get(url, headers=headers)
    return res

def json_load(text_data):#將text轉換為json格式
    return json.loads(text_data)

def get_data (trun_data,path):
    recode_debug=set()
    try:
        if os.path.exists(path):
            with open(path + r'/' + 'recode.txt', 'r', encoding='utf-8') as f:
                for totle in f:
                    recode_debug.add(totle.replace('\n', ''))
    except:
        print("還未建立檢查資料集")
    product_name = trun_data['ProductName']
    product_color = trun_data['Color']
    product_price = trun_data['Price']
    product_ID = trun_data['ProductID']
    product_special_price = trun_data['ActivityPrice']
    product_img = 'https://s4.lativ.com.tw' + trun_data['image_140']
    if product_special_price == 0:
        tem_str = ''
        tem_str += '\n --- Product ID：%s ---\n' % (product_ID)
        tem_str += 'Product URL：%s\n' % (product_img)
        tem_str += 'Product Name: %s\n' % (product_name)
        tem_str += 'Product Color: %s\n' % (product_color)
        tem_str += 'Product Price: %s\n' % (product_price)
    else:
        tem_str = ''
        tem_str += '\n --- Product ID：%s ---\n' % (product_ID)
        tem_str += 'Product URL：%s\n' % (product_img)
        tem_str += 'Product Name: %s\n' % (product_name)
        tem_str += 'Product Color: %s\n' % (product_color)
        tem_str += 'Product Price: %s\n' % (product_price)
        tem_str += 'Product Special Price: %s' % (product_special_price)

    print(tem_str)
    #later_data.append(product_name)
    #print(later_data)
    title = replace_illegal_characters(str(product_name))

    if str(product_ID) not in str(recode_debug):
        path_dir_each = mkdir_second(path,your_path_name=title)
        get_jpg(product_img,path_dir_each=path_dir_each,waiting_write_data=tem_str,product_ID=product_ID)
    #request.urlretrieve(product_img, path_dir_each +r'/' +  r'/' + '%s' % product_img.split('/')[-1])

    # 圖案檔案存檔的語法  純棉圓領背心-男
    #with open(path_dir_each +r'/'+r'/' + str(product_ID) + '.txt', 'w', encoding='utf8') as f:
        #f.write(tem_str)
        return product_ID



'''
def page_url(page_start,page_end):

    url = 'https://www.lativ.com.tw/Product/GetNewProductCategoryList?MainCategory=MEN&pageIndex=%s&cacheID=32157'  # 給一個網址
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    for i in range(page_start,page_end):
        return get_url(url,headers,page_code=i)
'''
def get_jpg(product_img_url,path_dir_each,waiting_write_data,product_ID):#抓取圖片檔案及文字資料product_img(圖片的位置),path_dir_each(檔案放置的資料夾位置),waiting_write_data(等待輸入進去的資料),proudct_ID(檔案的名稱)

    request.urlretrieve(product_img_url, path_dir_each + '/' + '%s' % product_img_url.split('/')[-1])

    # 圖案檔案存檔的語法
    with open(path_dir_each + '/' + str(product_ID) + '.txt', 'w', encoding='utf8') as f:
        f.write(waiting_write_data)


def main(path,start_page,end_page):#r'C:\Users\USER\PycharmProjects\finalhomework\lativ'
    mkdir_data(path)
    colthes_tag = ['WOMEN','MEN','SPORTS']
    recode_debug = set()
    later_data = []
    try:
        if os.path.exists(path):
            with open(path + r'/' + 'recode.txt', 'r', encoding='utf-8') as f:
                for totle in f:
                    recode_debug.add(totle.replace('\n', ''))
    except:
        print("還未建立檢查資料集")
    for z in range(len(colthes_tag)):
        url = r'https://www.lativ.com.tw/Product/GetNewProductCategoryList?MainCategory=%s&pageIndex=%s&cacheID=32157' % (colthes_tag[z],'%s')   # 給一個網址
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>更換種類')
        for i in range(start_page,end_page):
            a=get_url (url ,headers,page_code=i)
            if a =='[]' or a==None :
                continue
            try:
                trun_data = json_load(a.text)
            except  Exception as e:
                print('頁數超過@@@@,已回到首頁',e)
                continue
            for b in trun_data:
                product_name=get_data(b,path=path)
                later_data.append(str(product_name)+'\n')
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>換頁爬取')
    try:
        for j in later_data:
            with open(path + r'/' + 'recode.txt', 'a', encoding='utf-8') as f:
                if j == 'None'+'\n':
                    continue
                f.write(str(j))
    except Exception as e :
        print(e)


if __name__ == '__main__':
    print ('Parent process %s.' % os.getpid())
    p = mp.Process(target=main, args=(r'./lativ',0,5))
    print('Process will start.')
    p.start()
    p.join()
    print('Process end.')
