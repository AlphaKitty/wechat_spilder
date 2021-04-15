import wechatsogou
from cachelib import SimpleCache
import json


# 获取特定公众号信息
def get_gzh_info():
    # 直连
    ws_api = wechatsogou.WechatSogouAPI()
    info = ws_api.get_gzh_info('码猿技术专栏')
    print(json.dumps(info, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))


# 搜索公众号
def search_gzh():
    ws_api = wechatsogou.WechatSogouAPI()
    info = ws_api.search_gzh('码猿技术专栏')
    for item in info:
        print(json.dumps(item, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))


# 搜索公众号文章
def search_article(keyword):
    ws_api = wechatsogou.WechatSogouAPI()
    info = ws_api.search_article(keyword)
    for item in info:
        print(json.dumps(item, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))


# 联想关键词
def get_sugg():
    ws_api = wechatsogou.WechatSogouAPI()
    info = ws_api.get_sugg('Java')
    for item in info:
        print(json.dumps(item, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))


# 搜索热门文章
def get_gzh_article_by_hot():
    ws_api = wechatsogou.WechatSogouAPI()
    info = ws_api.get_gzh_article_by_hot('Java多线程')
    print(json.dumps(info, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))


# 搜索公众号文章历史
def get_gzh_article_by_history():
    ws_api = wechatsogou.WechatSogouAPI()
    info = ws_api.get_gzh_article_by_history('码猿技术专栏')
    print(json.dumps(info, sort_keys=True, indent=4, separators=(', ', ': '), ensure_ascii=False))


if __name__ == '__main__':
    # get_gzh_info()
    # search_gzh()
    search_article('Java多线程')
    # get_gzh_article_by_history()
    # get_gzh_article_by_hot()
    # get_sugg()

# # 验证码输入错误的重试次数，默认为1
# ws_api = wechatsogou.WechatSogouAPI(captcha_break_time=3)
#
# # 所有requests库的参数都能在这用
# # 如 配置代理，代理列表中至少需包含1个 HTTPS 协议的代理, 并确保代理可用
# ws_api = wechatsogou.WechatSogouAPI(proxies={
#     "http": "127.0.0.1:8888",
#     "https": "127.0.0.1:8888",
# })
#
# # 如 设置超时
# ws_api = wechatsogou.WechatSogouAPI(timeout=0.1)
