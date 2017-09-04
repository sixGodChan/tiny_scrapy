from twisted.web.client import getPage, defer
from twisted.internet import reactor


# 2. 基于装饰器（一）

def all_done(arg):
    reactor.stop()


def onedone(response):
    print(response)


@defer.inlineCallbacks
def task(url):
    """
    想要程序调用函数不阻塞，需要满足三要素：装饰器、deferred对象、yield deferred（Twisted标准写法）
    :param url: 
    :return: 
    """
    deferred = getPage(bytes(url, encoding='utf8'))
    deferred.addCallback(onedone)
    yield deferred


deferred_list = []

url_list = ['http://www.bing.com', 'http://www.baidu.com', ]
for url in url_list:
    deferred = task(url)
    deferred_list.append(deferred)

dlist = defer.DeferredList(deferred_list)
dlist.addBoth(all_done)

reactor.run()
