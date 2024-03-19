import scrapy
from lab2.items import FacultyItem, DepartmentItem, NewsItem

class LaptopsSpider(scrapy.Spider):
    name = "laptops_xpath"
    allowed_domains = ["kpi.ua"]
    start_urls = ["https://kpi.ua/kpi_faculty"]

    def parse(self, response):
        main_container = response.xpath('//div[@class="main-container"]')
        if main_container:
            items = main_container.xpath('.//ul[2]/li')

            for li in items:
                a = li.xpath('//a')
                name = li.xpath('.//a/text()').get().strip()
                url = f"https://kpi.ua{li.xpath('.//a/@href').get()}"
                yield FacultyItem(
                    name=name,
                    url=url
                )
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_faculty,
                    meta={
                        "faculty": name
                    }
                )
        else:
            self.logger.warning("Елемент з іменем класу 'main-container' не знайдено на сторінці.")

    def parse_faculty(self, response):
        field_item = response.xpath('//div[@class="field-item" and position() >= 4 and position() <= 6]/a')

        if field_item:
            for li in field_item:
                dep_name = li.xpath('text()').get()
                dep_url = f"https://kpi.ua{li.xpath('@href').get()}"
                yield DepartmentItem(
                    name=dep_name,
                    url=dep_url,
                    faculty=response.meta.get("faculty")
                )
                yield scrapy.Request(
                    url=dep_url,
                    callback=self.parse_news,
                    meta={
                        "department": dep_name
                    }
                )

    def parse_news(self, response):
        news_list = response.xpath('//div[@class="item-list"]/ul/li/div/span')
        if news_list:
            for li in news_list:
                name = li.xpath('a/text()').get()
                yield NewsItem(
                    name=name,
                    department=response.meta.get("department")
                )


