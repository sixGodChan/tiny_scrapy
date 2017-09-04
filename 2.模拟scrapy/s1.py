from twisted.web.client import getPage, defer
from twisted.internet import reactor


class ExecutionEngine:
    def __init__(self):
        self.running_list = []
        self.stop_deferred = None

    def onedone(self, response, url):
        print(response)
        self.running_list.remove(url)

    def check_empty(self,response):
        if not self.running_list:
            self.stop_deferred.callback(None)

    @defer.inlineCallbacks
    def open_spider(self, url):
        deferred2 = getPage(bytes(url, encoding='utf8'))
        deferred2.addCallback(self.onedone, url)
        deferred2.addCallback(self.check_empty)  # 第二个回调函数检测全局列表中是否有url
        yield deferred2

    @defer.inlineCallbacks
    def stop(self, url):
        self.stop_deferred = defer.Deferred()
        yield self.stop_deferred  # yield defer.Deferred()对象，会夯住


@defer.inlineCallbacks
def task(url):
    engine = ExecutionEngine()
    engine.running_list.append(url)

    yield engine.open_spider(url)
    yield engine.stop(url)


def all_done(arg):
    reactor.stop()


if __name__ == '__main__':
    ret = task("http://www.baidu.com")
    ret.addBoth(all_done)

    reactor.run()
