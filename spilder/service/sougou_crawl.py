import random
import re
import time
import uuid
from urllib.parse import urlencode, quote

import pymysql
import requests
from pyquery import PyQuery as pq


class TicketSpider:
    def __init__(self, url):
        self.url = url
        self.key = 'hello world'
        # quote:转义成带%前缀的url样式 这个url是搜狗微信请求的最简格式
        self.format_url = 'https://weixin.sogou.com/weixin?type=2&query={}'.format(quote(self.key))
        # User-Agent是必须要有的 不然骗不过目标网站
        self.headers_str = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77'
        self.a_str = '''
uigs_cl	first_click
uigs_refer	https://weixin.sogou.com/
uigs_productid	vs_web
terminal	web
vstype	weixin
pagetype	result
channel	result_article
s_from	input
sourceid	
type	weixin_search_pc
uigs_cookie	SUID,sct
query	hello world
weixintype	2
exp_status	-1
exp_id_list	0_0
wuid	0071440178DB40975D3C689EE37C6784
rn	1
login	0
uphint	1
bottomhint	1
page	1
exp_id	null_0-null_1-null_2-null_3-null_4-null_5-null_6-null_7-null_8-null_9
time	20914
'''
        self.b_data = self.str_to_dict()
        self.headers = self.headers_to_dict()

    def headers_to_dict(self):
        headers_str = self.headers_str.strip()
        # 把header字符串枚举化并转成字典
        headers_dict = dict((i.split(':', 1)[0].strip(), i.split(':', 1)[1].strip()) for i in headers_str.split('\n'))
        return headers_dict

    def str_to_dict(self):
        '''
        将a_str形式的字符串转化为字典形式；
        :param a_str:
        :return:
        '''
        str_a = list(i for i in self.a_str.split('\n') if i != '')
        str_b = {}
        for a in str_a:
            a1 = a.split('\t')[0]
            a2 = a.split('\t')[1]
            str_b[a1] = a2

        return str_b

    def get_suva(self, sunid):
        '''
        根据sunid来获取suv参数；并添加到cookie
        :param a: sunid
        :return:
        '''
        self.b_data['snuid'] = sunid.split('=')[-1]
        self.b_data['uuid'] = uuid.uuid1()
        self.b_data['uigs_t'] = str(int(round(time.time() * 1000)))
        url_link = 'https://pb.sogou.com/pv.gif?' + urlencode(self.b_data)
        res = requests.get(url_link)
        cookie_s = res.headers['Set-Cookie'].split(',')
        cookie_list_s = []
        for i in cookie_s:
            for j in i.split(','):
                if 'SUV' in j:
                    cookie_list_s.append(j)
                else:
                    continue
        print(cookie_list_s[0].split(';')[0])
        self.headers['Cookie'] = cookie_list_s[0].split(';')[0]

    # Todo snuid上限大概100次 可以每爬取50页就重新以无cookie身份去获取一次SNUID
    def get_first_parse(self):
        # 给headers中添加Referer参数 可以不填
        # headers['Referer'] = url_list
        res = requests.get(self.url, headers=self.headers)
        # 访问标准url 获取response中的Set-Cookie
        cookies = res.headers['Set-Cookie'].split(';')
        cookie_list_long = []
        cookie_list2 = []
        for cookie in cookies:
            cookie_list_long.append(str(cookie).split(','))
        for news_list_li in cookie_list_long:
            for set in news_list_li:
                if 'SUID' in set or 'SNUID' in set:
                    cookie_list2.append(set)
        sunid = cookie_list2[0].split(';')[0]
        self.get_suva(sunid)
        # 构造动态Cookies
        self.headers['Cookie'] = self.headers['Cookie'] + ';' + ';'.join(cookie_list2)
        news_list_lis = pq(res.text)('.news-list li').items()
        for news_list_li in news_list_lis:
            # 提取href属性标签 得到的url才是能够正确跳转的url
            href = pq(news_list_li('.img-box a').attr('href'))
            href = str(href).replace('<p>', '').replace('</p>', '').replace('amp;', '')
            # 构造参数k与h;
            b = int(random.random() * 100) + 1
            a = href.find("url=")
            result_link = href + "&k=" + str(b) + "&h=" + href[a + 4 + 21 + b: a + 4 + 21 + b + 1]
            whole_href = "https://weixin.sogou.com" + result_link
            logic_url = requests.get(whole_href, headers=self.headers).text
            #  获取真实url
            url_text = re.findall("\'(\S+?)\';", logic_url, re.S)
            best_url = ''.join(url_text)
            real_article_url = best_url.replace('&from=inner', '').replace("@", "")
            real_article_text = requests.get(url=str(real_article_url)).text
            print('------------------------------------------------------------------------------------')
            print('url: ' + real_article_url)
            print('标题: ' + pq(real_article_text)('#activity-name').text())
            print('图片: ' + pq(news_list_li('.img-box a img').attr('src')).text().split('url=')[1])
            print('时间戳: ' + pq(news_list_li('.txt-box div span script')).text().split('\'')[1])
            # 二维码链接不显示
            # print(pq(real_article_text)('.qr_code_pc_img').attr('src').text())
            print('作者: ' + pq(real_article_text)('#js_name').text())
            # print('发布时间: ' + pq(real_article_text)('.rich_media_meta_list').text())
            # print(pq(real_article_text)('#meta_content > span.rich_media_meta.rich_media_meta_text').text())


class DBAccessor:

    def __init__(self):
        self.conn = pymysql.connect(
            host='39.107.99.242',
            user='zyl',
            password='zyl',
            db='tagme',
            port=3306,
            charset='utf8mb4',
        )

    def exec(self, sql):
        cursor = self.conn.cursor()


if __name__ == '__main__':
    ticket = TicketSpider('https://weixin.sogou.com/weixin?type=2&query=%E8%B5%A0%E7%A5%A8')
    ticket.get_first_parse()
