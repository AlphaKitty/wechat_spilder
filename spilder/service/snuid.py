'''
获取SNUID的值
'''
import requests
import json
import time
import random

'''
方法（一）通过phantomjs访问sogou搜索结果页面，获取SNUID的值
'''


def phantomjs_getsnuid():
    from selenium import webdriver
    d = webdriver.PhantomJS('D:\python27\Scripts\phantomjs.exe', service_args=['--load-images=no', '--disk-cache=yes'])
    try:
        d.get("https://www.sogou.com/web?query=")
        Snuid = d.get_cookies()[5]["value"]
    except:
        Snuid = ""
    d.quit()
    return Snuid


'''
方法（二）通过访问特定url，获取body里面的id
'''


def Method_one():
    url = "http://www.sogou.com/antispider/detect.php?sn=E9DA81B7290B940A0000000058BFAB0&wdqz22=12&4c3kbr=12&ymqk4p=37&qhw71j=42&mfo5i5=7&3rqpqk=14&6p4tvk=27&eiac26=29&iozwml=44&urfya2=38&1bkeul=41&jugazb=31&qihm0q=8&lplrbr=10&wo65sp=11&2pev4x=23&4eyk88=16&q27tij=27&65l75p=40&fb3gwq=27&azt9t4=45&yeyqjo=47&kpyzva=31&haeihs=7&lw0u7o=33&tu49bk=42&f9c5r5=12&gooklm=11&_=1488956271683"
    headers = {"Cookie":
                   "ABTEST=0|1488956269|v17;\
                   IPLOC=CN3301;\
                   SUID=E9DA81B7290B940A0000000058BFAB6D;\
                   PHPSESSID=rfrcqafv5v74hbgpt98ah20vf3;\
                   SUIR=1488956269"
               }
    try:
        f = requests.get(url, headers=headers).content
        f = json.loads(f)
        Snuid = f["id"]
    except:
        Snuid = ""
    return Snuid


'''
方法（三）访问特定url，获取header里面的内容
'''


def Method_two():
    url = "https://www.sogou.com/web?query=333&_asf=www.sogou.com&_ast=1488955851&w=01019900&p=40040100&ie=utf8&from=index-nologin"
    headers = {"Cookie":
                   "ABTEST=0|1488956269|v17;\
                   IPLOC=CN3301;\
                   SUID=E9DA81B7290B940A0000000058BFAB6D;\
                   PHPSESSID=rfrcqafv5v74hbgpt98ah20vf3;\
                   SUIR=1488956269"
               }
    f = requests.head(url, headers=headers).headers
    print
    f


'''
方法（四）通过访问需要输入验证码解封的页面，可以获取SNUID
'''


def Method_three():
    '''
    http://www.sogou.com/antispider/util/seccode.php?tc=1488958062 验证码地址
    '''
    '''
    http://www.sogou.com/antispider/?from=%2fweb%3Fquery%3d152512wqe%26ie%3dutf8%26_ast%3d1488957312%26_asf%3dnull%26w%3d01029901%26p%3d40040100%26dp%3d1%26cid%3d%26cid%3d%26sut%3d578%26sst0%3d1488957299160%26lkt%3d3%2C1488957298718%2C1488957298893
    访问这个url，然后填写验证码，发送以后就是以下的包内容，可以获取SNUID。
    '''
    import socket
    import re
    res = r"id\"\: \"([^\"]*)\""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('www.sogou.com', 80))
    s.send('''
POST http://www.sogou.com/antispider/thank.php HTTP/1.1
Host: www.sogou.com
Content-Length: 223
X-Requested-With: XMLHttpRequest
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Cookie: CXID=65B8AE6BEE1CE37D4C63855D92AF339C; SUV=006B71D7B781DAE95800816584135075; IPLOC=CN3301; pgv_pvi=3190912000; GOTO=Af12315; ABTEST=8|1488945458|v17; PHPSESSID=f78qomvob1fq1robqkduu7v7p3; SUIR=D0E3BB8E393F794B2B1B02733A162729; SNUID=B182D8EF595C126A7D67E4E359B12C38; sct=2; sst0=958; ld=AXrrGZllll2Ysfa1lllllVA@rLolllllHc4zfyllllYllllljllll5@@@@@@@@@@; browerV=3; osV=1; LSTMV=673%2C447; LCLKINT=6022; ad=6FwTnyllll2g@popQlSGTVA@7VCYx98tLueNukllll9llllljpJ62s@@@@@@@@@@; SUID=EADA81B7516C860A57B28911000DA424; successCount=1|Wed, 08 Mar 2017 07:51:18 GMT; seccodeErrorCount=1|Wed, 08 Mar 2017 07:51:45 GMT
c=6exp2e&r=%252Fweb%253Fquery%253Djs%2B%25E6%25A0%25BC%25E5%25BC%258F%25E5%258C%2596%2526ie%253Dutf8%2526_ast%253D1488957312%2526_asf%253Dnull%2526w%253D01029901%2526p%253D40040100%2526dp%253D1%2526cid%253D%2526cid%253D&v=5
    ''')
    buf = s.recv(1024)
    p = re.compile(res)
    L = p.findall(buf)
    if len(L) > 0:
        Snuid = L[0]
    else:
        Snuid = ""
    return Snuid


def getsnuid(q):
    while 1:
        if q.qsize() < 10:
            Snuid = random.choice([Method_one(), Method_three(), phantomjs_getsnuid()])
            if Snuid != "":
                q.put(Snuid)
                print
                Snuid
                time.sleep(0.5)


if __name__ == "__main__":
    import Queue

    q = Queue.Queue()
    getsnuid(q)
