from twisted.web.client import getPage, defer
from twisted.internet import reactor


# 3. 基于装饰器（二）

def all_done(arg):
    reactor.stop()


def onedone(response):
    print(response)


@defer.inlineCallbacks
def task():
    deferred2 = getPage(bytes("http://www.baidu.com", encoding='utf8'))
    deferred2.addCallback(onedone)
    yield deferred2

    deferred1 = getPage(bytes("http://www.google.com", encoding='utf8'))
    deferred1.addCallback(onedone)
    yield deferred1


ret = task()
ret.addBoth(all_done)

reactor.run()
