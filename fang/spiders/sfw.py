# -*- coding: utf-8 -*-
import re
import scrapy
from urllib.parse import urljoin
from fang.items import NewhouseItem, EsfItem


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
                # yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse, meta={'info': (province, city)})
                # 发送请求携带参数 meta 传入info元组（province，city)
                yield scrapy.Request(url=esf_url, callback=self.parse_esf, meta={'info': (province, city)})
                # break  #
            # break  #

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
            # print(name)  # 小区名称

            house_type_text = li.xpath(
                ".//div[contains(@class,'house_type')]/a/text()").getall()  # 返回居室的列表
            # house_type_text = list(map(lambda x: re.sub(r"\s", "", x),
            # house_type_text))  # 替换空字符
            rooms = list(
                filter(
                    lambda x: x.endswith("居"),
                    house_type_text))  # 过滤掉没有居室的小区 价格待定的
            # print(rooms)
            area = li.xpath(
                ".//div[contains(@class,'house_type')]/text()").getall()  # 得到一个列表
            area = "".join(area)  # 转换为字符串
            area = re.sub(r"\s|-|－|/", "", area)  # 使用re去除横线斜线

            address = li.xpath(".//div[@class='address']/a/@title").get()
            # print(address)
            # 保险起见
            district_text = "".join(
                li.xpath(".//div[@class='address']/a//text()").getall())
            # ()内是我们要提取的内容 只提取()中 group(1),group()提取所有内容
            district = re.search(r".*\[(.+)\].*", district_text).group(1)
            # print(district)  # 行政区

            # 是否在售
            sale = li.xpath(
                ".//div[contains(@class,'fangyuan')]/span/text()").get()
            # 价格 转换字符串
            price = "".join(
                li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price = re.sub(r"\s|广告", "", price)  # 除去空白字符，广告

            # 详情页url
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            origin_url = urljoin("https://", origin_url)  # 补全直辖市的url

            item = NewhouseItem(
                name=name,
                rooms=rooms,
                area=area,
                address=address,
                district=district,
                sale=sale,
                price=price,
                origin_url=origin_url,
                city=city,
                province=province)  # 传入item
            yield item  #

        next_url = response.xpath(
            "//div[@class='page']//a[@class='next']/@href").get()
        if next_url:  # 如果有下一页 继续请求,urljoin()保证url完整
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_newhouse,
                                 meta={'info': (province, city)})  # 循环调用自己

    # 解析二手房数据
    def parse_esf(self, response):
        province, city = response.meta.get('info')  # 解包拿到info信息
        dls = response.xpath(
            "//div[contains(@class,clearfix)]/dl[@dataflag='bg']")
        for dl in dls:
            item = EsfItem(province=province, city=city)  # 字典
            item['name'] = dl.xpath(".//p[@class='add_shop']/a/@title").get()  # 小区名称
            infos = dl.xpath(".//p[@class='tel_shop']/text()").getall()
            infos_list = map(
                lambda x: re.sub(
                    r"\s",
                    "",
                    x),
                infos)  # map对象转化为list
            # 得到列表 ['4室2厅', '115.2㎡', '中层（共18层）', '南向', '2018年建', ''],
            infos = list(infos_list)
            # 遍历infos，分开得到居室，楼层，朝向，建成年代等
            for info in infos:
                if ('室' or '栋' or '厅') in info:
                    item['rooms'] = info
                elif '㎡' in info:
                    item['area'] = info
                elif '层' in info:
                    item['floor'] = info
                elif '向' in info:
                    item['toward'] = info
                elif '年' in info:
                    item['year'] = info.replace("年建", "")

            # 获取地址
            item['address'] = dl.xpath(
                ".//p[@class='add_shop']/span/text()").get()

            price_infos = "".join(dl.xpath(".//dd[@class='price_right']/span//text()").getall())
            item['price'] = price_infos.split("万")[0] + "万"  # 总价
            item['unit'] = price_infos.split("万")[1]  # 单价
            # print(price, unit)  # 3600万 198074元/㎡

            # 获取详情页url
            detail_url = dl.xpath(".//dd/h4/a/@href").get()
            # origin_url = response.urljoin(detail_url)
            item['origin_url'] = response.urljoin(detail_url)

            yield item
        next_url = response.xpath("//div[@class='page_al']/p/a/@href").get()
        # next_url = response.urljoin(next_url)  # 打印出来是随机的 没有意义
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_esf,
                                 meta={'info': (province, city)})
