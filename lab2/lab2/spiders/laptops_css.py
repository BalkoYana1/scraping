import scrapy
from lab2.items import FacultyItem, DepartmentItem, NewsItem

class LaptopsSpider(scrapy.Spider):
    name = "laptops_css"
    allowed_domains = ["kpi.ua"]
    start_urls = ["https://kpi.ua/kpi_faculty"]

    def parse(self, response):
        main_container = response.css('div.main-container')
        if main_container:
            items = main_container.css('ul:nth-of-type(2) li')

            for li in items:
                a = li.css('a')
                name = li.css('a::text').get().strip()
                url = f"https://kpi.ua{li.css('a::attr(href)').get()}"
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
        field_item = response.css('div.field-item:nth-of-type(n+4):nth-of-type(-n+6) a')

        if field_item:
            for li in field_item:
                dep_name = li.css('::text').get()
                dep_url = f"https://kpi.ua{li.css('::attr(href)').get()}"
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
        news_list = response.css('div.item-list ul li div span')
        if news_list:
            for li in news_list:
                name = li.css('a::text').get()
                yield NewsItem(
                    name=name,
                    department=response.meta.get("department")
                )
