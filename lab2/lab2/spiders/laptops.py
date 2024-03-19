import scrapy
from bs4 import BeautifulSoup
from lab2.items import FacultyItem,DepartmentItem,NewsItem


class LaptopsSpider(scrapy.Spider):
    name = "laptops"
    allowed_domains = ["kpi.ua"]
    start_urls = ["https://kpi.ua/kpi_faculty"]

    def parse(self, response):
        soup = BeautifulSoup(response.body, "html.parser")
        main_container = soup.find(name="div", class_="main-container")

        if main_container:
            lists = main_container.select('div > ul')
            if len(lists) > 1:
                items = lists[1]
                for li in items.find_all("li"):
                    a = li.find("a")
                    name = a.find(string=True, recursive=False).strip()
                    url = f"https://kpi.ua{a.get('href')}"
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
                self.logger.warning("список не знайдено на сторінці.")
        else:
            self.logger.warning("Елемент з іменем класу 'main-container' не знайдено на сторінці.")

    def parse_faculty(self, response):
        soup = BeautifulSoup(response.body, "html.parser")
        field_item = soup.select(".field-item > a")[3:6]
        if field_item:
            for li in field_item:
                dep_name = li.find(string=True, recursive=False)
                dep_url = f"https://kpi.ua{li.get('href')}"
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
        soup = BeautifulSoup(response.body, "html.parser")
        news_list = soup.find(class_="item-list")
        if news_list:
            for li in news_list.find_all("li"):
                name = li.a.find(string=True, recursive=False)
                print(f"новини  {name}")
                if not name and li.span:
                    name = li.span.find(string=True, recursive=False)
                yield NewsItem(
                    name=name,
                    department=response.meta.get("department")
                )
