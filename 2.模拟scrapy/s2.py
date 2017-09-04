#!/usr/bin/env python
# -*- coding:utf-8 -*-
from twisted.web.client import getPage, defer
from twisted.internet import reactor
import queue


# 将url和回调函数封装入request请求
class Request(object):
    def __init__(self, url, callback):
        self.url = url
        self.callback = callback


# 调度器
class Scheduler(object):
    def __init__(self, engine):
        self.q = queue.Queue()  # 初始化队列
        self.engine = engine

    def enqueue_request(self, request):
        """
        将一个url请求加入调度器队列
        :param request: 
        :return: 
        """
        self.q.put(request)

    def next_request(self):
        """
        从调度器队列那一个请求
        :return: 
        """
        try:
            req = self.q.get(block=False)
        except Exception as e:
            req = None

        return req

    def size(self):
        return self.q.qsize()

# 引擎
class ExecutionEngine(object):
    def __init__(self):
        self._closewait = None
        self.running = True
        self.start_requests = None
        self.scheduler = Scheduler(self)

        self.inprogress = set()

    def check_empty(self, response):
        if not self.running:
            self._closewait.callback('......')

    def _next_request(self):
        while self.start_requests:
            try:
                request = next(self.start_requests)
            except StopIteration:
                self.start_requests = None
            else:
                self.scheduler.enqueue_request(request)

        print(len(self.inprogress), self.scheduler.size())  # 正在执行中的任务，调度器中有几个任务
        while len(self.inprogress) < 5 and self.scheduler.size() > 0:  # 最大并发数为5

            request = self.scheduler.next_request()
            if not request:
                break

            self.inprogress.add(request)
            d = getPage(bytes(request.url, encoding='utf-8'))  # 请求页面
            d.addBoth(self._handle_downloader_output, request)  # 请求页面成功执行addCallback,请求失败执行addError，成功与否都执行addBoth
            d.addBoth(lambda x, req: self.inprogress.remove(req), request)  # 从正在运行的任务中删除
            d.addBoth(lambda x: self._next_request())  # 回调自己

        if len(self.inprogress) == 0 and self.scheduler.size() == 0:  # 正在执行中的任务=0，调度器中任务=0
            self._closewait.callback(None)  # 终止程序

    def _handle_downloader_output(self, response, request):
        """
        获取内容，执行回调函数，并且把回调函数中的返回值获取，并添加到队列中
        :param response: 
        :param request: 
        :return: 
        """
        import types

        gen = request.callback(response)
        if isinstance(gen, types.GeneratorType):  # 返回值是否为生成器
            for req in gen:
                # 此处可以判断：如果数request请求，加入队列，如果是item对象，加入pipeline
                self.scheduler.enqueue_request(req)  # request请求放入调度器

    @defer.inlineCallbacks
    def start(self):
        self._closewait = defer.Deferred()
        yield self._closewait  # 夯住

    @defer.inlineCallbacks
    def open_spider(self, start_requests):
        self.start_requests = start_requests
        yield None
        reactor.callLater(0, self._next_request)  # 等待0秒后执行函数_next_request


@defer.inlineCallbacks
def crawl(start_requests):
    """
    
    :param start_requests: 
    :return: 返回defer对象 
    """
    engine = ExecutionEngine()

    start_requests = iter(start_requests)  # start_requests列表做成迭代器
    yield engine.open_spider(start_requests)
    yield engine.start()


def _stop_reactor(_=None):
    reactor.stop()


count = 1


def parse(response):
    print(response)
    for i in range(10):
        yield Request("http://dig.chouti.com/all/hot/recent/%s" % i, parse)


if __name__ == '__main__':
    start_requests = [
        [Request("http://www.baidu.com", parse), ]
    ]

    ret = crawl(start_requests)

    ret.addBoth(_stop_reactor)

    reactor.run()
