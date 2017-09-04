from twisted.web.client import getPage, defer
from twisted.internet import reactor


# 4. 基于装饰器，永恒循环

def all_done(arg):
    reactor.stop()


def onedone(response):
    print(response)


@defer.inlineCallbacks
def task():
    deferred2 = getPage(bytes("http://www.baidu.com", encoding='utf8'))
    deferred2.addCallback(onedone)
    yield deferred2

    stop_deferred = defer.Deferred()  # defer.Deferred()对象
    # stop_deferred.callback(None)  # defer.Deferred()对象.callback(None),可以主动终止
    yield stop_deferred  # yield defer.Deferred()对象，会夯住


ret = task()
ret.addBoth(all_done)

reactor.run()
