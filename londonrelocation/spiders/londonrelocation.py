import scrapy
from ..property import Property


class RentalScrapSpider(scrapy.Spider):
    name = 'rental_scrap'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']
    page_number = 1

    def parse(self, response):
        for start_url in self.start_urls:
            yield scrapy.Request(url=start_url,
                                 callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath('.//div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()

        for area_url in area_urls:
            yield scrapy.Request(url=area_url,
                                 callback=self.parse_area_pages)

    def parse_area_pages(self, response):
        # Write your code here and remove `pass` in the following line
        items = Property()
        all_div = response.css('.test-box')
        for item in all_div:
            title = item.css(".h4-space a::text").extract()[0]
            price = item.css("h5::text").extract()[0]
            link = item.css(".h4-space a::attr(href)").extract()[0]
            items["title"] = title

            if price.split(" ")[3] == 'pw':
                salary = round(365.25 / (7 * 12) * float(price.split(" ")[2]), 2)
            else:
                salary = float(price.split(" ")[2])

            items["price"] = salary

            items["link"] = "https://londonrelocation.com" + link

            yield items

        next_page = str(response.url) + "&pageset=" + str(RentalScrapSpider.page_number)
        if RentalScrapSpider.page_number < 3:
            RentalScrapSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse_area_pages)

        # an example for adding a property to the json list:
        # property = ItemLoader(item=Property())
        # property.add_value('title', '2 bedroom flat for rental')
        # property.add_value('price', '1680') # 420 per week
        # property.add_value('url', 'https://londonrelocation.com/properties-to-rent/properties/property-london/534465-2-bed-frognal-hampstead-nw3/')
        # return property.load_item()
