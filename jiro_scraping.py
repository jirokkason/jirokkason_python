from __future__ import absolute_import
from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup as bs
import sqlite3


class Scraping:

    DB_PATH = "jirokkason.db"
    DB_SCHEMA_PATH = "jiro_copype_schema.sql"

    def __init__(self, url=None, tag=None, class_=None, selector=None, range_num=1):
        self.url = url
        self.tag = tag
        self.class_ = class_
        self.selector = selector
        self.range_num = range_num
        print("true")

    def scraping(self):
        data = []
        for i in range(1, self.range_num + 1):
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

    def save(self, datas, init=False):
        """
        三つ組ごとに出現回数をDBに保存。カラムは(prefix1, prefix2, suffix, freq)
        :param triplet_freqs: 三つ組とその出現回数が集まった辞書 key: 三つ組(タプル) val:出現回数
        :param init: DBを初期化するかどうか。
        :return:
        """
        # DBオープン
        con = sqlite3.connect(Scraping.DB_PATH)

        # DBの初期化から始める場合
        if init:
            # schema.sqlを開き、sqlite3の中で実行
            with open(Scraping.DB_SCHEMA_PATH, "r") as f:
                schema = f.read()
                con.executescript(schema)

        # DBに保存。datasにはすべてのカラムがまとまったtuple一つ一つが繰り返し自動的に入る。
        p_statement = "insert into jiro_copype (title, body, url) values (?, ?, ?)"
        con.executemany(p_statement, datas)  # dataにはtupleを入れる
        con.commit()

    def show(self):
        # DBオープン
        con = sqlite3.connect(Scraping.DB_PATH)
        # con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select body from jiro_copype")
        copype_list = cur.fetchall()
        cur.close()
        con.close()
        return copype_list


if __name__ == "__main__":
    jiro_scraping_text = Scraping("https://matome.naver.jp/odai/2139244522734938601", "p", "mdMTMWidget01ItemTxt01View")
    jiro_scraping_title = Scraping("https://matome.naver.jp/odai/2139244522734938601", "p", "mdMTMWidget01ItemTtl01View")

    body = jiro_scraping_text.scraping(1)
    title = jiro_scraping_title.scraping(1)
    Scraping.save((title, body, "https://matome.naver.jp/odai/2139244522734938601"))