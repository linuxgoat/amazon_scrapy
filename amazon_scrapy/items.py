# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
    category_name=scrapy.Field()
    category_url=scrapy.Field()
    upper_category=scrapy.Field()
    product_title=scrapy.Field()
    ASIN=scrapy.Field()
    price=scrapy.Field()
    review_len=scrapy.Field()
    review_rate=scrapy.Field()
    product_rank=scrapy.Field()
    product_image=scrapy.Field()
    res=scrapy.Field()
