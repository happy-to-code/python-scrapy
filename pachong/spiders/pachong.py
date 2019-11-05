# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request

from pachong.items import *


def del_replay(replay, replay_list):
    """
    处理回复的方法
    :param replay:
    :param replay_list:
    :return:
    """
    for rep in replay_list:
        re = Reply()

        rep_author_name = rep.xpath('tr/td[3]/strong/a/text()').get()
        rep_content = rep.xpath('tr/td[3]/div[4]/text()').get()
        # 处理以@回复的情况
        if str(rep_content).startswith("@"):
            name = rep.xpath('tr/td[3]/div[4]/a/text()').get()
            temp = rep.xpath('tr/td[3]/div[4]/text()[2]').get()

            rep_content = "@" + str(name) + str(temp)

        re['rep_author_name'] = rep_author_name
        re['rep_content'] = rep_content

        replay.append(re)

    # 将回复信息打印出来
    for rr in replay:
        print(rr)


class PachongSpider(scrapy.Spider):
    name = 'pachong'
    start_urls = ['https://www.v2ex.com/']

    def parse(self, response):
        list = response.xpath('//*[@id="TopicsHot"]/div[*]/table')

        for li in list:
            item = PachongItem()
            # 获取href
            part_url = li.xpath('tr/td[3]/span/a/@href').get()

            # 拼接URL
            url = 'https://www.v2ex.com' + part_url

            # 将此part_url存放到item中
            item['part_url'] = part_url

            # 访问新的URL
            req = Request(url, meta={'item': item}, callback=self.secondParse)
            yield req

    def secondParse(self, response):
        item = response.meta['item']
        # 标题
        title = response.xpath('//*[@id="Main"]/div[2]/div[1]/h1/text()').get()
        item['title'] = title
        # 作者
        author = response.xpath('//*[@id="Main"]/div[2]/div[1]/small/a/text()').get()
        item['author'] = author
        # 点击数
        contain_count = response.xpath('//*[@id="Main"]/div[2]/div[1]/small/text()').get()
        count = contain_count.split("·")[2].replace(" 次点击", "")
        item['count'] = count
        # 问题详情
        content = response.xpath("//div[@class='topic_content']").xpath('string(.)').get()
        if content == '':
            content = response.xpath("//div[@class='markdown_body']").xpath('string(.)').get()
        item['content'] = content
        # 头像图片
        image_urls = response.xpath('//*[@id="Main"]/div[2]/div[1]/div[1]/a/img/@src').get()
        item['image_urls'] = [f'https:{image_urls}']
        # 留言数量
        reply_count_str = response.xpath('//*[@id="Main"]/div[4]/div[1]/span').xpath('string(.)').get()
        reply_count = reply_count_str[0:reply_count_str.find(" 回复")]
        item['reply_count'] = reply_count

        # 留言
        replay = []
        # 1) 获取最大的分页数量
        page_count = response.xpath('//input[@class="page_input"]/@max').get()

        # 2) 再次解析回复
        if page_count is not None:
            for i in range(1, int(page_count)):
                page_url = 'https://www.v2ex.com' + item['part_url'] + '?p=' + str(i)
                yield Request(page_url, callback=self.pageParse(response, replay))
        else:
            # 只有一页
            people_reply = response.xpath('//*[@id="Main"]/div[4]/div[position()>1]/table')
            # 处理回复
            del_replay(replay, people_reply)

        print(
            "标题为:%s,作者为:%s,点击数:%s,头像图片地址:%s,正文为:%s,留言数量为:%s" % (title, author, count, image_urls, content, reply_count))

        yield item

    # 解析回复分页
    def pageParse(self, response, replay):
        replay_list = response.xpath('//*[@id="Main"]/div[4]/div[position()>2]/table')
        # 处理回复
        del_replay(replay, replay_list)
