# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TedspeakerItem(scrapy.Item):
    # define the fields for your item here like:
    URL = scrapy.Field()
    image_name = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()
