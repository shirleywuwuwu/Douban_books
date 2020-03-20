# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

class BookListSpider(scrapy.Spider):
    name = 'book_list'
    allowed_domains = ['https://book.douban.com/']
    start_urls = ['https://book.douban.com/tag/%E6%8E%A8%E7%90%86?start='+str(i*20)+'&type=T' for i in range(50)]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self, response):
        soup_texts = BeautifulSoup(response.body, 'lxml')
        # 获取书籍数据
        soup_book_html = soup_texts.find_all("div", attrs={"class": "info"})
        for tag in soup_book_html:
            book_url = tag.find("a").attrs['href']  # 书籍url
            url_id = book_url.split("/")[-2]
            book_title = tag.find("a").attrs['title']  # 书籍名称
            book_pub = tag.find("div", class_="pub").get_text()
            book_pub = book_pub[15:len(book_pub) - 8]
            rate_comment = tag.find("div", class_="star clearfix")
            rating = rate_comment.find("span", class_="rating_nums").get_text()  # 豆瓣评分
            comment_num = rate_comment.find("span", class_="pl").get_text()
            num = comment_num[10:len(comment_num) - 9]  # 评论人数
            book_intro = tag.find("p").get_text()  # 内容简介

            yield {
                'url_id': url_id,
                'title': book_title,
                'pub': book_pub,
                'rating': rating,
                'num': num,
                'intro': book_intro,
            }
        pass
