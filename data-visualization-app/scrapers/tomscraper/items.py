# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TomArticle(scrapy.Item):
    agency = scrapy.Field()
    datePublished = scrapy.Field()
    articleSection = scrapy.Field()
    author = scrapy.Field()
    headline = scrapy.Field()
    link = scrapy.Field()
    sentiment_score = scrapy.Field()
    content = scrapy.Field()  # Add the content field
    is_political = scrapy.Field()
    image_url = scrapy.Field()