from __future__ import absolute_import
from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup as bs


class Scraping:

    def __init__(self, url, tag=None, class_=None, selector=None):
        self.url = url
        self.tag = tag
        self.class_ = class_
        self.selector = selector
        print("true")

    def scraping(self, range_num):
        data = []
        for i in range(1, range_num + 1):
            if i == 1:
                instance = requests.get(self.url)
            else:
                instance = requests.get(self.url + "?page=" + str(i))
            soup = bs(instance.text, "html.parser")
            text_list = soup.find_all(self.tag, attrs={"class": self.class_})

            for q in text_list:
                data.append(q.text)
        print("fin")
        return data


if __name__ == "__main__":
    jiro_scraping_text = Scraping("https://matome.naver.jp/odai/2139244522734938601", "p", "mdMTMWidget01ItemTxt01View")
    jiro_scraping_title = Scraping("https://matome.naver.jp/odai/2139244522734938601", "p", "mdMTMWidget01ItemTtl01View")

    body = jiro_scraping_text.scraping()
    title = jiro_scraping_title.scraping()
    print(title, body)