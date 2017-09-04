from twisted.web.client import getPage, defer
from twisted.internet import reactor


# 1. 基本使用

def all_done(arg):
    """
    所有爬虫执行完成后，终止循环
    :param arg: 
    :return: 
    """
    reactor.stop()


def callback(contents):
    """
    每一个爬虫获取结果之后自动执行
    :param contents: 
    :return: 
    """
    print(contents)


deferred_list = []

url_list = ['http://www.bing.com', 'http://www.baidu.com', ]
for url in url_list:
    deferred = getPage(bytes(url, encoding='utf8'))
    deferred.addCallback(callback)
    deferred_list.append(deferred)

dlist = defer.DeferredList(deferred_list)
dlist.addBoth(all_done)

reactor.run()
