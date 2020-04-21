# -*- coding: utf-8 -*-
import scrapy
import glob
import re
import pandas as pd
from tedspeaker.items import TedspeakerItem


class TedspeakerSpiderSpider(scrapy.Spider):
    name = 'tedspeaker_spider'
    allowed_domains = ['test.com']

    def start_requests(self):
        for filename in glob.glob('./*.xlsx'):
            df = pd.read_excel(filename)

        for url in df['URL']:
            url = url.strip()
            request = scrapy.Request(url, self.parse_info)
            request.meta['url'] = url
            yield request

    def parse_info(self, response):
        img_url = response.xpath(
            '//span[@itemprop="author"]/link[@itemprop="image"]/@href').getall()

        item = TedspeakerItem()
        item['URL'] = response.meta['url']
        item['image_urls'] = img_url
        item['image_name'] = ['%s.png' % re.findall(r'talks/(.*)$', response.url)[0]]
        yield item
