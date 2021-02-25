import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from hypobank.items import Article


class HypobankSpider(scrapy.Spider):
    name = 'hypobank'
    start_urls = ['https://www.hypobank.ch/']

    def parse(self, response):
        articles = response.xpath('//a[@class="c-newsitem"]')
        for article in articles:
            link = article.xpath('./@href').get()
            date = article.xpath('./div[@class="c-newsitem__meta"]/text()').get()
            if date:
                date = date.strip().split()[0]

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//section[contains(@class,"c-textsection--events")]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
