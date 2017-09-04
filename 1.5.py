#!/usr/bin/env python
# -*- coding:utf-8 -*-
from twisted.web.client import getPage, defer
from twisted.internet import reactor
import queue


class Request(object):
    def __init__(self, url, callback):
        self.url = url
        self.callback = callback


class Scheduler(object):
    def __init__(self, engine):
        self.q = queue.Queue()
        self.engine = engine

    def enqueue_request(self, request):
        self.q.put(request)

    def next_request(self):
        try:
            req = self.q.get(block=False)
        except Exception as e:
            req = None

        return req

    def size(self):
        return self.q.qsize()


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

        print(len(self.inprogress), self.scheduler.size())
        while len(self.inprogress) < 5 and self.scheduler.size() > 0:  # 最大并发数为5

            request = self.scheduler.next_request()
            if not request:
                break

            self.inprogress.add(request)
            d = getPage(bytes(request.url, encoding='utf-8'))
            d.addBoth(self._handle_downloader_output, request)
            d.addBoth(lambda x, req: self.inprogress.remove(req), request)
            d.addBoth(lambda x: self._next_request())

            if len(self.inprogress) == 0 and self.scheduler.size() == 0:
                self._closewait.callback(None)


def _handle_downloader_output(self, response, request):
    """
    获取内容，执行回调函数，并且把回调函数中的返回值获取，并添加到队列中
    :param response: 
    :param request: 
    :return: 
    """
    import types

    gen = request.callback(response)
    if isinstance(gen, types.GeneratorType):
        for req in gen:
            self.scheduler.enqueue_request(req)


@defer.inlineCallbacks
def start(self):
    self._closewait = defer.Deferred()
    yield self._closewait


@defer.inlineCallbacks
def open_spider(self, start_requests):
    self.start_requests = start_requests
    yield None
    reactor.callLater(0, self._next_request)


@defer.inlineCallbacks
def crawl(start_requests):
    engine = ExecutionEngine()

    start_requests = iter(start_requests)
    yield engine.open_spider(start_requests)
    yield engine.start()


def _stop_reactor(_=None):
    reactor.stop()


def parse(response):
    for i in range(10):
        yield Request("http://dig.chouti.com/all/hot/recent/%s" % i, parse)


if __name__ == '__main__':
    start_requests = [Request("http://www.baidu.com", parse), Request("http://www.baidu1.com", parse), ]

    ret = crawl(start_requests)

    ret.addBoth(_stop_reactor)

    reactor.run()
