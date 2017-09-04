from twisted.web.client import getPage, defer
from twisted.internet import reactor

# 5. 基于装饰器，执行完毕后停止事件循环

running_list = []
stop_deferred = None


def all_done(arg):
    reactor.stop()


def onedone(response, url):
    """
    执行完成，将url从全局列表中删除
    :param response: 
    :param url: 
    :return: 
    """
    print(response)
    running_list.remove(url)


def check_empty(response):
    """
    全局列表中没有值，主动终止
    :param response: 
    :return: 
    """
    if not running_list:
        stop_deferred.callback(None)


@defer.inlineCallbacks
def open_spider(url):
    deferred2 = getPage(bytes(url, encoding='utf8'))
    deferred2.addCallback(onedone, url)
    deferred2.addCallback(check_empty)  # 第二个回调函数检测全局列表中是否有url
    yield deferred2


@defer.inlineCallbacks
def stop(url):
    global stop_deferred
    stop_deferred = defer.Deferred()
    yield stop_deferred  # yield defer.Deferred()对象，会夯住


@defer.inlineCallbacks
def task(url):
    yield open_spider(url)

    yield stop()


# @defer.inlineCallbacks
# def task(url):
#     deferred2 = getPage(bytes(url, encoding='utf8'))
#     deferred2.addCallback(onedone, url)
#     deferred2.addCallback(check_empty)  # 第二个回调函数检测全局列表中是否有url
#     yield deferred2
#
#     global stop_deferred
#     stop_deferred = defer.Deferred()
#     yield stop_deferred  # yield defer.Deferred()对象，会夯住


running_list.append("http://www.baidu.com")  # 将url加入全局列表
ret = task("http://www.baidu.com")
ret.addBoth(all_done)

reactor.run()
