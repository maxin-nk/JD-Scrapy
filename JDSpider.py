# ! /usr/bin/env python
# coding:utf-8
# python interpreter:3.6.2
# author: admin_maxin

import re
import logging
import json
import requests
from scrapy import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from JDSpider.items import *
from bs4 import BeautifulSoup


# 电商平台可能的地址开头
key_word = ['book', 'e', 'channel', 'mvd', 'list']
Base_url = 'https://xxxx'
list_url = 'https://xxxx'
comment_url = 'https://xxxx'


class JDSpider(Spider):
    # 爬虫名称
    name = "JDSpider"
    # 允许爬取域名
    allowed_domains = ["jd.com"]
    # 起始URL
    start_urls = ['https://xxxx']
    # 将requests的日志级别设成WARNING
    logging.getLogger("requests").setLevel(logging.WARNING)

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        """获取分类页"""
        selector = Selector(response)
        try:
            texts = selector.xpath('//div[@class="category-item m"]/div[@class="mc"]/div[@class="items"]/dl/dd/a').extract()
            for text in texts:
                # 获取全部三级类目链接+三级类目名称
                items = re.findall(r'<a href="(.*?)" target="_blank">(.*?)</a>', text)
                for item in items:
                    # 判断“商品链接”是否需要继续请求
                    if item[0].split('.')[0][2:] in key_word:
                        if item[0].split('.')[0][2:] != 'list':
                            yield Request(url='https:' + item[0], callback=self.parse_category)
                        else:
                            # 记录一级类目：名称/可提数URL/id编码
                            categoriesItem = CategoriesItem()
                            categoriesItem['name'] = item[1]
                            categoriesItem['url'] = 'https:' + item[0]
                            categoriesItem['_id'] = item[0].split('=')[1].split('&')[0]
                            yield categoriesItem
                            meta = dict()
                            meta["category"] = item[0].split("=")[1]
                            yield Request(url='https:' + item[0], callback=self.parse_list, meta=meta)
        except Exception as e:
            print('error:', e)

        # # 测试
        # meta = dict()
        # meta["category"] = "1315,1343,9720"
        # yield Request(url='https://list.jd.com/list.html?cat=1315,1343,9720', callback=self.parse_list, meta=meta)

    def parse_list(self, response):
        """分别获得三级类目链接下的全部商品地址(涉及翻页)"""
        meta = dict()
        meta["category"] = response.meta["category"]

        # `Selector`是一个包装响应，用于选择其内容的某些部分
        selector = Selector(response)
        texts = selector.xpath('//*[@id="J_goodsList"]/ul/li/div/div[@class="p-img"]/a').extract()
        for text in texts:
            items = text.split("=")[3].split('"')[1]
            yield Request(url='https:' + items, callback=self.parse_product, meta=meta)

        # 翻页[仅翻前50页]
        maxPage = int(response.xpath('//div[@id="J_filter"]/div/div/span/i/text()').extract()[0])
        if maxPage > 1:
            if maxPage > 50:
                maxPage = 50
            for i in range(2, maxPage):
                num = 2*i - 1
                caterory = meta["category"].split(",")[0]+'%2C' + meta["category"].split(",")[1] + '%2C' + meta["category"].split(",")[2]
                url = list_url % (caterory, num, 30*num)
                print('products next page:', url)
                yield Request(url=url, callback=self.parse_list2, meta=meta)

        # # 测试
        # print('2')
        # yield Request(url='https://item.jd.com/53692850597.html', callback=self.parse_product, meta=meta)

    def parse_list2(self, response):
        """分别获得三级类目链接下的全部商品地址(涉及翻页)"""
        meta = dict()
        meta["category"] = response.meta["category"]

        # `Selector`是一个包装响应，用于选择其内容的某些部分
        selector = Selector(response)
        texts = selector.xpath('//*[@id="J_goodsList"]/ul/li/div/div[@class="p-img"]/a').extract()
        for text in texts:
            items = text.split("=")[3].split('"')[1]
            yield Request(url='https:' + items, callback=self.parse_product, meta=meta)

    def parse_product(self, response):
        """商品页获取title,price,product_id"""
        category = response.meta['category']
        productsItem = ProductsItem()
        shopItem = ShopItem()

        # 商品在售店铺id+店铺信息获取
        shopItem["shopName"] = response.xpath('//div[@class="m m-aside popbox"]/div/div/h3/a/text()').extract()[0]
        shopItem["_id"] = "https:" + response.xpath('//div[@class="m m-aside popbox"]/div/div/h3/a/@href').extract()[0]
        productsItem['shopId'] = shopItem["_id"]
        # 区分是否自营
        res = response.xpath('//div[@class="score-parts"]/div/span/em/@title').extract()
        if len(res) == 0:
            shopItem["shopItemScore"] = "京东自营"
            shopItem["shopLgcScore"] = "京东自营"
            shopItem["shopAfterSale"] = "京东自营"
        else:
            shopItem["shopItemScore"] = res[0]
            shopItem["shopLgcScore"] = res[1]
            shopItem["shopAfterSale"] = res[2]
            # shopItem["_id"] = response.xpath('//div[@class="m m-aside popbox"]/div/div/h3/a/@href').extract()[0].split("-")[1].split(".")[0]
        yield shopItem

        # 商品类目
        productsItem['category'] = category

        # 商品名称
        try:
            titles = response.xpath('//div[@class="sku-name"]/text()').extract()
            for tl in titles:
                if len(tl.replace(u"\xa0", "").strip()) > 4:
                    title = tl.replace(u"\xa0", "").strip()
                    productsItem['name'] = title
        except Exception as e:
            title = response.xpath('//div[@id="name"]/h1/text()').extract()[0]
            productsItem['name'] = title

        # 商品id
        product_id = response.url.split('/')[-1][:-5]
        productsItem['_id'] = product_id

        # 商品url
        productsItem['url'] = response.url

        # 商品描述
        desc = response.xpath('//div[@class="p-parameter"]/ul/li/text()|//div[@class="p-parameter"]/ul/li/a/text()').extract()
        productsItem['description'] = ';'.join(i.strip() for i in desc)

        # 商品累计评价数[response.text中的累计评价数消失了]
        productsItem['commentCount'] = response.xpath('//div[@id="comment-count"]/a/text()').extract()

        data = dict()
        data['product_id'] = product_id
        # 判断productsItem的类型
        yield productsItem
        # 将当前商品的第1页评论传递给parse_comments函数处理
        yield Request(url=comment_url % (product_id, '0'), callback=self.parse_comments, meta=data)

    def parse_comments(self, response):
        """
        获取商品评论
        :param response: 评论相应的json脚本
        :return:
        """
        try:
            data = json.loads(response.text)
        except Exception as e:
            print('get comment failed:', e)
            return None

        product_id = response.meta['product_id']

        # 商品评论概况获取[仅导入一次]
        commentSummaryItem = CommentSummaryItem()
        commentSummary = data.get('productCommentSummary')
        commentSummaryItem['_id'] = commentSummary.get('skuId')
        commentSummaryItem['productId'] = commentSummary.get('productId')
        commentSummaryItem['commentCount'] = commentSummary.get('commentCount')
        commentSummaryItem['score1Count'] = commentSummary.get('score1Count')
        commentSummaryItem['score2Count'] = commentSummary.get('score2Count')
        commentSummaryItem['score3Count'] = commentSummary.get('score3Count')
        commentSummaryItem['score4Count'] = commentSummary.get('score4Count')
        commentSummaryItem['score5Count'] = commentSummary.get('score5Count')
        yield commentSummaryItem

        # 商品评论[第一页，剩余页面评论由，parse_comments2]
        for comment_item in data['comments']:
            for comment_item in data['comments']:
                comment = CommentItem()
                comment['_id'] = str(product_id) + "," + str(comment_item.get("id"))
                comment['productId'] = product_id
                comment["guid"] = comment_item.get('guid')
                comment['score'] = comment_item.get('score')
                comment['nickname'] = comment_item.get('nickname')
                comment['plusAvailable'] = comment_item.get('plusAvailable')
                comment['content'] = comment_item.get('content')
                comment['creationTime'] = comment_item.get('creationTime')
                comment['replyCount'] = comment_item.get('replyCount')
                comment['usefulVoteCount'] = comment_item.get('usefulVoteCount')
                comment['imageCount'] = comment_item.get('imageCount')
                yield comment

            # 存储当前用户评论中的图片
            if 'images' in comment_item:
                for image in comment_item['images']:
                    commentImageItem = CommentImageItem()
                    commentImageItem['commentId'] = str(product_id) + "," + str(comment_item.get("id"))
                    commentImageItem['imgId'] = image.get('id')
                    commentImageItem['_id'] = str(product_id)+","+str(comment_item.get('id'))+","+str(image.get('id'))
                    commentImageItem['imgUrl'] = 'http:' + image.get('imgUrl')
                    commentImageItem['imgTitle'] = image.get('imgTitle')
                    commentImageItem['imgStatus'] = image.get('status')
                    yield commentImageItem

        # 评论翻页[尽量保证评分充足]
        max_page = int(data.get('maxPage', '1'))
        # if max_page > 60:
        #     # 设置评论的最大翻页数
        #     max_page = 60
        for i in range(1, max_page):
            url = comment_url % (product_id, str(i))
            meta = dict()
            meta['product_id'] = product_id
            yield Request(url=url, callback=self.parse_comments2, meta=meta)

    def parse_comments2(self, response):
        """获取商品comment"""
        try:
            data = json.loads(response.text)
        except Exception as e:
            print('get comment failed:', e)
            return None

        product_id = response.meta['product_id']

        for comment_item in data['comments']:
            comment = CommentItem()
            comment['_id'] = str(product_id)+","+str(comment_item.get("id"))
            comment['productId'] = product_id
            comment["guid"] = comment_item.get('guid')
            comment['score'] = comment_item.get('score')
            comment['nickname'] = comment_item.get('nickname')
            comment['plusAvailable'] = comment_item.get('plusAvailable')
            comment['content'] = comment_item.get('content')
            comment['creationTime'] = comment_item.get('creationTime')
            comment['replyCount'] = comment_item.get('replyCount')
            comment['usefulVoteCount'] = comment_item.get('usefulVoteCount')
            comment['imageCount'] = comment_item.get('imageCount')
            yield comment

            if 'images' in comment_item:
                for image in comment_item['images']:
                    commentImageItem = CommentImageItem()
                    commentImageItem['commentId'] = str(product_id) + "," + str(comment_item.get("id"))
                    commentImageItem['imgId'] = image.get('id')
                    commentImageItem['_id'] = str(product_id)+","+str(comment_item.get('id'))+","+str(image.get('id'))
                    commentImageItem['imgUrl'] = 'http:' + image.get('imgUrl')
                    commentImageItem['imgTitle'] = image.get('imgTitle')
                    commentImageItem['imgStatus'] = image.get('status')
                    yield commentImageItem