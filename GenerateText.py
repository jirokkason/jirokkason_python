"""
マルコフ連鎖を用いて入力から適当な文章を自動生成するファイル
"""

import os.path
import sqlite3
import random

from PrepareChain import PrepareChain
DB_PATH = "/Users/matsumotokazuki/Desktop/jirokkason/jirokkason_python/jirokkason.db"
DB_SCHEMA_PATH = "/Users/matsumotokazuki/Desktop/jirokkason/jirokkason_python/markov_schema.sql"

class GenerateText:
    """
    文章生成クラス
    """

    def __init__(self, n=10):
        """
        初期化メソッド
        :param n: 文章をいくつ生成するか
        """
        self.n = n

    def generate(self):
        """
        文章を生成する処理をまとめたメソッド。
        :return: 生成された文章
        """

        # 最終的に出来上がる文章
        generated_text = ""

        # 単語毎の状態変異が保存されたDBと接続
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row # 通常、sqliteのデータはlist（数値）で帰ってくるが、このメソッドによりカラム名で取得可能

        # 指定の数だけ文章を繋げる。n回分BEGIN~ENDを繰り返した文章を取得。
        for i in range(self.n):
            text = self._generate_sentence(con)
            generated_text += text

        # DBクローズ
        con.close()

        return generated_text


    def _generate_sentence(self, con):
        """
        ランダムに一文を生成する処理をまとめたもの
        :param con: DB接続のためのコネクション
        :return: 生成された一つの文章
        """

        # 生成文章のリスト
        morphemes = []

        # 文章の始まりを取得。BEGIN_SENTENSEとなっているところからランダムに取得。返り値はtuple
        first_triplet = self._get_first_triplet(con)
        morphemes.append(first_triplet[1])
        morphemes.append(first_triplet[2])

        # 続きの文章を取得。__END_SENTENCE__がくるまで繰り返し。
        while morphemes[-1] != PrepareChain.END:
            # ここで、マルコフ連鎖の理論が適用されて、一個ずれの三つ組の単語で考えているので、前の三つ組のprefix2,suffixが次のprefix1,2となる。
            # 要するにmorphemesの後ろから二番目、後ろから一番目をprefixとする
            prefix1 = morphemes[-2]
            prefix2 = morphemes[-1]
            triplet = self._get_triplet(con, prefix1, prefix2)  # prefix1,2から次の単語を取得するメソッド
            # tupleで次の三つ組が帰ってくるので、そのsuffixのみを取得
            morphemes.append(triplet[2])

        # morphemesにBEGIN~ENDまでランダムに取得した文字列が格納されているので、連結
        result = "".join(morphemes[:-1])

        return result

    def _get_first_triplet(self, con):
        """
        文章の始まりの三つ組をランダムに取得
        :param con: DB接続のためのコネクション
        :return: 文章の始まりの三つ組のタプル
        """
        # dbのカラムが(prefix1, prefix2, suffix...)となっているので、始まりの文章はprefix1が__BEGIN_SENTENCE__となっていること
        # なので、BEGINをprefix1としてチェーンを取得するためのtupleを定義
        prefixes = (PrepareChain.BEGIN, )

        # prefix1がBEGINとなっているチェーンを配列で取得。この要素からランダムに選んでいく。
        chains = self._get_chain_from_DB(con, prefixes)
        # 始まりの三つ組が格納されているchainsから、ランダムに一つ取得
        triplet = self._get_probable_triplet(chains)

        # idとfreqsはいらないので、文字列だけ返させる。
        return (triplet["prefix1"], triplet["prefix2"], triplet["suffix"])

    def _get_triplet(self, con, prefix1, prefix2):
        """
        prefix1,prefix2からsuffixをランダムに取得
        :param con: DBと接続するためのコネクション
        :param prefix1:
        :param prefix2:
        :return: 3つ組のtuple
        """
        # suffixを取得するためprefix1,2を代入したtupleを作成
        prefixes = (prefix1, prefix2, )

        # prefix1,prefix2が引数の値と等しいチェーンを配列で取得。この要素からランダムに選んでいく。
        chains = self._get_chain_from_DB(con, prefixes)
        # print(chains)

        # 取得したチェーンから、確率的に一つ選ぶ
        triplet =self._get_probable_triplet(chains)

        # idとfreqsはいらないので、文字列だけ返させる。
        return (triplet["prefix1"], triplet["prefix2"], triplet["suffix"])

    def _get_probable_triplet(self, chains):
        """
        チェーンの配列の中から確率的に一つを返す。
        :param chains: チェーンの配列
        :return: ランダムに選んだ三つ組
        """
        # 確率配列。（単語の頻度によって確率が変わるので）ここに三つ組が入っているchainsから取得するためのindexを入れ直す。
        # probability = []

        # freqが高い、つまり複数回文章に出てきている単語はその分高確率でなくてはならない
        # 各三つ組のindexを、「freqの値分」probabilityに代入。
        # for index, chain in enumerate(chains):
        #     for _ in range(chain["freq"]):
        #         probability.append(index)


        probability = [index for index, chain in enumerate(chains) for _ in range(chain["freq"])]
        # print(probability)
        # chainを選ぶためのindexをランダムに取得

        chain_index = random.choice(probability)

        return chains[chain_index]

    def _get_chain_from_DB(self, con, prefixes):
        """
        チェーンの情報をDBから取得。
        始まりの位置だけ取得する時はprefix1のみがくるが、それ以外はprefix1,prefix2二つのvalueを用いて検索することに注意。
        :param con: DBと接続するためのコネクション
        :param prefixes: チェーンを取得するためのprefixの条件。tupleかlist
        :return: チェーンの情報の配列。
        """
        # ベーシックの検索sql。BEGINを検索する時はこれ
        sql = "select prefix1, prefix2, suffix, freq from chain_freqs where prefix1 = ?"
        # 途中の三つ組を検索する時がprefixが二つなので、条件に加える
        if len(prefixes) == 2:
            sql += "and prefix2 = ?"

        # 結果を格納するlist
        result = []

        # DBから取得。第一引数に入れたsql文の?の部分にprefixesの値が入る。
        cursor = con.execute(sql, prefixes)
        for row in cursor:
            # if len(prefixes) == 1:
            #     print(dict(row))
            result.append(dict(row))

        return result


if __name__ == '__main__':
    generator = GenerateText()
    print(generator.generate())