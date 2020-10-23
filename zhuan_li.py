#coding:utf-8
import csv
import json
import os
import random
import time
import datetime
import re
from bs4 import BeautifulSoup
from lxml import etree

import requests


def cha(city_one, city_two, date, csv_writer):
    head = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": "www.patenthub.cn",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "http://www.wanfangdata.com.cn",
        "Referer": "https://www.patenthub.cn/s?ds=cn&dm=mix&p=&ps=20&s=score%21&q2=&m=none&fc=%5B%7B%22type%22%3A%22countryCode%22%2C%22op%22%3A%22include%22%2C%22values%22%3A%5B%22CN%22%5D%7D%5D&q=%28ap%3A%28%E9%9D%92%E5%B2%9B%29+AND+ap%3A%28%E6%B5%8E%E5%8D%97%29%29+AND+%28ad%3A%5B2019-01-01+TO+2019-12-31%5D%29",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Cookie": 'T_ID=20201009124820eScDYtafPdHKEkTEgq; U_TOKEN=da3361cba07264464551fd1535ff0546740cc87a; s=RVEBUjxjA0lVfHYBByEUG1l4NzcTThQ0CSkYIAcAPQ8GLxEiNjwCMzMMAg4ZH09JGBIFCERJTi4VSigGDQM1SjdmfAsHWlRSFRBMQ1dBIxdGSVNfEENQGw==; Qs_lvt_241723=1602327913%2C1602739630; Qs_pv_241723=2844199901264264700%2C1598020803824542000; _nxid=94104; l=1; pref="ds:cn,s:score!,dm:mix_20"; Hm_lvt_7eea63afd346b9c6a715f0ead1cb45e9=1602218900,1602739631,1603281519; Hm_lpvt_7eea63afd346b9c6a715f0ead1cb45e9=1603281519'
    }
    pageNum = 1
    count = 1
    requests.packages.urllib3.disable_warnings()
    while True:
        hot = 'https://www.patenthub.cn/s?p={0}&'.format(count)
        url = hot + 'ps=20&q=(ag%3A(' + city_one + ')+AND+addr%3A(' + city_two + '))+AND+(dd%3A[' + date + '])&fc=[{"type"%3A"type"%2C"op"%3A"include"%2C"values"%3A["CN_发明公开"%2C"CN_发明授权"]}]'
        print(url)
        res = requests.get(url=url, headers=head)
        soup = BeautifulSoup(res.text, 'lxml')
        # 总数量
        sum_count = soup.select(".clearfix > div:nth-of-type(1) > span:nth-of-type(1)")[0].text
        print("本次查询总计有: %s数据" % sum_count)
        sum = int(sum_count.split('条')[0])
        if (sum > 20):
            if (sum > 1000):
                pageNum = 50
            else:
                if (sum & 20 != 0):
                    pageNum = int(sum / 20 + 1)
                else:
                    pageNum = sum / 20
        # 循环每个标签
        ul_text = soup.find_all('ul', class_="items")
        for ul_li in ul_text:
            # 公开号
            documentNumber = ul_li.find('label', string="公开(公告)号：").find_next_sibling('span').text
            # 标题
            title = ul_li.find('a', class_='patent-title').find('span', class_='dn').find_next_sibling('span').text
            # 申请日
            applicationDate = ul_li.find('label', string="申请日：").find_next_sibling('span').text
            # 总标题
            sum_title = "{} {}".format(documentNumber, title)
            # 公开日
            documentDate = ul_li.find('label', string="公开(公告)日：").find_next_sibling('span').text
            # IPC分类号
            ipc_id = ul_li.find_all('span', class_="ipc")
            if (len(ipc_id) > 1):
                ipc_conent = []
                for ipc in ipc_id:
                    ipc_conent.append(ipc.text)
            elif (len(ipc_id) == 1):
                ipc_conent = ipc_id[0].text
            else:
                ipc_conent = ""
            xiang_url = 'https://www.patenthub.cn/patent/%s.html?ds=cn' % documentNumber
            print("获取详情页: %s" % xiang_url)
            xiang_url_res = requests.get(url=xiang_url, headers=head)
            xiang_soup = BeautifulSoup(xiang_url_res.text, 'lxml')
            try:
                # 代理机构
                propy = xiang_soup.find('span', string="代理机构：").find_next_sibling('span').find('a').text
            except Exception as e:
                propy = ''
            # 申请（专利权）人
            highlight_target_text = xiang_soup.find_all('span', class_="-highlight-target-text")
            if (len(highlight_target_text) > 1):
                highlight = []
                for target in highlight_target_text:
                    highlight.append(target.text)
            elif (len(highlight_target_text) == 1):
                highlight = highlight_target_text[0].text
            else:
                highlight = ""
            # 申请人地址
            if xiang_soup.find('span', string="申请人地址：") is None:
                city = None
            else:
                city = xiang_soup.find('span', string="申请人地址：").find_next_sibling('span').text
            #city = xiang_soup.find('span', string="申请人地址：").find_next_sibling('span').text
            # 4. 写入csv文件内容
            if (city is not None):
                city = re.sub('\d+', '', city)
            print("start writing csv file")
            csv_writer.writerow(
                [city_one, city_two, applicationDate, documentDate, sum_title, ipc_conent, city, highlight, propy,
                 sum_count])
            time.sleep(random.randint(6, 9))
            print("writing csv file ok")
        time.sleep(random.randint(9, 14))
        if (count >= pageNum):
            count = 0
            break
        else:
            count = count + 1
            print("下次是第:%s页,一共有：%s页" % (count, pageNum))


if __name__ == '__main__':
    # video()
    city_sum = ["青岛", "济南", "烟台", "潍坊", "临沂", "济宁", "淄博", "威海", "东营", "日照", "泰安", "滨州", "枣庄", "德州", "聊城", "菏泽"]
    #文件名称跟当前系统时间相关，不会被覆盖掉
    path = os.getcwd() + '/2016-代理机构-申请人' + datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S') # fixed by lgy
    # 1. 创建文件对象
    f = open('%s.csv' % path, 'w+', encoding='utf-8', newline='' "")
    # 2. 基于文件对象构建 csv写入对象
    csv_writer = csv.writer(f)
    # 3. 构建列表头
    csv_writer.writerow(["代理机构", "申请人", "申请日", "公开公告日", "专利名称", "IPC分类号", "申请人地址", "申请(专利权)人", "代理机构信息", "数据总量"])
    for city_one in city_sum:
        flag = False
        for city_two in city_sum:
            if(flag == True):
                date = '2016-01-01+TO+2016-12-31'
                cha(city_one, city_two, date, csv_writer)
                print(city_one + '-' + city_two)
            if (city_one == city_two):
                flag = True

