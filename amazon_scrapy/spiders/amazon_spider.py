# -*- coding: utf-8 -*-
import scrapy
from amazon_scrapy.items import AmazonItem
import scrapy, re
from function_library.function_library_all import write_json_utf8
from function_library.Redis_Class import *


class AmazonSpider(scrapy.Spider,Redis_class):
    def __init__(self):
        super().__init__()
        self.visited_set = []
        self.host="192.168.31.102"
        self.port="6379"
        self.db="13"

    #Redis_to_visit = Redis_Class("192.168.31.102", "6379", "14")
    #Redis_visited = Redis_class("192.168.31.102", "6379", "15")
    to_visit_url = set()
    visited_url = set()
    name = "amazon_spider"
    allowed_domains = ['amazon.com']
    # start_urls = ['https://www.amazon.com/Best-Sellers/zgbs/ref=zg_bs_tab']
    # start_urls = ['https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing-Beading-Jewelry-Making/zgbs/arts-crafts/12896081/']
    # start_urls = ['https://www.amazon.com/Best-Sellers-Arts-Crafts-Sewing-Beading-Cords-Threads/zgbs/arts-crafts/262593011']
    start_urls = ['https://www.amazon.com/Best-Sellers/zgbs/amazon-devices/ref=zg_bs_nav_0']
    def parse(self, response):
        import re
        if response.status != 200:
            write_json_utf8("fail.json", response.url)
            return 0
        else:
            try:
                try:
                    short_url = re.search("https://www.amazon.com/(\w|-)+/", response.url, re.IGNORECASE).group()
                except ImportError:
                    write_json_utf8("re_fail.json", response.url)
                    short_url = None
                # self.to_visit_url.remove(response.url)
                #self.visited_url.add(short_url)
                self.add_to_redis("15",short_url,"visited")

                #for each in self.get_keys_from_redis("15"):
                #    write_json_utf8("visited_url.json", each)
            except ImportError:
                pass

        items = self.get_best_sellers(response)
        for item in items:
            yield item
        try:
            if response.xpath('//*[@id="zg-center-div"]/div[2]/div/ul/li[4]/a/@href').extract()[0]:
                next_page_url = response.xpath('//*[@id="zg-center-div"]/div[2]/div/ul/li[4]/a/@href').extract()[0]
                yield scrapy.Request(next_page_url, callback=self.parse)
        except:
            pass
        urls = response.xpath('//*[@id="zg_browseRoot"]//li[*]/a/@href').extract()
        for url in urls:
            try:
                short_url = re.search("https://www.amazon.com/(\w|-)+/", url, re.IGNORECASE).group()
            except:
                short_url = None
                write_json_utf8("re_fail.json", url)
            if short_url not in self.get_keys_from_redis("15"):
                # self.to_visit_url.add(url)
                self.add_to_redis("14",url,"to_visit")
                for each in self.to_visit_url:
                    write_json_utf8("to_visit.json", short_url)
                # write_json_utf8("urls.json",url)
                yield scrapy.Request(url, callback=self.parse)

    def get_best_sellers(self, response):
        items = []
        if response.xpath('//*[@id="zg-ordered-list"]/li[*]'):
            pass

        for i in range(len(response.xpath('//*[@id="zg-ordered-list"]/li[*]'))):
            item = AmazonItem()
            item["category_name"] = response.xpath('//*[@id="zg-right-col"]/h1/span/text()').extract()
            item["category_url"] = response.url
            """
            if "no longer available" in response.xpath(
                    '//*[@id="zg-ordered-list"]/li[%s]/span/div/span/text()' % (i + 1)).extract_first():
                continue
            """
            upper_category = ""
            try:
                # for each in response.xpath('//*[@class="zg_browseUp"]/a/text()').extract():
                upper_category = "/".join(response.xpath('//*[@class="zg_browseUp"]/a/text()').extract())
            except:
                upper_category = "/"
            # upper_category = upper_category + "/" + \
            #                 response.xpath('//*[@id="zg_browseRoot"]//ul')[-1].xpath('./li/a/text()')[0].extract()
            item["upper_category"] = upper_category
            product_title = response.xpath(
                '//*[@id="zg-ordered-list"]/li[%s]/span/div/span/a/div/text()' % (i + 1)).extract_first()
            item["product_title"] = product_title
            try:
                item["ASIN"] = re.search("/\w{8,10}/", response.xpath(
                    '//*[@id="zg-ordered-list"]/li[%d]/span/div/span/a/@href' % (i + 1)).extract_first()).group().strip(
                    "/")
            except:
                item["ASIN"] = response.xpath(
                    '//*[@id="zg-ordered-list"]/li[%d]/span/div/span/a/@href' % (i + 1)).extract_first()
                item["price"] = "none"
            try:
                item["price"] = response.xpath(
                    '//*[@id="zg-ordered-list"]/li[%d]/span/div/span/div[2]/a/span/span/text()' % (
                            i + 1)).extract_first()
            except:
                item['price'] = "none"
            try:
                item["review_len"] = response.xpath(
                    '//*[@id="zg-ordered-list"]/li[%d]/span/div/span/div[1]/a[2]/text()' % (i + 1)).extract_first()
                item["review_rate"] = response.xpath(
                    '//*[@id="zg-ordered-list"]/li[%d]/span/div/span/div[1]/a[1]/i/span/text()' % (
                            i + 1)).extract_first()
            except:
                pass
            item["product_rank"] = response.xpath(
                '//*[@id="zg-ordered-list"]/li[%d]/span/div/div/span[1]/span/text()' % (i + 1)).extract_first()
            item['product_image'] = response.xpath(
                '//*[@id="zg-ordered-list"]/li[%d]/span/div/span/a/span/div/img/@src' % (i + 1)).extract_first()

            items.append(item)
        return items

    """
    import re
    item = DoubanItem()
    item["ASIN"] = "function"

    item["category_name"] = response.xpath('//*[@id="zg-right-col"]/h1/span/text()')
    item["category_url"] = response.url
    upper_category = ""
    try:
        for each in response.xpath('//*[@class="zg_browseUp"]/a/text()').extract():
            upper_category = upper_category + "/" + each
    except:
        upper_category = "/"
    item["upper_category"] = upper_category
    for product_item in response.xpath('//*[@id="zg-ordered-list"]/li[*]'):
        item["product_title"] = product_item.xpath('.//span/div/span/a/div/text()').extract()[0]
        #item["ASIN"] = product_item.xpath('//span/div/span/a/@href').extract()[0]
        # item["price"] =
        # item["review_len"] =
        # item["review_rate"] =
        # item["product_rank"] =
        return item
    """
