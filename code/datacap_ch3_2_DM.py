# 导入模块
import numpy as np
import pandas as pd
import parsel
import requests
import chardet
import time
import json


# 3.2数据获取
# 设置爬虫代理，模拟用户行为
headers = {'User-Agent' : 'Mozilla/5.0'}
# 获取手机的商品编号,即url,后续将会依据商品编号爬取手机的销售数据和售后数据
all_product_number = pd.DataFrame(columns = ['商品编号'])
for i in range(1, 51):
    print('正在爬取第{}页的商品编号'.format(i))
    ur1 = 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&wq=%E6%89%8B%E6%9'\
    'C%BA&pvid=98798f7f8d414d11a96c285fd3bc53ce&page=' + str(i)
    rqg = requests.get(ur1, headers = headers, timeout = 10)
    rqg.encoding = chardet.detect(rqg.content)['encoding']
    html = rqg.content.decode('utf-8')
    selector = parsel.Selector(html)
    product_number = pd.DataFrame([])
    product_number['商品编号'] = selector.xpath('//div[@class="p-price"]/strong/i/@data-price').extract()
    all_product_number = pd.concat([all_product_number, product_number], axis = 0, ignore_index = True)

# 3.2.1爬取手机的销售数据
columns = ['店铺名称', '手机品牌', '商品编号', '商品名称', 'CPU型号', '后摄主摄像素',
           '前摄主摄像素', '系统', '商品评价量', '手机价格']
all_sales_data = pd.DataFrame(columns = columns)
for i in all_product_number['商品编号']:
    print('正在爬取商品编号为{}的商品信息'.format(i))
    ur1 = 'https://item.jd.com/' + i + '.html#product-detail'
    try:
        rqg = requests.get(ur1, headers = headers, timeout = 30)
    except requests.exceptions.ConnectionError:
        requests.status_codes = "Connection refused"
    rqg.encoding = chardet.detect(rqg.content)['encoding']
    html = rqg.content.decode('utf-8')
    selector = parsel.Selector(html)
    sales_data = pd.DataFrame([])
    sales_data['店铺名称'] = selector.xpath('//*[@id="crumb-wrap"]/div/div[2]/div[2]/div[1]/div/a/text()').extract()
    sales_data['手机品牌'] = selector.xpath('//ul[@class="p-parameter-list"]/li/a/text()').extract()
    details = selector.xpath('//ul[@class="parameter2 p-parameter-list"]/li/text()').extract()
    try:
        details_partition= dict(i.split('：') for i in details)
    except:
        continue
    for k in columns[2:8]:
        if k in details_partition:
            sales_data[k] = details_partition[k]
        else:
            sales_data[k] = None
    try:
        url = 'https://club.jd.com/comment/productPageComments.action?productId=' + i + '&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'
        rqg = requests.get(url, headers = headers, timeout = 5)
        page_text1 = json.loads(rqg.text)
        sales_data['商品评价量'] = page_text1['productCommentSummary']['commentCountStr']
    except:
        continue
    try:
        url = 'https://p.3.cn/prices/get?skuid=J_'+ i
        rqg = requests.get(url, headers = headers, timeout = 5)
        page_text2 = json.loads(rqg.text)[0]
        sales_data['手机价格'] = page_text2['p']
    except:
        continue
    all_sales_data = pd.concat([all_sales_data, sales_data], axis = 0, ignore_index = True)
    time.sleep(np.random.randint(5, 15))

# 存储手机销售数据
all_sales_data.to_csv('../tmp/手机销售数据.csv', encoding = 'gbk', index=None)



# 3.2.2爬取手机售后数据
# 自定义get_information函数，获取网页中的手机售后信息
def get_information(page, prod_id, score):
    url = 'https://club.jd.com/comment/productPageComments.action?'
    params = {
        'callback': 'fetchJSON_comment98',
        'productId': prod_id,
        'score': score,
        'sortType': 5,
        'page': page,
        'pageSize': 10,
        'isShadowSku': 0,
        'fold': 1,
    }
    cookie = 'shshshfpa=66205ea6-e9d4-2f19-9295-86972ef1331f-1614736117; shshshfpb=fzYtGMdjxFvkqWdHUPeW1SA%3D%3D; __jdu=16304875337921094432507; pinId=DzGEKa9dKc1vAKb_oSCq9A; pin=%E6%84%8F%E6%80%9Dsddas; unick=%E6%84%8F%E6%80%9Dsddas; _tp=gs1wDL2CI9C8erFAxZjUPd0AWTR98juqA5vOqXQBmDQ%3D; _pst=%E6%84%8F%E6%80%9Dsddas; user-key=bdcbff73-558f-4dd6-bcfe-d7f1a346c65d; ipLoc-djd=19-1601-50283-0; areaId=19; PCSYCityID=CN_440000_440100_440112; unpl=V2_ZzNtbURWERJyDhRRKRxfDWJUFlUSAhRHdwoVUS5OXQM1CxsJclRCFnUUR1xnGlkUZwcZXUBcRxRFCEdkeB5fA2AFEFlBZxBFLV0CFi9JH1c%2bbRBfRV5BEXQPTlNzKWwGZzMSXHJXRBd0DU9SfxteA28AElxKUkYXdgxHUkspWzVXMxpZQ1ZDEUUJdlVLWwhZZQUbWkJUDhVyCkdRch9YB2UFGl5CVksQcApFUHofbARXAA%3d%3d; __jdv=76161171|baidu-search|t_262767352_baidusearch|cpc|33683506969_0_70c667c4c4294f59adfc33b4df07c98e|1632467630760; jwotest_product=99; TrackID=1GYtPm0SGtO9GznRSdNU27_yjFx4cOfxUiSXh8Nvewvfs1kr-rvUmuchZJAf3TfOxcXCm7Qp6ZmUoed1Algc7md7nTx0ZfsSUtnTgZrHOx28; ceshi3.com=000; shshshfp=e80b3754f5e1e3c757aaffef158debc4; __jdc=122270672; __jda=122270672.16304875337921094432507.1630487534.1632545895.1632551195.37; token=e3bb41d82d72b884ffdfc75066bcd387,3,906973; __tk=iceJVxpORUnMV0jDiMoDVxPxWlaKWlROVZVOWUoFixnER0eJiMiLiX,3,906973; JSESSIONID=F42150FF55C4184D8D6EFB675CEC195E.s1; shshshsID=3c1d606d53e3be1a2cc9ab4c81210969_4_1632552980248; __jdb=122270672.4.16304875337921094432507|37.1632551195; thor=B34B76BD4A8C8329EB8825AD5436991FBB6ECA9F743DCE6F49944BF470FF861235EA163B1EE96FFC81D8AB28B987C3AF37669A969DDA068CC5AA64672657BB62029846708D0A6E548854946FAC064BEDBF38BED3FBBADC368E53D9789A0D91E2DE0EB68D8EED16FDD078EE86A341290712B1765AE9A7CEDEAECC1FF2A31DDC2FD9867F13A8D31069F4053916EF8344AA; 3AB9D23F7A4B3C9B=QIOYXNN3R4JOFMHQH4BNPMJMGRMQE4YYQ3JIFNHCSRNZACBMXIXA4UP5SMPTJGRZQWGMQ27KN3KJBUHYJT3BAI6JMM'
    cookies = {}
    # 将cookie转成字典结构
    for i in cookie.split(';'):
        key, value = i.split('=')
        cookies[key] = value
    np.random.seed(123)
    try:
        res = requests.get(url=url, headers=headers, params=params, cookies=cookies, timeout = 15)
        res.encoding = chardet.detect(res.content)['encoding']
    except requests.exceptions.ConnectionError:
        requests.status_codes = 'Connection refused'
    return res.text

# 自定义parse_information函数，解析网页中的手机售后数据
def parse_information(html):
    # 将爬取的网页数据转换成JSON格式
    tmp = html[len('fetchJSON_comment98('): -2]
    global data
    try:
    # 将JSON数据转换成字典
        data = json.loads(tmp, strict = False)
    except:
        pass
    all_after_sales_data = pd.DataFrame([])
    # 提取关键信息
    all_after_sales_data['评论文本'] = [i['content'] for i in data['comments']]   # 评论文本
    all_after_sales_data['评论时间'] = [i['creationTime'] for i in data['comments']]  # 评论时间
    all_after_sales_data['用户评分'] = [i['score'] for i in data['comments']]   # 用户评分
    all_after_sales_data['手机配色'] = [i['productColor'] for i in data['comments']]  # 手机配色
    all_after_sales_data['手机内存'] = [i['productSize'] for i in data['comments']]    # 商品规格
    all_after_sales_data['购买时间'] = [i['referenceTime'] for i in data['comments']]  # 购买时间
    return all_after_sales_data

# 调用Get_Information和Parse_Information自定义函数，按照比例循环爬取所需的手机售后数据
if __name__ == '__main__':
    # 各手机的商品编号
    info = [100008348542, 100014348492, 100009077475, 100026667910, 100032528220, 100014352539, 100018902008, 100016799388, 100018640842, 100016415677]
    # 1代表差评，2代表中评，3代表好评;10、50、100即对应1：5：10的比例
    scores = {1 : 10, 2 : 50, 3 : 100}
    after_sales_data = pd.DataFrame([])
    for prod_id in info[:]:
              for score in scores.keys():
                for page in range(scores[score]):
                    print(f'正在爬取第{prod_id, score, page}页'.center(50, '='))
                    html = get_information(prod_id=prod_id, score=score, page=page)
                    by_after_sales_data = parse_information(html)
                    after_sales_data = pd.concat([after_sales_data,
                                                  by_after_sales_data], ignore_index=True)
                    time.sleep(np.random.randint(3, 7))

# 存储手机售后数据
after_sales_data.to_csv('../tmp/手机售后数据.csv', encoding = 'gbk', index=None)