# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PachongItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    count = scrapy.Field()
    content = scrapy.Field()
    image_urls = scrapy.Field()
    reply_count = scrapy.Field()
    part_url = scrapy.Field()


class Reply(scrapy.Item):
    rep_content = scrapy.Field()
    rep_author_name = scrapy.Field()
