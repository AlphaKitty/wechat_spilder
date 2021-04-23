import random
import requests
from pyquery import PyQuery as pq
from urllib.parse import urlencode, quote
import uuid
import time
from lxml import etree
import re

key = 'hello world'
# quote:转义成带%前缀的url样式 这个url是搜狗微信请求的最简格式
format_url = 'https://weixin.sogou.com/weixin?type=2&query={}'.format(quote(key))

# User-Agent是必须要有的 不然骗不过目标网站
# headers_str = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
headers_str = 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36 Edg/89.0.774.77'


# headers_str = '''
# Host: weixin.sogou.com
# Connection: keep-alive
# Upgrade-Insecure-Requests: 1
# User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
# Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
# Accept-Encoding: gzip, deflate, br
# Accept-Language: zh-CN,zh;q=0.9
# '''


def headers_to_dict(headers_str):
    headers_str = headers_str.strip()
    # 把header字符串枚举化并转成字典
    headers_dict = dict((i.split(':', 1)[0].strip(), i.split(':', 1)[1].strip()) for i in headers_str.split('\n'))
    return headers_dict


a_str = '''
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


def str_to_dict(a_str):
    '''
    将a_str形式的字符串转化为字典形式；
    :param a_str:
    :return:
    '''
    str_a = list(i for i in a_str.split('\n') if i != '')
    str_b = {}
    for a in str_a:
        a1 = a.split('\t')[0]
        a2 = a.split('\t')[1]
        str_b[a1] = a2

    return str_b


b_data = str_to_dict(a_str)
headers = headers_to_dict(headers_str)


def get_suva(sunid):
    '''
    根据sunid来获取suv参数；并添加到cookie
    :param a: sunid
    :return:
    '''
    b_data['snuid'] = sunid.split('=')[-1]
    b_data['uuid'] = uuid.uuid1()
    b_data['uigs_t'] = str(int(round(time.time() * 1000)))
    url_link = 'https://pb.sogou.com/pv.gif?' + urlencode(b_data)
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
    headers['Cookie'] = cookie_list_s[0].split(';')[0]


# Todo snuid上限大概100次 可以每爬取50页就重新以无cookie身份去获取一次SNUID
def get_first_parse(url):
    '''
    1,构造'真'url;
    2,获取正确的动态cookie;
    3,返回真url,访问并解析文章内容
    :param url: 访问的初始url
    :return:
    '''
    # 给headers中添加Referer参数 可以不填
    # headers['Referer'] = url_list
    res = requests.get(url, headers=headers)
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
    get_suva(sunid)
    # 构造动态Cookies
    headers['Cookie'] = headers['Cookie'] + ';' + ';'.join(cookie_list2)
    news_list_lis = pq(res.text)('.news-list li').items()
    for news_list_li in news_list_lis:
        # 提取href属性标签
        href = pq(news_list_li('.img-box a').attr('href'))
        href = str(href).replace('<p>', '').replace('</p>', '').replace('amp;', '')
        # 构造参数k与h;
        b = int(random.random() * 100) + 1
        a = href.find("url=")
        result_link = href + "&k=" + str(b) + "&h=" + href[a + 4 + 21 + b: a + 4 + 21 + b + 1]
        a_url = "https://weixin.sogou.com" + result_link
        second_url = requests.get(a_url, headers=headers).text
        #  获取真实url
        url_text = re.findall("\'(\S+?)\';", second_url, re.S)
        best_url = ''.join(url_text)
        last_text = requests.get(url=str(best_url.replace('&from=inner', '').replace("@", ""))).text
        print('------------------------------------------------------------------------------------')
        print('url: ' + best_url.replace('&from=inner', '').replace("@", ""))
        print('标题: ' + pq(last_text)('#activity-name').text())
        # print(pq(last_text)('#js_content > p').text())
        # 二维码链接不显示
        # print(pq(last_text)('.qr_code_pc_img').attr('src').text())
        print('作者: ' + pq(last_text)('#js_name').text())
        # print('发布时间: ' + pq(last_text)('.rich_media_meta_list').text())
        # print(pq(last_text)('#meta_content > span.rich_media_meta.rich_media_meta_text').text())


if __name__ == '__main__':
    get_first_parse(
        'https://weixin.sogou.com/weixin?type=2&query=%E8%B5%A0%E7%A5%A8')
