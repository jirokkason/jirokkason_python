from __future__ import absolute_import
from __future__ import unicode_literals
import jiro_db
import jiro_scraping
import jiro_doc2vec


def scraping_and_save():
    copype_url1 = "https://matome.naver.jp/odai/2139244522734938601"
    copype_url2 = "https://matome.naver.jp/odai/2138389040041091701"
    copype_url3 = "https://matome.naver.jp/odai/2135502414433224101"
    # jiro_scraping_text = jiro_scraping.Scraping(copype_url1, "p", "mdMTMWidget01ItemTxt01View")
    # jiro_scraping_title = jiro_scraping.Scraping(copype_url1, "p", "mdMTMWidget01ItemTtl01View")
    # jiro_scraping_text = jiro_scraping.Scraping(copype_url2, "p", "mdMTMWidget01ItemTxt01View")
    # jiro_scraping_title = jiro_scraping.Scraping(copype_url2, "p", "mdMTMWidget01ItemTtl01View")
    jiro_scraping_text = jiro_scraping.Scraping(copype_url3, "q", "mdMTMWidget01ItemQuote01Txt")
    jiro_scraping_title = jiro_scraping.Scraping(copype_url3, "p", "mdMTMWidget01ItemTtl01View")
    print("scrape body")
    body_list = jiro_scraping_text.scraping(3)
    print("scrape title")
    title_list = jiro_scraping_title.scraping(3)

    print("insert db")
    for i, (title, body) in enumerate(zip(title_list, body_list)):
        jiro_data = jiro_db.DB("root", "", "jirokkason")


        jiro_data.insert("insert into jiro_copype (title, body) values (%s, %s);", (title, body))


def main():
    print("select db")
    jiro_data = jiro_db.DB("root", "", "jirokkason")
    data = jiro_data.select("select body from jiro_copype")
    print(len(data))
    for d in data:
        doc = d[0]
        jiro_doc2vec.split_into_words(doc)


if __name__ == "__main__":
    main()
    # scraping_and_save()