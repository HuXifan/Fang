# -*- coding: utf-8 -*-
import re
import scrapy


class SfwSpider(scrapy.Spider):
    name = 'sfw'
    allowed_domains = ['fang.com']
    start_urls = ['https://www.fang.com/SoufunFamily.htm']  # 更改开始url

    def parse(self, response):
        trs = response.xpath("//div[@class='outCont']//tr")
        province = None  # 默认省份为None
        for tr in trs:

            # 找到没有class属性的td标签 即去除没有用的第一个td标签，不能使用class！=XX
            # 而是使用not(@class)没有class标签，否则其他td标签也不能获取
            tds = tr.xpath(".//td[not(@class)]")  # 每组有两个td 一组是省份 一组是第二行
            province_td = tds[0]
            province_text = province_td.xpath(".//text()").get()
            province_text = re.sub(r"\s", "", province_text)  # 替换空白字符
            if province_text:  # 如果第二个td标签有值 就是省份
                province = province_text  # 有就保存省份名称
            if province == "其它":  # 不爬取海外的国家
                continue

            # 没有还是使用之前的省份名
            city_td = tds[1]  # 城市td标签第1（有效的第二个）td
            city_links = city_td.xpath(".//a")  # 城市链接是td标签下的a标签
            for city_link in city_links:
                city = city_link.xpath(".//text()").get()  # 城市名
                city_url = city_link.xpath(".//@href").get()  # 城市url
                # 有了城市的url 就可以请求城市
                # print("省份：", province + "  城市：", city + "  城市链接：", city_url)

                # 1 构建新房的url链接
                url_module = city_url.split(".", 1)  # 第二个参数为 1，返回两个参数列表
                #  http://hf.fang.com/  -> ['http://hf','fang.com']
                scheme = url_module[0]  # https://hf
                if 'bj' in scheme:  # 判断北京特例
                    newhouse_url = "https://newhouse.fang.com/house/s/"
                    esf_url = "https://esf.fang.com/"
                else:
                    domain = url_module[1]  # fang.com
                    newhouse_url = scheme + ".newhouse." + domain + "house/s/"
                    # http://hf.newhouse.fang.com
                    # 2 构建二手房的url链接
                    esf_url = scheme + ".esf." + domain
                    # http://hf.esf.fang.com
                # print("城市：%s%s" % (province, city))
                # print("新房链接：", newhouse_url)
                # print("二手房链接：", esf_url)
                pass
                # 有了链接 返回继续请求
                yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse, meta={'info': (province, city)})
                # 发送请求携带参数 meta 传入info元组（province，city)
                yield scrapy.Request(url=esf_url, callback=self.parse_esf, meta={'info': (province, city)})
                break
            break

    # 解析新房数据
    def parse_newhouse(self, response):
        province, city = response.meta.get('info')  # 解包拿到info信息

        lis = response.xpath("//div[contains(@class,'nl_con')]/ul/li")
        for li in lis:
            name = li.xpath(".//div[@class='nlcd_name']/a/text()").get()
            if name:
                name = name.strip()
            else:  # 发现有多余的不含有用信息的li 过滤掉
                continue
            print(name)
            house_type_text = li.xpath(".//div[contains(@class,'house_type')]//a/text()").getall()  # 返回居室的列表

    # 解析二手房数据
    def parse_esf(self, response):
        province, city = response.meta.get('info')  # 解包拿到info信息
        pass
