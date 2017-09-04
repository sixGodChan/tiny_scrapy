#!/usr/bin/env python
# -*- coding:utf-8 -*-
from twisted.web.client import getPage, defer
from twisted.internet import reactor

# 1. 基本使用
"""
def all_done(arg):
    reactor.stop()

def callback(contents):
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
"""


# 2. 基于装饰器（一）
"""
def all_done(arg):
    reactor.stop()


def onedone(response):
    print(response)


@defer.inlineCallbacks
def task(url):
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
"""


# 3. 基于装饰器（二）
"""
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
"""



# 4. 基于装饰器，永恒循环
"""
def all_done(arg):
    reactor.stop()


def onedone(response):
    print(response)


@defer.inlineCallbacks
def task():
    deferred2 = getPage(bytes("http://www.baidu.com", encoding='utf8'))
    deferred2.addCallback(onedone)
    yield deferred2

    stop_deferred = defer.Deferred()
    
    yield stop_deferred


ret = task()
ret.addBoth(all_done)

reactor.run()
"""


# 5. 基于装饰器，执行完毕后停止事件循环
"""
running_list = []
stop_deferred = None

def all_done(arg):
    reactor.stop()

def onedone(response):
    print(response)

def check_empty(response):
    if not running_list:
        stop_deferred.callback('......')

@defer.inlineCallbacks
def task(url):
    deferred2 = getPage(bytes(url, encoding='utf8'))
    deferred2.addCallback(onedone)
    deferred2.addCallback(check_empty)
    yield deferred2

    stop_deferred = defer.Deferred()
    yield stop_deferred


ret = task("http://www.baidu.com")
ret.addBoth(all_done)

reactor.run()
"""


# reactor.callLater(0) # 结束当前Deferred，事件循环也会终止



# 6. 基于装饰器，执行完毕后停止事件循环
"""
import queue

running_list = []
stop_deferred = None
q = queue.Queue()


def all_done(arg):
    reactor.stop()

def onedone(response):
    print(response)

def check_empty(response):
    if not running_list:
        stop_deferred.callback('......')


def open_spider():
    url = q.get()
    deferred = getPage(bytes(url, encoding='utf8'))
    deferred.addCallback(onedone)
    deferred.addCallback(check_empty)


@defer.inlineCallbacks
def task(start_url):
    q.put(start_url)
    open_spider()

    global stop_deferred
    stop_deferred = defer.Deferred()
    yield stop_deferred

li = []
ret = task("http://www.baidu.com")
li.append(ret)

lid = defer.DeferredList(li)
lid.addBoth(all_done)

reactor.run()
"""





