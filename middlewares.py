# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os
import logging
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware
import random

logger = logging.getLogger(__name__)


class UserAgentMiddleware(object):
    """ 换User-Agent """

    def process_request(self, request, spider):
        """设置爬虫代理"""
        with open("E://proxy.txt", "r") as f:
            PROXIES = f.readlines()
            agent = random.choice(PROXIES)
            agent = agent.strip()
            request.headers["User-Agent"] = agent


class CookiesMiddleware(RetryMiddleware):
    """ 维护Cookie """

    def process_request(self, request, spider):
        pass

    def process_response(self, request, response, spider):
        if response.status in [300, 301, 302, 303]:
            try:
                reason = response_status_message(response.status)
                return self._retry(request, reason, spider) or response  # 重试
            except Exception as e:
                raise IgnoreRequest
        elif response.status in [403, 414]:
            logger.error("%s! Stopping..." % response.status)
            os.system("pause")
        else:
            return response

