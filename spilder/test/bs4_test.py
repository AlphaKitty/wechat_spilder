# 请求网页
import bs4
import requests
# 解析xpath
from lxml import etree
# 美化html
from bs4 import BeautifulSoup, Comment
# 正则表达式
import re
# html转markdown
import html2text as ht


def get_html(url):
    response = requests.get(url)
    response.encoding = 'utf8'
    if response.status_code == 200:
        return response.text


def get_content(html):
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find(id='js_content')
    [s.extract() for s in content("script")]
    # 去除注释
    comments = content.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]
    pretty_content = BeautifulSoup(str(content).encode('utf8'), 'lxml')
    return pretty_content.prettify()


def example():
    # print(soup.prettify())
    # 获取文本
    # print(soup.h2.string.strip())
    # 修改属性
    # soup.p['class'] = "newClass"
    # 删除属性
    # del soup.p['class']
    # 判断内容是否为注释
    # if type(soup.a.string) == bs4.element.Comment:
    #     print(soup.a.string)
    # 列表形式输出子节点
    # print(soup.head.contents)
    # 列表索引获取子元素
    # print(soup.head.contents[1])
    # List形式
    # print(soup.body.children)
    # 遍历List
    # for child in soup.body.children:
    #     print(child)
    # 和children的区别是可以递归遍历
    # for child in soup.descendants:
    #     print(child)
    # 内容集合
    # for child in soup.div.strings:
    #     print(child)
    # 修剪后的内容集合
    # for child in soup.div.stripped_strings:
    #     print(child)
    # 直接和递归父节点
    # print(soup.div.parent.name)
    # for parent in soup.div.parents:
    #     print(parent.name)
    # 上一个和下一个兄弟节点
    # print(soup.div.next_sibling)
    # print(soup.div.previout_sibling)
    # 上面的和下面的全部兄弟节点
    # for sibling in soup.div.previous_siblings:
    #     print(sibling)
    # for sibling in soup.div.next_siblings:
    #     print(sibling)
    # 无视层级关系的上一个和下一个节点
    # print(soup.div.previous_element)
    # print(soup.div.next_element)
    # for element in soup.div.previous_elements:
    #     print(element)
    # for element in soup.div.next_elements:
    #     print(element)
    # 查找当前节点下的所有符合条件的子节点
    # print(soup.div.find_all('section'))
    # print(soup.div.find_all(['section', 'p']))
    # 根据正则表达式搜索
    # for tag in soup.find_all(re.compile('^b')):
    #     print(tag)
    # 返回所有tag名字
    # for tag in soup.find_all(True):
    #     print(tag.name)
    # 一个标签过滤器 可以作为find_all的参数 返回符合条件的标签
    # def has_class_but_no_id(tag):
    #     return tag.has_attr('class') and not tag.has_attr('id')
    # soup.find_all(has_class_but_no_id)
    # 搜索某个特定属性
    # print(soup.find_all(id='activity-name'))
    # 正则配合标签
    # soup.find_all(href=re.compile("elsie"))
    # 多个条件配合
    # soup.find_all(href=re.compile("elsie"), id='link1')
    # class是关键字 应该用class_
    # soup.find_all("a", class_="sister")
    # 特殊符号的需要用attr
    # soup.find_all(attrs={"data-foo": "value"})
    # 还可以搜索内容
    # soup.find_all(text="Elsie")
    # soup.find_all(text=["Tillie", "Elsie", "Lacie"])
    # soup.find_all(text=re.compile("Dormouse"))
    # limit限制返回个数
    # soup.find_all("a", limit=2)
    # 关闭默认的递归查找
    # soup.html.find_all("title", recursive=False)
    # 其他的还有:
    #           find(和find_all的区别是find直接返回第一个不返回列表 find和find_all都是模糊匹配)
    #           find_parent/find_parents
    #           find_next_sibling/find_next_siblings
    #           find_previous_sibling/find_previous_siblings
    #           find_next/find_all_next(element)
    #           find_previous/find_all_previous
    # find系列是模糊匹配 多个标签也会匹配 select是精准匹配 返回的是列表 可以直接过滤css
    # print(soup.find(class_='profile_nickname').text)
    # print(soup.select('.profile_nickname')[0].text)
    # print(soup.select('#activity-name')[0].text.strip())
    # 组合查找 多个条件同时满足 比如查找p标签下id为link1的标签等 中间要空格
    # print(soup.select('p #link1'))
    # print(soup.select("head > title"))
    # 组合查找内部标签 中间不空格
    # print(soup.select('a[class="sister"]'))
    # print(soup.select('a[href="http://example.com/elsie"]'))
    # 上面两种可以再组合 缩小范围
    # soup.select('p a[href="http://example.com/elsie"]')
    # text? get_text()?
    # print(soup.select('title')[0].get_text())

    # 去除属性script
    # [s.extract() for s in soup("script")]
    # 去除<div class="sup--normal“>
    # [s.extract() for s in soup.find_all("div", {"class": "sup--normal"})]

    # tree = etree.HTML(html)
    # title = tree.xpath('//*[@id="activity-name"]/text()')[0].strip()
    # public_from = tree.xpath('//*[@id="js_name"]/text()')[0].strip()
    # # span1 = tree.xpath('//*[@id="js_content"]/p[1]/strong/span/text()')[0].strip()
    # # span2 = tree.xpath('//*[@id="js_content"]/p[2]/strong/span/text()')[0].strip()
    # # span2 = tree.xpath('//*[@id="js_content"]/p[3]/text()')[0].strip()
    # spans = tree.xpath('//*[@id="js_content"]')[0]
    # print(title)
    # print(public_from)
    # print(spans)
    # print(span2)
    pass


def build_markdown(content):
    text_maker = ht.HTML2Text()
    # text_maker.bypass_tables = False
    text = text_maker.handle(content)
    # md = text.split('#')
    return text


def main():
    # 获取原html
    html = get_html(
        # 'https://mp.weixin.qq.com/s?__biz=MzkzODAwMTQwNw==&mid=2247492296&idx=1&sn=30e482203c7fcf924ce223dcca5dfa47')
        'https://mp.weixin.qq.com/s?__biz=MzU3MDAzNDg1MA==&mid=2247486231&idx=1&sn=e3624c839e8adfec6955dafd7460a5c2&chksm=fcf4d4dacb835dcc6db4573f218e0f5dcfb6b0a4df8396f42bc4e2704b5e92d9fa983a3863ad&scene=126&sessionid=1606669915&key=714c43c4e763db4243694020799bb2ac331c879a97e3850926760e3b9df66b1b1ce2bc8512e5d1cec4d15fe69dc2a4efddfa4a1e440bd732410b9c87f7378abcefeddb40ef5b173dc84c268386fa16abfd70e577da65682eea515ce1828f85eabd1c1986c50cb90313da55ba672281d99df4d50547cc156cd9d51f07227c10a2&ascene=1&uin=MTIxMTIwNjIzNA%3D%3D&devicetype=Windows+10+x64&version=6300002f&lang=zh_CN&exportkey=AxLQ%2F9XCYsuvZ0ktoXSnb7U%3D&pass_ticket=hosf1xh4gpEpplPyin9b6gopmtdGiNUaIPHikWi%2Fa%2FrVc8ApPyI9CKJ3dQPdJX2E&wx_header=0')
    # 'https://mp.weixin.qq.com/s?__biz=MzkzODAwMTQwNw==&mid=2247492267&idx=1&sn=e7865f9f836ed1555030f6a5a285e630&chksm=c284743bf5f3fd2dc975883f6a7e01485a3360d6addf96ef3ba7172c72691ff63e0e5d524d47&scene=126&sessionid=1606644497&key=12842f32187c232df23b9448e3e7611566a3cc9e10533522c37a82a1b2f386c31d85dfa4beab109eab7029b42d239c513679dc34fd3709128ea6975af57ee57e6fa1c73b5c05c17ce6475d154ba273c6283547f9efecf30409b95dd0e2437060b5c75109bedd3ba5dd49aa9f5042238d307e48d625eee3e8a84e01c3df075e78&ascene=1&uin=MTIxMTIwNjIzNA%3D%3D&devicetype=Windows+10+x64&version=6300002f&lang=zh_CN&exportkey=AzmxUtwhAhoK%2Fbib3EKsV5g%3D&pass_ticket=hosf1xh4gpEpplPyin9b6gopmtdGiNUaIPHikWi%2Fa%2FrVc8ApPyI9CKJ3dQPdJX2E&wx_header=0')
    content = get_content(html)
    # print(content)
    md = build_markdown(content)
    print(md)


if __name__ == '__main__':
    main()
