#! -*-coding:utf-8 -*-

from urllib import request, parse
from bs4 import BeautifulSoup as BS
import json
import datetime
import xlsxwriter
import time
import re
import urllib
import math

starttime = datetime.datetime.now()

url = r'https://www.lagou.com/jobs/positionAjax.json?city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false&isSchoolJob=0'
# 拉钩网的招聘信息都是动态获取的，所以需要通过post来递交json信息，默认城市为北京

tag = ['companyName', 'companyShortName', 'positionName', 'education', 'salary', 'financeStage', 'companySize',
       'industryField', 'companyLabelList']  # 这是需要抓取的标签信息，包括公司名称，学历要求，薪资等等

tag_name = ['公司名称', '公司简称', '职位名称', '所需学历', '工资', '公司资质', '公司规模', '所属类别', '公司介绍']


def read_page(url, page_num, keyword):  # 模仿浏览器post需求信息，并读取返回后的页面信息
    page_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch, br',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'www.lagou.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Cookie': 'user_trace_token=20170529170535-f9c2c61d-444d-11e7-9468-5254005c3644; PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html%3Fmsg%3Dvalidation%26uStatus%3D2%26clientIp%3D223.20.35.98; LGUID=20170529170535-f9c2ca34-444d-11e7-9468-5254005c3644; JSESSIONID=ABAAABAAADEAAFI755D3A01C2C01F7BBAD36A9C10003482; _gat=1; index_location_city=%E5%8C%97%E4%BA%AC; TG-TRACK-CODE=index_navigation; SEARCH_ID=f6eb83ea6f014ca5b22bad098089c4fa; _gid=GA1.2.1479464309.1496050214; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1496048733; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1496050214; _ga=GA1.2.1251572620.1496048733; LGSID=20170529170535-f9c2c89c-444d-11e7-9468-5254005c3644; LGRID=20170529173016-6c7f3d70-4451-11e7-b9f1-525400f775ce',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Referer' :'https://www.lagou.com/jobs/list_%E6%95%B0%E6%8D%AE%E5%88%86%E6%9E%90%E5%B8%88?labelWords=&fromSearch=false'
        }
    if page_num == 1:
        boo = 'true'
    else:
        boo = 'false'
    page_data = parse.urlencode([   # 通过页面分析，发现浏览器提交的FormData包括以下参数
        ('first', boo),
        ('pn', page_num),
        ('kd', keyword)
        ])
    
    req = request.Request(url,page_data.encode('UTF-8'),headers=page_headers)
    page = request.urlopen(req).read()
    page = page.decode('utf-8')
    return page


def read_tag(page, tag):
    
    page_json = json.loads(page)
    page_json = page_json['content']['positionResult']['result']  # 通过分析获取的json信息可知，招聘信息包含在返回的result当中，其中包含了许多其他参数
    page_result = [num for num in range(15)]  # 构造一个容量为15的list占位，用以构造接下来的二维数组
    for i in range(15):
        page_result[i] = []  # 构造二维数组
        for page_tag in tag:
            page_result[i].append(page_json[i].get(page_tag))  # 遍历参数，将它们放置在同一个list当中
        page_result[i][8] = ','.join(page_result[i][8])
    return page_result   # 返回当前页的招聘信息



def save_excel(fin_result, tag_name, file_name):  # 将抓取到的招聘信息存储到excel当中
    book = xlsxwriter.Workbook(r'C:\python app\%s.xls' % file_name)  # 默认存储在桌面上
    tmp = book.add_worksheet()
    row_num = len(fin_result)
    for i in range(1, row_num):
        if i == 1:
            tag_pos = 'A%s' % i
            tmp.write_row(tag_pos, tag_name)
        else:
            con_pos = 'A%s' % i
            content = fin_result[i-1]  # -1是因为被表格的表头所占
            tmp.write_row(con_pos, content)
    book.close()


if __name__ == '__main__':
    print('**********************************即将进行抓取**********************************')
    #keyword = '数据分析师'
    #keyword = '数据工程师'
    keyword = input('请输入要抓取的职位：')
    
    fin_result = []  # 将每页的招聘信息汇总成一个最终的招聘信息
    for page_num in range(1, 30):
        print('******************************正在下载第%s页内容*********************************' % page_num)
        page = read_page(url, page_num, keyword)
        page_result = read_tag(page, tag)
        fin_result.extend(page_result)
        time.sleep(12)
    file_name = input('抓取完成，输入文件名保存：')
    save_excel(fin_result, tag_name, file_name)
    endtime = datetime.datetime.now()
    time = (endtime - starttime).seconds
    print('总共用时：%s s' % time)