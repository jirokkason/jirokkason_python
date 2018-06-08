"""
与えられた文書からマルコフ連鎖のためのチェーン（連鎖）を作成して、DBに保存するファイル。
マルコフ連鎖が「ある状態が起こる確率が、その直前の状態から決まる」ことなので、「直前の言葉」に対応した「ある言葉」を定義して保存しておく。
ただし、直前の言葉:ある言葉が1:1だと、 一番短い繋がりが2単語となってしまい、意味の通る文になりにくいので、
直前の言葉1(prefix1)と直前の言葉2(prefix2):ある言葉(Suffix) というふうに2:1対応で考える。

要するに、このプログラムではマルコフ連鎖モンテカルロ法を起こすための前処理=>DB保存という処置を行う。

1.文章を三つ組にするメソッド、make_triplet_freqsを実行し、その最中に文章を改行ごとに切り分ける(_devide)。その時、句読点や記号は邪魔なので\nに置換する。
2.__init__時に定義したMeCabのタガーを使い_morphological_analysisで文を形態素解析。
3._make_tripletで形態素解析が行われた元々文だった単語を三つ区切りにし、その三つの単語が文中何回来るかをカウント。
make_tripletはforの中で実行されているので、形態素解析された一文が送られて来るので、それの始まりと終わりに一文の開始と終了をあわらす文字列を追加。
返り値は、一文ごとの単語と、その単語の出現回数。
4.あらかじめ定義して置いた辞書triplet_freqsに「三つ区切りの単語がはいったtuple」をkey、「その単語三つの出現回数」をvalueとして保存。
5.
"""

import re
import MeCab
import sqlite3
from collections import defaultdict


class PrepareChain:
    """
    チェーンを作成してDBに保存するクラス
    """

    BEGIN = "__BEGIN_SENTENCE__"
    END = "__END_SENTENCE__"

    DB_PATH = "chain.db"
    DB_SCHEMA_PATH = "schema.sql"

    def __init__(self, text):
        """
        初期化メソッド
        :param text: 文章。これを形態素解析=> (３組): カウント という風に分割していく。
        """
        # if isinstance(text, str):  # isinstanceメソッドは、第一引数に渡したオブジェクトが第二引数に渡した型かどうか判定するメソッド。
        #     text = text.decode("utf-8")
        self.text = text

        # 形態素解析用タガー
        self.tagger = MeCab.Tagger("-Ochasen")

    # 3個:countの辞書型を作るメソッド
    def make_triplet_freqs(self):
        """
        形態素解析 ~ 三つ組までの処理をまとめたメソッド。
        :return: ３つ組とその出現回数の辞書 key: 三つ組(タプル) val: 出現回数
        """

        sentences = self._divide(self.text)  # 長い文章をセンテンスごとに分割。

        # 3つ組の出現回数
        # defaultdict 辞書型に新しいkeyを追加するときの場合分けがいらなくなるモジュール
        triplet_freqs = defaultdict(int)

        # 文章の三つ区切りゾーン。一文毎に分かち書き、単語３つ区切り: count という処理を行っていることに注意
        for sentence in sentences:
            morphemes = self._morphological_analysis(sentence)  # 一文を分かち書きし、配列化
            triplets = self._make_triplet(morphemes)  # 分かち書き単語順3つ区切りで取得する
            # 辞書を繰り返し処理。一文毎だったのを全体でまとめるため、それぞれのcountの和を取る
            for triplet, count in triplets.items():
                triplet_freqs[triplet] += 1

    # 長い文章をセンテンスごとに分割
    def _divide(self, text):
        """
        「。」や改行などで区切られた長い文章を一文ずつに分ける
        :param text: 分割前の文章
        :return: 句読点などで区切られた、一文ずつの配列
        """
        # 改行文字以外の分割文字(正規表現)
        delimiter = "。 |．|\."

        # すべての分割文字を改行文字に置換(splitした時に「。」などの文字をなくさないため。)
        text = re.sub("({0})".format(delimiter), "\1\n", text)

        # splitlinesで先ほど置換した改行文字で分割
        sentences = text.splitlines()
        # stripで前後の空白文字を削除
        sentences = [s.strip() for s in sentences]

        return sentences

    # 分かち書きメソッド
    def _morphological_analysis(self, sentence):
        """
        文を形態素解析する。
        :param sentence: 一文
        :return: 形態素で分割された配列
        """
        morphemes = []  # 分かち書きした単語を入れる配列
        # sentence = sentence.encode("utf-8")
        node = self.tagger.parseToNode(sentence)  # MeCabで分かち書き。-Ochasenを指定しているのでparseToNodeメソッドを使用。
        while node:
            if node.posid != 0:
                morpheme = node.surface  # parseToNodeで取得した時はsurfaceで単語が取得できる。decode("utf-8)の必要有りかも。
                morphemes.append(morpheme)
            node = node.next  # イテレータなのでnextメソッドで次に行く。
        return morphemes

    # 単語三つ区切り、回数の辞書作成
    def _make_triplet(self, morphemes):
        """
        形態素解析で分割された配列を、言葉順三つ区切りの一個ずれずつで取得し、その出現回数を数える
        :param morphemes: 形態素配列
        :return: 3つ組とその出現回数の辞書 key: (sen1, sen2, sen3) val: 出現回数
        """
        # 三つ組を作れない場合は終わる。
        if len(morphemes) < 3:
            return {}

        # （一文の中での）単語の出現回数をカウントするためのdict
        triplet_freqs = defaultdict(int)

        # 一文内の単語ごとに繰り返し処理。三つ区切りなので、-2
        for i in range(len(morphemes) - 2):
            triplet = tuple(morphemes[i:i + 3])  # 辞書のkeyの作成。三つ区切りなので i:i+3
            triplet_freqs[triplet] += 1  # 単語の並びが一致していたらカウント。なければdefaultdictにより新規作成

        # ここまでで三つ区切り：countの処理は完了した。
        # だが、最終的には全文dbにまとめて保存してしまうため、「一文の開始、終了地点」という情報が失われてしまう。
        # なので、一文を表しているmorphemesの先頭に__BEGIN_SENTENCE__,
        # 終了地点に__END_SENTENCE__という記号を追加する。

        # beginを追加。スコープの外なので、classから呼び出す。
        triplet = (PrepareChain.BEGIN, morphemes[0], morphemes[1])
        triplet_freqs[triplet] = 1

        # endを追加
        triplet = (morphemes[-1], morphemes[-2], PrepareChain.END)
        triplet_freqs[triplet] = 1

        return triplet_freqs  # 一文毎の３つ区切り:countのdictを返す。


if __name__ == '__main__':
    text = "さてだいぶ食ってるハズですが・・・おいおい麺はいつ終わるんだ(汗)食っても食ってもエンドレスな。消耗してきた麺欲。めんどいから箸で掴むもん構わず口に運ぶとキャベツが結構邪魔だ・・・芯とな部分がボリューム増しな印象にしてくれるので・・・そう言えばコチラ本山の麺は噂通り柔め！と言うよりヌメリが凄い。だから重量感がある！麺の長さもえらく短い。ショートなんで箸を突っ込む回数が多い。いやぁマジで苦しくなってきた。早々に大満足の豚ちゃんは胃袋ダイブさせてるので問題ないが・・・だからヤサイが邪魔なんだよ今日に関しては。手こずると予想してたからコールをしないつもりだったのに・・・よりによってヤサイマシですから。ヘルプッ！！どこで潜ましてたか判らなかったニンニクを探すべく・・・エイッ！とかき混ぜる！フワッと鼻腔を突いてきたよ！OK！スープに新たな味が生まれてくる。心地良いニンニクの力！熱で焼けてる感のある油をより駆り立てて豚骨醤油と交わる。まるでニンニク強めの生姜焼き時の肉から脂から出る油がヤバい時と同じだ！右手に。箸を持つ手に元気が宿る！脳の麺欲が！このＪ欲がスパートをかけるぅ～！キャベツの芯とは無理せずフィニッシュ！！ラストはスープを飲みたいぜ！一回ゴクリ。。。二回目ゴクリ・・・ご馳走様でした～！！デンジャラスオイリー本山豚旨スープ！胸が焼け・・・焦げそうだ(笑)"
    chain = PrepareChain(text)
    triplet_freqs = chain.make_triplet_freqs()
    # chain.save(triplet_freqs, True)
    # chain.show(triplet_freqs)