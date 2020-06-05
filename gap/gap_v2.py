import datetime
import requests
import json
import os
import pandas as pd
from bs4 import BeautifulSoup
from urllib import request

# table表格用于储存书本信息
table = []
table1 = []

def replace_illegal_characters(string):
    mark = ['*', '|', '\\', ':', '\"', '<', '>', '?', '/']
    for r in mark:
        string = string.replace(r, '')
    return string


# 处理网页
def get_web(url, z, i):
    payloadData = {"data": {"conditionList": [{"key": "type", "value": ["0"], "valueType": "basic"},
                                              {"key": "saleStatus", "value": [1], "valueType": "basic"},
                                              {"key": "brandCode", "value": ["BR2019071600000003"],
                                               "valueType": "basic"},
                                              {"key": "parentCategoryCode", "value": z, "valueType": "basic"},
                                              {"key": "labelCode",
                                               "value": ["afd0be1fdd3e4b08a858c0f28e140170"],
                                               "valueType": "list"}],
                            "notIncludeSpuCodeList": [], "channelCode": 100, "storeCode": 1907038436},
                   "page": i,
                   "size": 32}

    payloadHeader = {"Host": "api.gap.tw", "Content-Type": "application/json;charset=UTF-8"}

    resp = requests.post(
        url,
        data=json.dumps(payloadData),
        headers=payloadHeader
    )
    if resp.status_code != 200:
        print('Invalid url:', resp.url)
        return None
    else:
        pass
    # 利用BeautifulSoup将获取到的文本解析成HTML
    soup = BeautifulSoup(resp.text, 'html.parser')
    js = json.loads(soup.text)
    js_data = js['data']['productList']
    return js_data


def download(js_data, pic_path, pic_gender):
    # 获取网页中的畅销书信息
    recode_debug = set()
    for product in js_data:
        try:
            if os.path.exists(pic_path):
                with open(pic_path +r'/'+ 'recode.txt', 'r', encoding='utf-8') as f:
                    for totle in f.readlines():
                        recode_debug.add(totle.replace('\n', ''))
        except:
            print("還未建立檢查資料集")
        id1 = product['spuCode']
        name = product["title"]
        price = product['listPrice']
        sale_price = product['salePrice']
        img_url = product['itemImageList'][0]['picUrl']
        date_1 = product['listTime']
        if date_1 is None:
            date = product['listTime']
        else:
            date = product['listTime']
        style = product['style']
        sales = product['sales']
        type_1 = product['attrList'][0]['attributeValueList']
        if type_1 is None:
            type1 = product['attrList'][0]['attributeValueList']
        else:
            type1 = product['attrList'][0]['attributeValueList'][0]["attributeValueFrontName"]
        color = product['attrSaleList'][0]['attributeValueList'][0]['attributeValueName']
        title = replace_illegal_characters(str(name))
        if id1 in recode_debug :
            print('ID有重複')
            continue
        else:
            if os.path.exists(pic_path):
                with open(pic_path + r'/' + 'recode.txt', 'a', encoding='utf-8') as f:
                    f.write(id1 + '\n')
                    print('ID沒有重複')

            a = id1
            b = title
            c = price
            d = sale_price
            e = style
            f = sales
            g = type1
            h = color
            i = date
            j = img_url
            table.append([a, b, c, d, e, f, g, h, i, j])

        path_dir_each = pic_path + '/' + pic_gender
        if not os.path.exists(path_dir_each):
            os.mkdir(path_dir_each)

        # 圖案檔案存檔的語法
        request.urlretrieve(j, path_dir_each + '/' + '%s' % a + '.jpg')



def path_dir(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
    return dir



if __name__ == '__main__':
    url = 'https://api.gap.tw/store/product/list/searchProductByCondition.do'
    gender = ['man', 'woman']
    gender_list = [["19082100002461"], ["19082100002378"]]
    gender_2 = [(["19082100002461"], 'man'), (["19082100002378"], 'woman')]
    # 统计该爬虫的消耗时间
    print('#' * 50)
    t1 = datetime.datetime.now()  # 开始时间
    page = 4
    p = r'./gap'
    # for z,y in gender_2:
    #     for j in range(0,page):
    #         print(z,y)
    #         try:
    #             js = get_web(url, z, j)
    #             path = path_dir(p)
    #             download(js, path, y)
    #             # 将table转化为pandas中的DataFrame并保存为CSV格式的文件
    #             df = pd.DataFrame(table,
    #                               columns=['id', 'name', 'price', 'sale_price', 'style', 'sales', 'type', 'color',
    #                                        'date', 'url'])
    #             print(df)
    #             df.to_csv(path + '/' + 'gap.csv', index=False)
    #         except:
    #              pass
    for q, manandwoman in zip(gender_list, gender):
        for cc in range(0, page):
            print(q, manandwoman)
            try:
                js = get_web(url, q, cc)
                path = path_dir(p)
                download(js, path, manandwoman)
                # 将table转化为pandas中的DataFrame并保存为CSV格式的文件
            except:
                pass
    df = pd.DataFrame(table, columns=['id', 'name', 'price', 'sale_price', 'style', 'sales', 'type', 'color',
                                      'date', 'url'])
    if os.path.exists(p+'/'+'gap1.csv'):
        df.to_csv(p + '/' + 'gap1.csv', mode='a+', index=False, encoding='utf-8', header=False)
    else:
        df.to_csv(p + '/' + 'gap1.csv', mode='a+', index=False, encoding='utf-8', header=True)

    # for z in gender_list:
    #     if z == ["19082100002461"]:
    #         for y in range(0, page):
    #             print('\n', '=== 第', y + 1, '頁 ====', '\n')
    #             print('ok')
    #             try:
    #                 js = get_web(url, gender_list[0], y)
    #                 path = path_dir(p)
    #                 download(js, path, gender[0])
    #                 # 将table转化为pandas中的DataFrame并保存为CSV格式的文件
    #                 df = pd.DataFrame(table,
    #                                   columns=['id', 'name', 'price', 'sale_price', 'style', 'sales', 'type', 'color',
    #                                            'date', 'url'])
    #                 df.to_csv(path + '/' + 'gap.csv', index=False)
    #                 print(df)
    #             except Exception as e:
    #                 print(e)
    #                 pass
    #     else:
    #         for y in range(0, page):
    #             print('\n', '=== 第', y + 1, '頁 ====', '\n')
    #             print('ok')
    #
    #             try:
    #
    #                 js = get_web(url, gender_list[1], y)
    #                 path = path_dir(p)
    #                 download(js, path, gender[1])
    #                 # 将table转化为pandas中的DataFrame并保存为CSV格式的文件
    #                 df = pd.DataFrame(table,
    #                                   columns=['id', 'name', 'price', 'sale_price', 'style', 'sales', 'type', 'color',
    #                                            'date', 'url'])
    #                 df.to_csv(path + '/' + 'gap.csv', index=False)
    #                 print(df)
    #             except Exception as e:
    #                 print(e)
    #                 pass
    t2 = datetime.datetime.now()  # 结束时间
    time_diff = t2 - t1
    # execution_time = time_diff.total_seconds()
    # print('共耗時' % execution_time)
    print('#' * 50)
'''

'''