# -*- coding: utf-8 -*-
#scrapy crawl book_comment

import scrapy
from bs4 import BeautifulSoup

class BookCommentSpider(scrapy.Spider):
    name = 'book_comment'
    #allowed_domains = ['https://book.douban.com/']
    start_urls = ['https://book.douban.com/tag/%E6%8E%A8%E7%90%86?start='+str(i*20)+'&type=T' for i in range(1)]

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

            #获取热门评论
            comment_urls = book_url+'comments/hot?p=1'
            yield scrapy.Request(url=comment_urls, meta={'url_id': url_id, 'title': book_title},
                                 callback=self.parse_comment)

    def parse_comment(self, response):
        soup_comment_texts = BeautifulSoup(response.body, 'lxml')
        url_id = response.meta['url_id']
        book_title = response.meta['title']

        # 获取页面评论数据
        soup_comment_html = soup_comment_texts.find_all("li", attrs={"class": "comment-item"})
        for tag in soup_comment_html:
            comment_info = tag.find("span", class_="comment-info")
            comment_user = comment_info.find("a").get_text()  # 评论者昵称
            comment_date = comment_info.find("span", class_="").get_text()  # 评论日期
            comment_text = tag.find("span", class_="short").get_text()  # 评论内容

            yield {
                'url_id': url_id,
                'title': book_title,
                'user': comment_user,
                'date': comment_date,
                'text': comment_text
            }

        # 获取下一页数据
        paginator = soup_comment_texts.find("ul", class_="comment-paginator")
        next_url_p = paginator.find_all("li", attrs={"class": "p"})[2]
        page_num = next_url_p.find("a").attrs['href'].split("=")[1]
        this_url = response.url.split("=")[0]
        next_url = this_url + '=' + page_num
        if next_url is not None and int(page_num) <= 5:
            yield scrapy.Request(url=next_url, meta={'url_id': url_id, 'title': book_title},
                                 callback=self.parse_comment)

        pass
