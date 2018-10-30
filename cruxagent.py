#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import mimetypes
from mitmproxy import http


def getCacheList():
    listFileName = "cachelist.txt"
    if not os.path.exists(listFileName):
        with open("cachelist.txt", "a", encoding='utf8') as f:
            pass  # 仅创建文件
        return []  # 返回空列
    # read in the list file
    fd = open(listFileName, "r")
    raw_urls = fd.readlines()
    fd.close()

    urls = []
    for word in raw_urls:
        word = word.split("#")[0]  # 井号为注释符
        word = word.rstrip()
        if word != "":
            urls.append(word)
    return urls

def request(flow: http.HTTPFlow):
    urlpath = re.sub(r":/", "://", re.sub(r"/+", "/", flow.request.pretty_url))  # 规范路径   // --> /
    localpath = urlpath.split("#")[0].split("?")[0].split("://")[1]  # 提取路径部分
    fulllocalpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache',localpath )
    localreadflag = False
    # 读取CacheList, 如果存在就尝试从cache文件夹中直接读取文件。
    for regx in getCacheList():
        if re.match(regx, urlpath.split("?")[0]):
            localreadflag = True

    if localreadflag:
        # print("%s | 尝试本地获取资源..."%urlpath)
        # ipdb.set_trace()
        if os.path.exists(fulllocalpath):
            print("Read local file :: %s"%localpath)
            # getResFromLocal(flow, fulllocalpath)
            with open(fulllocalpath, 'rb') as fp:
                headers = {}
                fs = os.fstat(fp.fileno())
                # flow.response.headers("Content-Length", str(fs[6]))
                # flow.response.status_code = 200
                # flow.response.headers["content-type"] = mimetypes.guess_type(fulllocalpath.split("/")[-1])[0]
                headers["Content-Length"] = str(fs[6])
                headers["Content-type"] = mimetypes.guess_type(fulllocalpath.split("/")[-1])[0]
                flow.response = http.HTTPResponse.make(200, fp.read(), headers=headers)
                flow.intercept()
                flow.reply.ack()
                flow.reply.commit()
                # print(flow.response.content)
                # time.sleep(1)
                # print(flow.response.is_replay)
        else:
            pass
    else:
        pass

def response(flow : http.HTTPFlow):
    urlpath = re.sub(r":/", "://", re.sub(r"/+", "/", flow.request.pretty_url))  # 规范路径   // --> /
    localpath = urlpath.split("#")[0].split("?")[0].split("://")[1]  # 提取路径部分
    fulllocalpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache',localpath )
    localreadflag = False
    # 读取CacheList, 如果存在就尝试从cache文件夹中直接读取文件。
    for regx in getCacheList():
        if re.match(regx, urlpath.split("?")[0]):
            localreadflag = True

    if localreadflag:
        # print("%s | 保存到本地..."%urlpath)
        # ipdb.set_trace()
        if os.path.exists(fulllocalpath):
            # print("//本地文件已经存在")
            pass
        else:
            res_body = flow.response.content
            # print(flow.response.content)
            if res_body:
                try:
                    if not os.path.exists(os.path.dirname(fulllocalpath)):
                        os.makedirs(os.path.dirname(fulllocalpath), exist_ok=False)
                except:
                    pass
                try:  # 尝试保存
                    with open(fulllocalpath, mode="wb") as fp:
                        fp.write(res_body)
                    print("%s | 成功 --> %s" % (urlpath[:80], fulllocalpath))
                except Exception as e:
                    print("%s | 失败 XXX %s" % (urlpath[:80], str(e)))