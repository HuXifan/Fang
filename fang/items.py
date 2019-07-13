# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewhouseItem(scrapy.Item):
    # define the fields for your item here like:
    province = scrapy.Field()  # 省份
    city = scrapy.Field()  # 城市
    name = scrapy.Field()  # 小区名
    price = scrapy.Field()  # 价格
    rooms = scrapy.Field()  #居室 这是个列表
    area = scrapy.Field()  #面积
    address = scrapy.Field()  # 地址
    district = scrapy.Field()  # 行政区
    sale = scrapy.Field()  # 是否在售
    origin_url = scrapy.Field()  # 房天下详情页面的url


# 二手房item
class EsfItem(scrapy.Item):
    # define the fields for your item here like:
    province = scrapy.Field()  # 省份
    city = scrapy.Field()  # 城市
    name = scrapy.Field()  # 小区名
    price = scrapy.Field()  # 价格
    rooms = scrapy.Field()  # 居室,几室几厅这是个列表
    area = scrapy.Field()  # 建筑面积
    toward = scrapy.Field()  # 朝向
    address = scrapy.Field()  # 地址
    unit = scrapy.Field()  # 单价
    floor = scrapy.Field()  # 楼层
    year = scrapy.Field()  # 建成年代
    origin_url = scrapy.Field()  # 房天下详情页面的url
