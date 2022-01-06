# ! /usr/bin/env python
# coding:utf-8
# python interpreter:3.6.2
# author: admin_maxin
from scrapy import Item, Field


class CategoriesItem(Item):
    """
    存储类目信息
    """
    name = Field()      # 商品三级类目名称
    url = Field()       # 商品三级类目对应url
    _id = Field()       # 商品类目对应id[一级id,二级id,三级id]


class ProductsItem(Item):
    """
    存储商品信息
    """
    name = Field()          # 商品名称
    url = Field()           # 商品url[用于商品主图提取]
    _id = Field()           # 商品sku
    category = Field()      # 商品三级类目
    description = Field()   # 商品描述
    shopId = Field()        # 商品所在店铺id(名称)
    commentCount = Field()  # 商品评价总数=CommentSummaryItem.commentCount
    # goodComment = Field()           # 商品好评数
    # generalComment = Field()        # 商品中评数
    # poolComment = Field()           # 商品差评数
    # favourableDesc1 = Field()       # 商品优惠描述1
    # favourableDesc2 = Field()       # 商品优惠描述2
    # venderId = Field()              # 供应商id
    # reallyPrice = Field()           # 商品现价
    # originalPrice = Field()         # 商品原价


class ShopItem(Item):
    _id = Field()                       # 店铺url
    shopName = Field()                  # 店铺名称
    shopItemScore = Field()             # 店铺[商品评价]
    shopLgcScore = Field()              # 店铺[物流履约]
    shopAfterSale = Field()             # 店铺[售后服务]


class CommentItem(Item):
    _id = Field()                       # 评论id[产品id,评论id]
    productId = Field()                 # 商品id=sku
    guid = Field()                      # 评论全局唯一标识符
    # firstCategory = Field()             # 商品一级类目
    # secondCategory = Field()            # 商品二级类目
    # thirdCategory = Field()             # 商品三级类目
    score = Field()                     # 用户评分
    nickname = Field()                  # 用户昵称
    plusAvailable = Field()             # 用户账户等级(201：PLUS, 103:普通用户，0：无价值用户)
    content = Field()                   # 评论内容
    creationTime = Field()              # 评论时间
    replyCount = Field()                # 评论的评论数
    usefulVoteCount = Field()           # 用户评论的被点赞数
    imageCount = Field()                # 评论中图片的数量


class CommentImageItem(Item):
    _id = Field()                       # 晒图对应id(1张图对应1个id)
    commentId = Field()                 # 晒图对应的评论id
    imgId = Field()                     # 晒图对应id
    imgUrl = Field()                    # 晒图url
    imgTitle = Field()                  # 晒图标题
    imgStatus = Field()                 # 晒图状态


class CommentSummaryItem(Item):
    """商品评论总结"""
    _id = Field()                       # 商品sku
    productId = Field()                 # 商品pid
    commentCount = Field()              # 商品累计评论数
    score1Count = Field()               # 用户评分为1的数量
    score2Count = Field()               # 用户评分为2的数量
    score3Count = Field()               # 用户评分为3的数量
    score4Count = Field()               # 用户评分为3的数量
    score5Count = Field()               # 用户评分为5的数量