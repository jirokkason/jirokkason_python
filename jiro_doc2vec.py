import MeCab
import collections
from gensim import models
from gensim.models.doc2vec import LabeledSentence

def split_into_words(doc, name=""):
    # mecab = MeCab.Tagger("-Owakati")  # 分かち書きのみ取得
    mecab = MeCab.Tagger("-Ochasen")  # 分かち書きした単語の品詞も取得。\tで区切られている。
    lines = mecab.parse(doc).splitlines()  #splitlinesは改行で分割しlistにするメソッド
    # print(lines)

    # 精度を上げるために単語を品詞で絞る部分
    words = []
    for line in lines:
        chunks = line.split("\t")
        # 品詞のみ、そして動詞、形容詞、名詞（"名詞-数"以外）を抜き出す。startswithは文字列の先頭を調べるメソッド。
        if len(chunks) > 3 and (chunks[3].startwith("動詞") or chunks[3].startswith('形容詞') or chunks[3].startswith('名詞')) and not (chunks[3].startswith('名詞-数')):
            words.append(chunks[0])
    return LabeledSentence(words=words, tags=[name])

# 文章のセットをコーパスという