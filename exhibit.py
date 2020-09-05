from abc import ABCMeta, abstractmethod
import re
import os
import unicodedata

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
# Selectタグが扱えるエレメントに変化させる為の関数を呼び出す
from selenium.webdriver.support.ui import Select

import pandas as pd
from datetime import date, datetime, timedelta
import time
import requests
from bs4 import BeautifulSoup

import sys
sys.path.append(os.path.abspath("machine_learnings"))
print(sys.path)
from custom_dict import CUSTOM_DICT
from main import predict


STATUS = "PREPARE"
dict_ = {}


class Exhibiter():
    URLS = {
        "LOGIN_URL": "https://www.buyma.com/login/",
        "SELL_URL": "https://www.buyma.com/my/sell/new/?tab=b"
    }

    elements = {
        # "ID": "",
        # "PASS": "",
        "商品画像": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[1]/div/div/div[2]/div/div/div[1]/div/div/div/input",
        "商品名": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[2]/div[1]/div/div[2]/div/div/div[1]/input",
        "商品コメント": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[2]/div[2]/div/div[2]/div/div/div[1]/textarea",
        "ブランド": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[3]/div[2]/div/div[2]/div/div/div/div[1]/div/div/div/div/div/div/div/input",
        "商品価格": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[7]/div[1]/div/div[2]/div/div/div[1]/div/div[1]/div/div/input",
        "参考価格": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[7]/div[2]/div/div[2]/div/div/div[2]/div/div/div/div/input",
        "買付先名": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[8]/div[2]/div/div[2]/div/div/div[1]/table/tbody/tr[1]/td[1]/div/input",
        "買付先URL": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[8]/div[2]/div/div[2]/div/div/div[1]/table/tbody/tr[1]/td[2]/div/div/input",
        "説明": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[8]/div[2]/div/div[2]/div/div/div[1]/table/tbody/tr[2]/td/div/input",
        "出品メモ": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[8]/div[1]/div/div[2]/div/div[1]/textarea",
        "下書き保存": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[9]/div/button[1]",
        "閉じる": "/html/body/div[3]/div[2]/div[1]/div/div[2]/div[8]/div/div/div[3]/button[1]",
        "型番": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[4]/div[2]/div/div[2]/div/div/div[2]/table/tbody/tr/td[1]/input",
        "配送方法": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[5]/div/div/div[2]/div/div/div[2]/div[1]/table/tbody/tr[1]/td[1]",
        "購入期限": "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[6]/div[1]/div/div[2]/div/div/div/div/div/div/div/div[1]/div/input",
    }

    validates = {
        "商品名": 60,  # 全角30文字, 半角60文字まで
        "商品コメント": 3000,  # 全角1500文字, 半角3000文字まで
        "出品メモ": 1000  # 半角1000文字まで
    }

    # TODO:: ブランドイントロダクション挿入
    template = {
        "商品コメント":"""
※ご注文前に必ず在庫確認をお願いいたします。
        
■ブランド名：{0}

■商品名：{1}

■カラー：

■仕様：

■サイズ：


【トラブル回避のため、ご購入前に必ずお読みください。】

■ご注文前に必ず在庫確認をお願いいたします。

■全商品、新品・未使用・本物保証
取り扱い商品は全て正規品です。各国のブランド正規・直営店で《直接》仕入れをしています。

■「あんしんプラス」へのご加入をお勧めいたします。
商品は追跡が可能な方法で発送をしますが、配送の遅延及び紛失が発生した場合バイヤー側では免責事項となります。ご加入いただくことで[無料鑑定][初期不良補償][紛失補償]などの補償が利用できます。
「あんしんプラス」
https://www.buyma.com/contents/safety/anshin.html

■各ブランド、直営アウトレット買い付けの場合、ギャランティーカード（保証書）に日付・サインがないことが多いです。また、ギャランティカード（保証書）の付属が元から存在しないブランドもあります。有無に関わらず、全て正規品になりますので、ご安心ください。

■天然皮革の商品に関して、キズ・シワ・シミ等見える箇所は不良ではなく天然素材によるもので初期不良ではございません。また、海外の商品は日本と品質基準が異なり、まれに縫製が雑であったり小さい傷や汚れ等があることがあります。 十分に検品した上でのお送りになります。また、ブランドの保存袋や商品ボックスはブランドの方で、もともと保管用のため多少傷汚れがある場合がありますが、不良ではございませんのでご容赦くださいませ。

■仕入れ時他商品とまとめて仕入れをしている関係でレシートはもしくはインボイス（購入証明）はお送りしておりません。予めご了承下さい。

■モニターにより、写真と実物の色が若干異なって見える場合がございます。「イメージと違う」等、お客様都合による返品・交換は原則受け付けておりません。
その他で何かあった場合はまずお問い合わせください。

■全て追跡付きの郵便にて発送
海外からの発送：DHL 国際郵便 など
日本からの発送：レターパック・ゆうパック・宅急便コンパクトなど

■発送時期
購入が確定次第、２〜7営業日以内に在庫確保・発送をいたします。
※土日は郵便局が休みのため発送業務は行なっておりませんので予めご了承下さい。

■到着時期
【発送後】海外から：通常時は、７−１４日でのお届けが目安となりますが、現在コロナウィルスの影響でお届けに遅延が発生しているケースがございます。
国内から：通常時は、翌日〜３日程度でのお届けが目安となりますが、天候やその他の状況により目安よりも日数がかかる場合がございます。
お荷物の場所は発送後にお送りさせていただく追跡番号にてご確認下さい。
""" ,
        "GUCCI":"""
_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
GUCCI
GG柄でも有名、シンプルで洗練されたデザインが人気のイタリアブランド
GUCCI(グッチ)は1923年にグッチオ・グッチが高級皮革製品の店をイタリアに創業したのが始まり。品質保証の為に、世界で初めてデザイナーの名前を入れて商品を販売したブランドとしても有名。
グッチオ・グッチ自らが考案した、ダブルＧのモノグラムは今も世界中の人々に愛され続けている。ミニマムで洗練されたアイテムの数々は常にファッション界の注目の的！
_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
""" ,
        "SMAXMARA":"""
_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
世界的な老舗ブランドMax Mara(マックスマーラ)の中の、シンプルでありながらディテールにこだわったライン、'S Max Mara(エス マックスマーラ)。
代表的なモデルはソフトダウンの"The cube (キューブ)"です。
老舗ブランドならではのハイクオリティーな素材で使用した、エレガントにもカジュアルにも着まわせるダウンは毎シーズンさまざまなバリエーションで展開しています。
リバーシブル・袖やフードの着脱など、機能面にもこだわったデザインが魅力です。
_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
"""
    }

    def __init__(self, data: dict):
        self.data = data

    @classmethod
    def active(cls, xpath=""):
        cls.find_element_by_css_selector(xpath)

    @classmethod
    def english_to_katakana(cls, word: str) -> str:
        # url = 'https://www.sljfaq.org/cgi/e2k_ja.cgi'
        # url_q = url + '?word=' + word
        # headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0'}

        # response = requests.get(url_q)
        # if response.status_code == 200:
        #     soup = BeautifulSoup(response.text, 'html.parser')
        #     katakana_string = soup.find_all(class_='katakana-string')[0].string.replace('\n', '')
        #     return katakana_string
        # else:
        #     print("EnglishToKatakana Response is ", response.status_code)
        #     return None

        # bep-eng.dicから辞書作成
        global STATUS
        global dict_
        if STATUS == "PREPARE":
            # dic_file = os.path.dirname(os.path.abspath(__file__)) + '/bep-eng.dic'
            # with open(dic_file, mode='r', encoding='utf-8') as f:
            #     lines = f.readlines()
            #     for i, line in enumerate(lines):
            #         if i >= 6:
            #             line_list = line.replace('\n', '').split(' ')
            #             dict_[line_list[0]] = line_list[1]
            dict_.update(CUSTOM_DICT)
            STATUS = "LOADED"
        
        return dict_.get(word.upper(), word)

    @classmethod
    def get_east_asian_width_count(cls, text: str) -> int:
        count = 0
        for c in text:
            if unicodedata.east_asian_width(c) in 'FWA':
                count += 2
            else:
                count += 1
        return count

    @classmethod
    def generate_images(cls, data: dict) -> list:
        # 画像DL
        images = []
        ptn = r"^(.+)_80(\.jpg|\.png|\.gif)$"
        ptn_ = r"^(//.+)$"
        for i, url in enumerate(data["retailer_images"].split("@@@")):
            try:
                url = re.sub(ptn, r"\1_1000\2", url)
                url = re.sub(ptn_, r"https:\1", url)

                print(url)

                response = requests.get(url)
                if response.status_code == 200:
                    image = response.content
                    if is_jpg(image):
                        ext = ".jpg"
                    elif is_png(image):
                        ext = ".png"
                    elif is_gif(image):
                        ext = ".gif"
                    else:
                        ext = ".jpg"
                    with open("/tmp/image_%s%s" % (str(i),ext,), "wb") as f:
                        f.write(image)
                        images.append("/tmp/image_%s%s" % (str(i), ext,))
                        i += 1
            except:
                break
        
        return images

    @classmethod
    def generate_titles(cls, data: dict) -> (str, str,):  # -> str:カナTitle
        title = data["brand"] + " " + data["retailer_title"]
        kana_title = " ".join([cls.english_to_katakana(word) for word in title.split()])

        # 文字数バリデーション
        if cls.get_east_asian_width_count(kana_title) > cls.validates["商品名"]:
            diff = cls.validates["商品名"] - cls.get_east_asian_width_count(kana_title)
            kana_title = kana_title[:diff]

        return (title, kana_title,)

    @classmethod
    def generate_comment(cls, data: dict) -> str:

        comment_ptn1 = comment_ptn2 = ""
        # 空白が入っているかどうかで sku 判定を行う
        if " " in data["retailer_sku"]:
            comment_ptn1 += "[ 型番が取得出来なかった可能性があります。アイテムを確認下さい。]\n"
            comment_ptn2 += "[ 型番が取得出来なかった可能性があります。アイテムを確認下さい。]\n"

        # description 追加
        comment_ptn1 += data["retailer_description"] + "\n"
        comment_ptn2 += data["retailer_description"] + "\n"

        # brand 紹介文
        if data["brand"].upper() in cls.template.keys():
            comment_ptn2 += cls.template[data["brand"].upper()]
        
        # コメントフォーマットに変数を挿入
        comment_ptn1 += cls.template["商品コメント"].format(data["brand"], data["retailer_title"])
        comment_ptn2 += cls.template["商品コメント"].format(data["brand"], data["retailer_title"])

        # 禁則文字処理 TODO::関数化
        comment_ptn1 = comment_ptn1.replace("é", "").replace("•", "")
        comment_ptn2 = comment_ptn2.replace("é", "").replace("•", "")

        # 文字数バリデーション
        comment = comment_ptn2
        comment = "※作成中\n" + comment
        if cls.get_east_asian_width_count(comment) > cls.validates["商品コメント"]:
            comment = comment_ptn1
        if cls.get_east_asian_width_count(comment) > cls.validates["商品コメント"]:
            diff = cls.validates["商品コメント"] - cls.get_east_asian_width_count(comment)
            comment = comment[:diff]

        return comment

    @classmethod
    def generate_categories(cls, kana_title: str) -> list:
        categories = [predict(kana_title, "category_1"), predict(kana_title, "category_2"), predict(kana_title, "category_3")]
        return categories

    @classmethod
    def generate_brand(cls, data: dict) -> str:
        brand = data["brand"]
        return brand

    @classmethod
    def generate_price(cls, data: dict) -> int:
        price = int(data["active_price"])
        return price

    @classmethod
    def generate_retailer(cls, data: dict) -> str:
        retailer = data["retailer"]
        return retailer

    @classmethod
    def generate_href(cls, data: dict) -> str:
        href = data["href"]
        return href

    @classmethod
    def generate_memo(cls, data: dict) -> str:
        memo = [data["retailer_brand"], data["retailer_title"], data["retailer_price"], data["retailer_origin_price"], data["retailer_sku"]]
        memo = ",".join(memo)
        memo = "AutoCreated: True\n" + memo
        if cls.get_east_asian_width_count(memo) > cls.validates["出品メモ"]:
            diff = cls.validates["出品メモ"] - cls.get_east_asian_width_count(memo)
            memo = memo[:diff]

        return memo


class Driver(metaclass=ABCMeta):
    @abstractmethod
    def access(self):
        """ Access The WebSite """
        pass

    @abstractmethod
    def get_html(self):
        """ Return HTML Source """
        pass

    @abstractmethod
    def exit(self):
        """ Stop Process """
        pass

class Chrome(Driver):
    _driver = None
    _user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.binary_location = "/opt/python/bin/headless-chromium"
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--single-process")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-infobars")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--enable-logging")
        options.add_argument("--log-level=0")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--homedir=/tmp")
        options.add_argument("--user-agent=%s" % (self._user_agent,))
    
        self._driver = webdriver.Chrome(
            # executable_path="/opt/python/bin/chromedriver",
            executable_path="/Users/sugiharanaoki/Repos/buyma/buyma-app/chromedriver",
            chrome_options=options
        )
        # デフォルト待機時間の設定
        self._driver.implicitly_wait(10)        

    def __del__(self):
        self.exit()

    def access(self, url: str = ""):
        self._driver.get(url)

    def get_html(self, url=None):
        # self._driver.get(url)
        # TODO:: ErrorHandling
        return self._driver.page_source

    def exit(self):
        self._driver.quit()

    def screenshot(self, filename:str="/tmp/shot1.png"):
        # get width and height of the page
        w = self._driver.execute_script("return document.body.scrollWidth;")
        h = self._driver.execute_script("return document.body.scrollHeight;")

        # set window size
        self._driver.set_window_size(w,h)

        # Get Screen Shot
        self._driver.save_screenshot(filename)

    def wait(self):
        WebDriverWait(self._driver, 15).until(EC.presence_of_all_elements_located)


def is_jpg(b: bytes) -> bool:
    """バイナリの先頭部分からJPEGファイルかどうかを判定する。"""
    return bool(re.match(b"^\xff\xd8", b[:2]))
def is_png(b: bytes) -> bool:
    """バイナリの先頭部分からPNGファイルかどうかを判定する。"""
    return bool(re.match(b"^\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", b[:8]))
def is_gif(b: bytes) -> bool:
    """バイナリの先頭部分からGIFファイルかどうかを判定する。"""
    return bool(re.match(b"^\x47\x49\x46\x38", b[:4]))


def main(event, context):

    chrome = Chrome()
    driver = chrome._driver

    path = "~/Desktop/buyma.com&bag.researched.csv"

    driver.get(Exhibiter.URLS["LOGIN_URL"])

    """ LOGIN """
    driver.find_element_by_id('txtLoginId').send_keys("ec-customer-support@valis.jp")
    chrome.screenshot(filename="/tmp/buyma1.png")
    driver.find_element_by_id('txtLoginPass').send_keys("VALISsugihara1")
    chrome.screenshot(filename="/tmp/buyma2.png")
    driver.find_element_by_id('login_do').click()
    chrome.screenshot(filename="/tmp/buyma3.png")

    """ フォーム入力 """
    try:
        driver.get(Exhibiter.URLS["SELL_URL"])
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "bmm-c-heading__ttl"))
        )
        # WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located)
        # h1_text = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[1]/h1").text
        h1_text = driver.find_element_by_css_selector("h1.bmm-c-heading__ttl").text
        if h1_text != "新規出品":
            chrome.screenshot(filename="/tmp/error_1.png")
            raise Exception("出品ページへ遷移出来ませんでした")
    except Exception as e:
        print(e.args[0])
        chrome.screenshot(filename="/tmp/error.png")

    # 商品名
    df = pd.read_csv(path)
    df = df.dropna()
    for index, data in df.iterrows():

        ex = Exhibiter(data=data)

        # 商品画像
        images = ex.generate_images(data=data)
        print(images)
        driver.find_element_by_xpath(ex.elements["商品画像"]).send_keys("\n".join(images))
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "商品画像"))

        # 商品タイトル
        title, kana_title = ex.generate_titles(data=data)
        print(kana_title, title)
        driver.find_element_by_xpath(ex.elements["商品名"]).send_keys(kana_title)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "商品名"))

        # 商品コメント
        comment = ex.generate_comment(data=data)
        driver.find_element_by_xpath(ex.elements["商品コメント"]).send_keys(comment)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "商品コメント"))

        # カテゴリ
        try:
            wait = WebDriverWait(driver, 30)
            categories = ex.generate_categories(kana_title=kana_title)
            # 普通にエレメントを取得する
            select_paths = ["react-select-2--value", "react-select-10--value", "react-select-11--value"]
            option_paths = ["bmm-c-select-option__main", "Select-option", "Select-option"]
            for i, select_path in enumerate(select_paths):
                select = driver.find_element_by_id(select_path)
                select.click()
                wait.until(
                    EC.visibility_of_element_located((By.CLASS_NAME, option_paths[i]))
                )
                chrome.screenshot(filename="/tmp/{0}{1}_{2}_sel{3}.png".format(data["brand"], str(index), "カテゴリ", i))

                options = driver.find_elements_by_class_name(option_paths[i])
                for op in options:
                    print(op.text)
                    if op.text == categories[i]:
                        op.click()
                        break
                chrome.screenshot(filename="/tmp/{0}{1}_{2}_op{3}.png".format(data["brand"], str(index), "ブランド", i))
        except Exception as e:
            print("Exception Occured ...", e.args[0])
            pass

        # ブランド
        brand = ex.generate_brand(data=data)
        driver.find_element_by_xpath(ex.elements["ブランド"]).send_keys(brand)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "ブランド"))

        # 型番（編集時のみ？）
        # sku = data["retailer_sku"]
        # driver.find_element_by_xpath(ex.elements["型番"]).send_keys(sku)
        # chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "型番"))

        # 配送方法
        script = 'document.getElementsByClassName("bmm-c-form-table__icon-cell")[1].click()'
        driver.execute_script(script)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "配送方法"))

        # 購入期限（14日後）
        ninety_days_since = date.today() + timedelta(14)
        ninety_days_since = ninety_days_since.strftime('%Y/%m/%d')
        # driver.find_element_by_xpath(ex.elements["購入期限"]).clear()
        # chrome.screenshot(filename="/tmp/{0}{1}_{2}_A.png".format(data["brand"], str(index), "配送方法"))
        # driver.find_element_by_xpath(ex.elements['購入期限']).send_keys(Keys.CONTROL + "a")
        # chrome.screenshot(filename="/tmp/{0}{1}_{2}_B.png".format(data["brand"], str(index), "配送方法"))
        # driver.find_element_by_xpath(ex.elements['購入期限']).send_keys(Keys.DELETE)
        # chrome.screenshot(filename="/tmp/{0}{1}_{2}_C.png".format(data["brand"], str(index), "配送方法"))
        for i in range(0, 10):
            driver.find_element_by_xpath(ex.elements['購入期限']).send_keys(Keys.BACK_SPACE)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}_C.png".format(data["brand"], str(index), "配送方法"))
        driver.find_element_by_xpath(ex.elements["購入期限"]).send_keys(ninety_days_since)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}_D.png".format(data["brand"], str(index), "配送方法"))
        # 別の箇所をクリック
        driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[6]/div[1]/div/div[1]/div/p").click()
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "購入期限"))

        # TODO::: 買付地

        # TODO:: 発送地

        # TODO:: 色・サイズ補足情報 に ブランドテンプレートと店内リンク
        """他のGucciのアイテムはこちらからもご確認頂けます☆
https://www.buyma.com/r/_GUCCI-%E3%82%B0%E3%83%83%E3%83%81/Arrivals/"""

        # 商品価格
        price = ex.generate_price(data=data)
        print(price)
        driver.find_element_by_xpath(ex.elements["商品価格"]).send_keys(price)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "商品価格"))

        # 参考価格
        # label_ = "/html/body/div[3]/div[2]/div[1]/div/div[1]/div/div/div/div[2]/form/div[7]/div[2]/div/div[2]/div/div/div[1]/div/label[2]"
        # driver.find_element_by_xpath(label_).click()
        # origin_price = data["retailer_origin_price"]
        # prc_ptn = r"[^0-9\.]"
        # if "€" in origin_price:
        #     # origin_price = float(origin_price.replace("€", "").replace(",", "").strip()) * 120
        #     origin_price = float(re.sub(prc_ptn, "", origin_price)) * 120
        # elif "£" in origin_price:
        #     # origin_price = float(origin_price.replace("£", "").replace(",", "").strip()) * 135
        #     origin_price = float(re.sub(prc_ptn, "", origin_price)) * 135
        # elif "$" in origin_price:
        #     # origin_price = float(origin_price.replace("$", "").replace(",", "").strip()) * 108
        #     origin_price = float(re.sub(prc_ptn, "", origin_price)) * 108
        # elif "¥" in origin_price or "JPY" in origin_price:
        #     # origin_price = float(origin_price.replace("¥", "").replace("JPY", "").replace(",", "").strip())
        #     origin_price = float(re.sub(prc_ptn, "", origin_price))

        # origin_price = int(origin_price)
        # driver.find_element_by_xpath(ex.elements["参考価格"]).send_keys(origin_price)
        # chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "参考価格"))
        # 設定しない
        pass

        # 買付先名
        retailer = ex.generate_retailer(data=data)
        driver.find_element_by_xpath(ex.elements["買付先名"]).send_keys(retailer)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "買付先名"))

        # 買付先URL
        href = ex.generate_href(data=data)
        driver.find_element_by_xpath(ex.elements["買付先URL"]).send_keys(href)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "買付先URL"))

        # 説明
        today_ = datetime.today().strftime('%Y/%m/%d') + "時点"
        driver.find_element_by_xpath(ex.elements["説明"]).send_keys(today_)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "説明"))

        # 出品メモ
        memo = ex.generate_memo(data=data)
        driver.find_element_by_xpath(ex.elements["出品メモ"]).send_keys(memo)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "出品メモ"))

        # 下書き保存
        driver.find_element_by_xpath(ex.elements["下書き保存"]).click()
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "下書き保存"))

        # wait until someid is clickable
        wait = WebDriverWait(driver, 30)
        # element = wait.until(EC.element_to_be_clickable((By.XPATH, ex.elements["閉じる"])))
        # driver.find_element_by_xpath(ex.elements["閉じる"]).click()
        # chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "閉じる"))

        success_text = "下書きの保存が完了しました"
        # done_xpath = "/html/body/div[3]/div[2]/div[1]/div/div[2]/div[3]/div/div/div[1]/p"
        done_selector = ".bmm-c-modal__head > p"
        try:
            element = wait.until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, done_selector), success_text)
            )
            chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "完了"))
        except Exception:
            chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "完了_E"))

        driver.get(ex.URLS["SELL_URL"])
        # 遷移確認のアラートが出るので OK を押す
        Alert(driver).accept()
        chrome.wait()
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png".format(data["brand"], str(index), "ReSTART"))

    driver.close()
    driver.quit()


    return True


main(1,1)