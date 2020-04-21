# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class CustomImageNamePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for (image_url, image_name) in zip(item[self.IMAGES_URLS_FIELD], item["image_name"]):
            yield scrapy.Request(
                url=image_url, meta={"image_name": image_name}, dont_filter=True)

    def file_path(self, request, response=None, info=None):
        image_name = request.meta["image_name"]
        return 'headshot/full/%s' % (image_name)

    def thumb_path(self, request, thumb_id, response=None, info=None):
        image_name = request.meta["image_name"]
        return 'headshot/%s/%s' % (thumb_id, image_name)
