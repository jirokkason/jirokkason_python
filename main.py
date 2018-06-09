from __future__ import absolute_import
from __future__ import unicode_literals
import re
from jiro_scraping import Scraping
from PrepareChain import PrepareChain
from GenerateText import GenerateText


def scraping_and_save():
    copype_url = "https://matome.naver.jp/odai/2139244522734938601" # 8
    # copype_url = "https://matome.naver.jp/odai/2138389040041091701" # 2
    # copype_url = "https://matome.naver.jp/odai/2135502414433224101" # 2
    jiro_scraping_text = Scraping(copype_url, "p", "mdMTMWidget01ItemTxt01View", None, 8)
    jiro_scraping_title = Scraping(copype_url, "p", "mdMTMWidget01ItemTtl01View", None, 8)
    # jiro_scraping_text = Scraping(copype_url, "p", "mdMTMWidget01ItemTxt01View", None, 2)
    # jiro_scraping_title = Scraping(copype_url, "p", "mdMTMWidget01ItemTtl01View", None, 2)
    # jiro_scraping_text = Scraping(copype_url, "q", "mdMTMWidget01ItemQuote01Txt", None, 2)
    # jiro_scraping_title = Scraping(copype_url, "p", "mdMTMWidget01ItemTtl01View", None, 2)
    print("scrape body")
    body_list = jiro_scraping_text.scraping()
    print("scrape title")
    title_list = jiro_scraping_title.scraping()
    data = [(title, body, copype_url) for title, body in zip(title_list, body_list)]
    jiro_scraping_text.save(data)


def text_to_prepare_chain():
    # マルコフ連鎖のためにデータ整形 => chain_freqsテーブルに保存
    select_data = Scraping()
    text_list = select_data.show()
    # すべての文字列を結合。改行で一文とみなす
    texts = []
    [texts.append(text) for text_tuple in text_list for text in text_tuple]
    chain = PrepareChain("\n".join(texts))
    triplet_freqs = chain.make_triplet_freqs()
    chain.save(triplet_freqs)
#
# @route("/", methods=['POST'])
def main(sentence_length):
    generator = GenerateText(sentence_length)

    jiro_sentence = re.sub("^\d{4}/\d{1,2}/\d{1,2}/\d{1,2}$", "", generator.generate()
          .replace("。", "。\n")
          .replace("「", " ")
          .replace("」", " ")
          .replace("(", " ")
          .replace("）", " ")
          .replace("(", " ")
          .replace(")", " ")
          .replace("『", " ")
          .replace("』", " ")
                 )
    print(jiro_sentence)

    # response = {'status': 200,
    #             'result': jiro_sentence
    #                     }
    # responseBody = json.dumps(response)

    # return responseBody.encode('utf-8')

# run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    # scraping_and_save()
    # text_to_prepare_chain()
    main(1)

# .headers on
# .mode csv
# .output chain.csv
# select * ffrom chain_freqs;
