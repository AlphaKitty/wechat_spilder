# 请求网页
import datetime
import html
# json解析
import json
import time

# html转markdown
import html2text as ht
# 数据库
import pymysql
import requests
# 美化html
from bs4 import BeautifulSoup


class WechatSpider:

    def __init__(self, biz, cookie, offset, count, log_edit):
        self.biz = biz
        self.cookie = cookie
        self.offset = offset
        self.count = count
        self.total = 0
        self.author_id = ''
        self.author_name = ''
        self.spider_count = 0
        self.log_edit = log_edit
        self.home_url = 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=' + self.biz + '=='
        self.page_url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=' + self.biz + '==&offset=' + str(
            self.offset) + '&count=' + str(self.count)
        # self.author_name = ''
        # self.author_avatar = ''
        # self.author_profile = ''

    def get_html(self, url, header):
        response = requests.get(url, headers=header)
        response.encoding = 'utf8mb4'
        if response.status_code == 200:
            self.log_edit.insertPlainText("[√]网页请求成功" + "\n")
            print("[√]网页请求成功")
            if "<title>验证</title>" in response.text:
                raise Exception("需要验证 刷新网页填写必要信息后重试")
            return response.text

    def get_article_url_list(self, page_article_list_html, test):
        # 解析文章主页html
        self.log_edit.insertPlainText("[.]正在解析文章列表html..." + "\n")
        print("[.]正在解析文章列表html...")
        soup = BeautifulSoup(html.unescape(page_article_list_html).encode('utf8'), 'lxml')
        pretty = soup.prettify(formatter='html')
        try:
            # 拆出需要的文章列表json
            self.log_edit.insertPlainText("[.]正则提取文章列表json..." + "\n")
            print("[.]正则提取文章列表json...")
            # split = pretty.split(sep='var msgList = \'')[1].split(sep='\';')[0].replace('&quot;', '\"')
            split = pretty.split(sep='var msgList = \'')[1].split(sep='\';')[0]
            # 格式化json
            self.log_edit.insertPlainText("[.]转义json 等待插入数据库..." + r"\n")
            print("[.]转义json 等待插入数据库...")
            articles_json = json.loads(split)
            if len(articles_json.get('list')) != 0:
                if not test:
                    self.offset = self.offset + 10
                    self.change_page_url()
                    self.spider()
                else:
                    return [articles_json['list'][0]]
            else:
                pass
        except Exception as r:
            self.log_edit.insertPlainText("异常!" + str(r) + "\n")
            print("异常!" + str(r))
            return
        return articles_json['list']

    @staticmethod
    def has_class_but_no_id(tag):
        return tag.has_attr('data-recommend-type')

    def get_article(self, html_str):
        # 解析文章主页html
        soup = BeautifulSoup(html_str.encode('utf8'), 'lxml')
        # 删除所有往期推荐
        [s.extract() for s in soup.find_all(self.has_class_but_no_id)]
        # 删除所有代码块行号
        [s.extract() for s in soup.find_all("ul", {"class": "code-snippet__line-index code-snippet__js"})]
        # trimmed_soup = soup.find(self.has_class_but_no_id).decompose()
        # 获取js_content
        article_js_content = soup.find(id='js_content')
        pretty_content = BeautifulSoup(str(article_js_content), 'lxml').prettify(formatter='html')
        # 转成markdown
        text_maker = ht.HTML2Text()
        # 设置为true防止content中的大小括号等被转义
        # text_maker.convert_charrefs = True
        text_maker.skip_internal_links = False
        text_maker.br_toggle = '<br>'
        # unescape_content = html.unescape(pretty_content)
        # 这里肯定要自定义一下markdown
        article_content_markdown = text_maker.handle(pretty_content)
        escaped_article_content_markdown = pymysql.escape_string(article_content_markdown)
        return escaped_article_content_markdown

    def get_article_list_from_url_list(self, article_list_json):
        if article_list_json is None or article_list_json == '':
            return
        article_list = []
        for article_json in article_list_json:
            # 标题
            title_ = html.unescape(article_json['app_msg_ext_info']['title'])
            # 摘要
            digest_ = html.unescape(article_json['app_msg_ext_info']['digest'])
            # 内容url
            content_url_ = article_json['app_msg_ext_info']['content_url']
            # 封面
            cover_ = article_json['app_msg_ext_info']['cover']
            # 作者
            author_ = article_json['app_msg_ext_info']['author']
            # 发布时间(s时间戳)
            datetime_ = article_json['comm_msg_info']['datetime']
            # 标签
            tag_ = self.choose_tag(title_)
            # 应该可以用来文章去重
            # fakeid_ = article_json['comm_msg_info']['fakeid']
            # 来源网站
            source_url_ = article_json['app_msg_ext_info']['source_url']
            # 多文章
            multi_item_list_ = article_json['app_msg_ext_info']['multi_app_msg_item_list']
            for item in multi_item_list_:
                article = Article()
                article.title = html.unescape(item['title'])
                article.cover = item['cover']
                article.author = item['author']
                article.summary = html.unescape(item['digest'])
                article.tag = self.choose_tag(article.title)
                article.create_at = datetime.datetime.fromtimestamp(datetime_).strftime("%Y-%m-%d %H:%M:%S")
                article.include_at = datetime.datetime.fromtimestamp(round(time.time())).strftime("%Y-%m-%d %H:%M:%S")
                url_ = item['content_url']
                if url_.strip() == '':
                    continue
                article.content = self.get_article(self.get_html(url_, ''))
                article_list.append(article)
            if content_url_.strip() == '':
                continue
            html_str = self.get_html(content_url_, '')
            article = Article()
            article.title = title_
            article.cover = cover_
            article.author = author_
            article.summary = digest_
            article.tag = tag_
            article.create_at = datetime.datetime.fromtimestamp(datetime_).strftime("%Y-%m-%d %H:%M:%S")
            article.include_at = datetime.datetime.fromtimestamp(round(time.time())).strftime("%Y-%m-%d %H:%M:%S")
            article.content = self.get_article(html_str)
            article_list.append(article)
        return article_list

    # TODO 需要抽取公共方法 游标不参与循环 一次插入多条 https://www.cnblogs.com/jinbuqi/p/11588806.html
    def add_article_list_to_mysql(self, article_list):
        self.log_edit.insertPlainText("[.]正在插入数据库..." + "\n")
        print("[.]正在插入数据库...")
        if article_list is None:
            self.log_edit.insertPlainText("记录为0 直接返回" + "\n")
            print("记录为0 直接返回")
            return
        count = 0
        conn = self.get_mysql_connection()
        cursor = conn.cursor()
        for article in article_list:
            sql = "insert into article(title,cover,author_id,author_name,summary,create_at,include_at,tag,content) values(\'" + article.title + "\',\'" + article.cover + "\',\'" + str(
                self.author_id[0]) + "\',\'" + self.author_name + "\',\'" + article.summary + "\',\'" + str(
                article.create_at) + "\',\'" + article.include_at + "\',\'" + str(
                article.tag) + "\',\'" + article.content + "\'" + ")"
            # unescape_sql = html.unescape("sql&nbsp;")
            try:
                cursor.execute(sql)
            except Exception as r:
                if "Duplicate" in str(r):
                    self.log_edit.insertPlainText("[!]文章重复 已忽略" + "\n")
                    print("[!]文章重复 已忽略")
                    continue
            conn.commit()
            count = count + 1
            self.log_edit.insertPlainText("[√]当前页第" + str(count) + "次插入成功" + "\n")
            print("[√]当前页第" + str(count) + "次插入成功")
        self.total = self.total + count
        return count

    def add_user_to_mysql(self, user):
        try:
            self.log_edit.insertPlainText("[.]尝试插入作者信息..." + "\n")
            print("[.]尝试插入作者信息...")
            if user is None:
                return
            sql = "insert into user(nick_name,avatar,type,signature,qr_code,account) values(\'" + user.nickname + "\',\'" + user.avatar + "\',\'" + str(
                user.type) + "\',\'" + user.signature + "\',\'" + user.qr_code + "\',\'" + str(
                round(time.time() * 1000)) + "\'" + ")"
            conn = self.get_mysql_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

        except Exception as e:
            if "Duplicate" in str(e):
                self.log_edit.insertPlainText("[*]昵称为" + user.nickname + "的作者信息已存在" + "\n")
                print("[*]昵称为" + user.nickname + "的作者信息已存在")
        finally:
            conn = self.get_mysql_connection()
            cursor = conn.cursor()
            get_user_sql = "select id from user where nick_name = \'" + user.nickname + "\'"
            cursor.execute(get_user_sql)
            fetchone = cursor.fetchone()
            conn.commit()
            return fetchone

    @staticmethod
    def get_mysql_connection():
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            db='tagme3',
            port=3306,
            charset='utf8mb4',
        )
        return conn

    def resolve_and_add_to_mysql(self, article_list_json):
        self.log_edit.insertPlainText("[.]正在解析偏移量为" + str(self.offset) + "的页..." + "\n")
        print("[.]正在解析偏移量为" + str(self.offset) + "的页...")
        self.offset -= self.count
        # 根据文章列表json解析文章实体
        article_list = self.get_article_list_from_url_list(article_list_json)
        if article_list is None:
            self.log_edit.insertPlainText("[!]当前页文章数为0" + "\n")
            print("[!]当前页文章数为0")
            return
        # 把文章实体插入到数据库并返回个数
        self.log_edit.insertPlainText("[√]解析成功 共" + str(len(article_list)) + "条" + "\n")
        print("[√]解析成功 共" + str(len(article_list)) + "条")
        count = self.add_article_list_to_mysql(article_list)
        return count

    def get_header(self):
        header = {
            'Host': 'mp.weixin.qq.com',
            # 'authority': 'mp.weixin.qq.com',
            # 'cache-control': 'max-age=0',
            # 'upgrade-insecure-requests': '1',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36 Edg/87.0.664.47',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36 QBCore/4.0.1301.400 QQBrowser/9.0.2524.400 Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat',
            'accept': '*/*',
            'x-requested-with': 'XMLHttpRequest',
            # 'sec-fetch-site': 'none',
            # 'sec-fetch-mode': 'navigate',
            # 'sec-fetch-user': '?1',
            # 'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.5;q=0.4',
            'cookie': self.cookie
        }
        return header

    def change_page_url(self):
        self.page_url = 'https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=' + self.biz + '==&offset=' + str(
            self.offset) + '&count=' + str(self.count)

    # 二维码 头像 昵称 简介
    # var username = "" || "gh_6efb04887fe0";
    # var headimg = "http://wx.qlogo.cn/mmhead/Q3auHgzwzM7hYOzDrKzROyuqzoy9yFr1h3Eg43JPafqZ3ibywZT1jhw/0" || "";
    # var nickname = "码猿技术专栏".html(false) || "";
    # var __biz = "MzU3MDAzNDg1MA==";
    def get_author_info(self):
        try:
            header = self.get_header()
            # 根据微信文章列表url获取html
            home_article_list_html = self.get_html(self.home_url, header)
            soup = BeautifulSoup(home_article_list_html.encode('utf8'), 'lxml')
            # 简介
            profile = soup.find(class_="profile_desc").text.strip()
            # 二维码
            qr_code = "https://open.weixin.qq.com/qr/code?username=" + \
                      home_article_list_html.split(sep='var username = "" || "')[1].split(sep='";')[0]
            # 头像
            avatar = home_article_list_html.split(sep='var headimg = "')[1].split(sep='" || "";')[0]
            # 昵称
            nickname = home_article_list_html.split(sep='var nickname = "')[1].split(sep='".html(false) || "";')[0]
            user = User()
            user.signature = profile
            user.qr_code = qr_code
            user.avatar = avatar
            user.nickname = nickname
            user.type = 2
            author_id = self.add_user_to_mysql(user)
            self.author_id = author_id
            self.author_name = nickname
            self.log_edit.insertPlainText("[√]获取作者信息成功: " + nickname + "" + "\n")
            print("[√]获取作者信息成功: " + nickname + "")
        except Exception as r:
            raise Exception("获取作者信息失败: " + str(r) + "")

    def spider(self):
        self.spider_count += 1
        self.log_edit.insertPlainText("-----------------开始第 " + str(self.spider_count) + "次爬虫-----------------" + "\n")
        print("-----------------开始第 " + str(self.spider_count) + "次爬虫-----------------")
        self.log_edit.insertPlainText("页大小" + str(self.count) + ",偏移量" + str(self.offset) + "\n")
        print("页大小" + str(self.count) + ",偏移量" + str(self.offset))

        header = self.get_header()
        # 根据微信文章列表url获取html
        page_article_list_html = self.get_html(self.page_url, header)
        # 睡3秒 不然就封24h
        time.sleep(3)
        # 根据html获取文章列表的json
        article_list_json = self.get_article_url_list(page_article_list_html, False)
        # 根据文章列表json解析文章集合并存入数据库
        count = self.resolve_and_add_to_mysql(article_list_json)
        return count

    def test_spider(self):
        self.spider_count += 1
        self.log_edit.insertPlainText("-----------------开始第 " + str(self.spider_count) + "次爬虫-----------------" + "\n")
        print("-----------------开始第 " + str(self.spider_count) + "次爬虫-----------------")
        self.log_edit.insertPlainText("页大小" + str(self.count) + ",偏移量" + str(self.offset) + "\n")
        print("页大小" + str(self.count) + ",偏移量" + str(self.offset))

        header = self.get_header()
        # 根据微信文章列表url获取html
        page_article_list_html = self.get_html(self.page_url, header)
        # 根据html获取文章列表的json
        article_list_json = self.get_article_url_list(page_article_list_html, True)
        # 根据文章列表json解析文章集合并存入数据库
        count = self.resolve_and_add_to_mysql(article_list_json)
        return count

    @staticmethod
    def choose_tag(title_):
        lower = title_.lower()
        result = 4
        if '前端' in lower or 'html' in lower or 'css' in lower or 'jquery' in lower or 'ajax' in lower or 'vue' in lower or 'webpack' in lower or 'elementui' in lower:
            result = 32
        if '小程序' in lower:
            result = 61
        if '架构' in lower:
            result = 60
        if 'java' in lower or '新特性' in lower:
            result = 44
        if 'spring' in lower or '注解' in lower or 'aop' in lower or 'ioc' in lower or '动态代理' in lower or 'cglib' in lower:
            result = 17
        if '面试题' in lower:
            result = 26
        if 'java基础' in lower or '面向对象' in lower or 'list' in lower or 'collection' in lower \
                or 'hashmap' in lower or 'object' in lower or '数组' in lower \
                or '集合' in lower or 'stringbuffer' in lower or 'stringbuilder' in lower \
                or '循环' in lower or '抽象类' in lower or '切面' in lower or 'gc' in lower or 'oom' in lower or 'stream' in lower \
                or '反射' in lower or 'switch' in lower or ('if' in lower and 'else' in lower):
            result = 7
        if '职场经验' in lower:
            result = 8
        if '软件安装' in lower:
            result = 10
        if '线程' in lower or '锁' in lower or 'synchronized' in lower or 'thread' in lower or 'volatile' in lower:
            result = 13
        if '数据库' in lower or 'mysql' in lower or 'sql' in lower \
                or 'oracle' in lower or 'innodb' in lower \
                or 'truncate' in lower or 'explain' in lower \
                or ('索引' in lower and '搜索引擎' not in lower):
            result = 11
        if 'redis' in lower:
            result = 9
        if 'linux' in lower:
            result = 15
        if '编程习惯' in lower or ('try' in lower and 'catch' in lower) or '代码审查' in lower or '优雅' in lower:
            result = 16
        if 'maven' in lower:
            result = 19
        if 'swagger' in lower:
            result = 20
        if 'mq' in lower or '消息队列' in lower or '消息中间件' in lower:
            result = 21
        if '分布式' in lower:
            result = 27
        if '微服务' in lower:
            result = 22
        if 'docker' in lower:
            result = 23
        if 'nginx' in lower:
            result = 24
        if 'jvm' in lower:
            result = 28
        if '开源项目' in lower:
            result = 29
        if '高并发' in lower or '秒杀' in lower:
            result = 30
        if 'tomcat' in lower:
            result = 31
        if ('spring' in lower and 'mvc' in lower):
            result = 34
        if 'jwt' in lower:
            result = 36
        if 'elasticsearch' in lower:
            result = 37
        if '分库分表' in lower or '读写分离' in lower:
            result = 38
        if '算法' in lower:
            result = 39
        if 'spring' in lower and 'cloud' in lower:
            result = 40
        if '数据恢复' in lower:
            result = 41
        if 'vue' in lower:
            result = 42
        if 'http' in lower or '次握手' in lower:
            result = 43
        if '性能调优' in lower:
            result = 45
        if '网关' in lower:
            result = 46
        if '框架' in lower:
            result = 47
        if 'dubbo' in lower:
            result = 48
        if 'zookeeper' in lower:
            result = 49
        if 'restful' in lower:
            result = 50
        if '权限认证' in lower or 'oauth' in lower or 'jwt' in lower:
            result = 51
        if 'ssm' in lower:
            result = 52
        if 'eureka' in lower:
            result = 53
        if 'git' in lower:
            result = 54
        if '负载均衡' in lower:
            result = 55
        if 'security' in lower:
            result = 56
        if 'mongodb' in lower:
            result = 57
        if '源码' in lower:
            result = 58
        if '数据结构' in lower or '红黑树' in lower:
            result = 59
        if ('spring' in lower and 'boot' in lower) or '@auto' in lower:
            result = 14
        if '设计模式' in lower:
            result = 25
        if 'jenkins' in lower:
            result = 18
        if 'mybatis' in lower:
            result = 6
        if 'mybatis' in lower and 'plus' in lower:
            result = 62
        # 最后面
        if '插件' in lower or '工具' in lower or '热部署' in lower or '安装' in lower:
            result = 12
        return result


class Article:
    def __init__(self):
        self.title = ''
        self.cover = ''
        self.author = ''
        self.summary = ''
        self.content = ''
        self.create_at = ''
        self.tag = ''


class User:
    def __init__(self):
        self.nickname = ''
        self.avatar = ''
        self.type = ''
        self.signature = ''
        self.qr_code = ''
