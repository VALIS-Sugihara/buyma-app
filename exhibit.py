from abc import ABCMeta, abstractmethod

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup


STATUS = "PREPARE"
def english_to_katakana(word):
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
    if STATUS == "PREPARE":
        dic_file = './bep-eng.dic'
        dict_ = {}
        with open(dic_file, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if i >= 6:
                    line_list = line.replace('\n', '').split(' ')
                    dict_[line_list[0]] = line_list[1]
        STATUS = "LOADED"
    
    return dict_.get(word, word)


class Exhibiter():
    URLS = {
        "LOGIN_URL": "https://www.buyma.com/login/",
        "SELL_URL": "https://www.buyma.com/my/sell/new/?tab=b"
    }

    elements = {
        # "ID": "",
        # "PASS": "",
        "商品画像": "#SellUI-react-component-457a7cb2-4c70-44f2-9598-a49559a9e794 > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(1) > div > div > div.bmm-l-col.bmm-l-col-9 > div > div > div.bmm-c-field__input > div > div > div.bmm-c-img-upload__dropzone.bmm-c-img-upload__dropzone--panel > input[type=file]",
        "商品名": "#SellUI-react-component-457a7cb2-4c70-44f2-9598-a49559a9e794 > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(2) > div:nth-child(1) > div > div.bmm-l-col.bmm-l-col-9 > div > div > div.bmm-c-field__input > input",
        "商品コメント": "#comment > div > div.bmm-l-col.bmm-l-col-9 > div > div > div.bmm-c-field__input > textarea",
        "ブランド": "#SellUI-react-component-457a7cb2-4c70-44f2-9598-a49559a9e794 > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(3) > div:nth-child(2) > div > div.bmm-l-col.bmm-l-col-9 > div > div > div > div:nth-child(1) > div > div > div > div > div > div > div > input",
        "商品価格": "#SellUI-react-component-457a7cb2-4c70-44f2-9598-a49559a9e794 > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(7) > div:nth-child(1) > div > div.bmm-l-col.bmm-l-col-9 > div > div > div.bmm-c-field__input > div > div.bmm-l-col.bmm-l-col-4 > div > div > input",
        "参考価格": "#SellUI-react-component-b3b598cf-6a8e-476b-9083-bb479ab7eb8b > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(7) > div:nth-child(2) > div > div.bmm-l-col.bmm-l-col-9 > div > div > div:nth-child(2) > div > div > div > div > input",
        "買付先名": "#SellUI-react-component-457a7cb2-4c70-44f2-9598-a49559a9e794 > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(8) > div:nth-child(2) > div > div.bmm-l-col.bmm-l-col-9 > div > div > div.bmm-c-form-table__body > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > input",
        "買付先URL": "#SellUI-react-component-457a7cb2-4c70-44f2-9598-a49559a9e794 > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(8) > div:nth-child(2) > div > div.bmm-l-col.bmm-l-col-9 > div > div > div.bmm-c-form-table__body > table > tbody > tr:nth-child(1) > td:nth-child(2) > div > div > input",
        "説明": "#SellUI-react-component-457a7cb2-4c70-44f2-9598-a49559a9e794 > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(8) > div:nth-child(2) > div > div.bmm-l-col.bmm-l-col-9 > div > div > div.bmm-c-form-table__body > table > tbody > tr:nth-child(2) > td > div > input",
        "出品メモ": "#SellUI-react-component-b3b598cf-6a8e-476b-9083-bb479ab7eb8b > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(8) > div:nth-child(1) > div > div.bmm-l-col.bmm-l-col-9 > div > div.bmm-c-field__input > textarea",
        "下書き保存": "#SellUI-react-component-457a7cb2-4c70-44f2-9598-a49559a9e794 > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div.sell-btnbar > div > button.bmm-c-btn.bmm-c-btn--sec.bmm-c-btn--m.bmm-c-btn--thick",
        "閉じる": "#modal-root > div:nth-child(8) > div > div > div.bmm-c-btns.bmm-c-btns--align-right.bmm-c-btns--balance-width.bmm-c-modal__btns > button.bmm-c-btn.bmm-c-btn--b.bmm-c-btn--l"
    }

    template = {
        "商品コメント": """
【トラブル回避のため、ご購入前に必ずお読みください。】

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
"""
    }

    @classmethod
    def active(cls, xpath=""):
        cls.find_element_by_css_selector(xpath)

    pass

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
    _user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"

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
            chrome_options=options
        )
        # デフォルト待機時間の設定
        # self._driver.implicitly_wait(10)        

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


def main(event, context):

    chrome = Chrome()
    ex = Exhibiter()
    driver = chrome._driver

    path = "~/Desktop/buyma.com&balenciaga+bag.researched.csv"

    driver.get(ex.URLS["LOGIN_URL"])

    """ LOGIN """
    driver.find_element_by_id('txtLoginId').send_keys("ec-customer-support@valis.jp")
    chrome.screenshot(filename="/tmp/buyma1.png")
    driver.find_element_by_id('txtLoginPass').send_keys("VALISsugihara1")
    chrome.screenshot(filename="/tmp/buyma2.png")
    driver.find_element_by_id('login_do').click()
    chrome.screenshot(filename="/tmp/buyma3.png")

    """ フォーム入力 """
    driver.get(ex.URLS["SELL_URL"])
    h1_text = driver.find_element_by_css_selector("#SellUI-react-component-b3b598cf-6a8e-476b-9083-bb479ab7eb8b > div > div > div > div.bmm-c-heading.sell-heading > h1").text
    if h1_text != "新規出品":
        chrome.screenshot(filename="/tmp/error_1.png")
        raise Exception("出品ページへ遷移出来ませんでした")

    # 商品名
    df = pd.read_csv(path)
    for index, row in df.iterrows():

        # 画像DL
        images = []
        i = 0
        for url in row["retailer_images"].split("@@@"):
            response = requests.get(url)
            if response.status_code == 200:
                image = response.content
                with open("/tmp/image_%s" % (str(i),), "wb") as f:
                    f.write(image)
                    i += 1
                    images.append("/tmp/image_%s" % (str(i),))
        # 商品画像
        driver.find_element_by_css_selector(ex.elements["商品画像"]).send_keys(",".join(images))
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "商品画像")

        # 商品タイトル
        title = row["brand"] + " " + row["retailer_title"]
        kana_title = [english_to_katakana(word) for word in title.split()]
        driver.find_element_by_css_selector(ex.elements["商品名"]).send_keys(title)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "商品名")

        # 商品コメント
        comment = "※作成中\n"
        comment += row["retailer_description"] + "\n"
        comment += ex.template["商品コメント"]
        driver.find_element_by_css_selector(ex.elements["商品コメント"]).send_keys(comment)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "商品コメント")

        # TODO:: カテゴリ

        # ブランド
        brand = row["brand"]
        driver.find_element_by_css_selector(ex.elements["ブランド"]).send_keys(brand)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "ブランド")

        # 商品価格
        price = int(row["active_price"])
        driver.find_element_by_css_selector(ex.elements["商品価格"]).send_keys(price)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "商品価格")

        # 参考価格
        label_ = "#SellUI-react-component-b3b598cf-6a8e-476b-9083-bb479ab7eb8b > div > div > div > div.bmm-l-cnt__body.sell-body.is-btnbar-fixed > form > div:nth-child(7) > div:nth-child(2) > div > div.bmm-l-col.bmm-l-col-9 > div > div > div:nth-child(1) > div > label:nth-child(2)"
        driver.find_element_by_css_selector(label_).click()
        origin_price = int(row["retailer_origin_price"])  # TODO:: toInt
        driver.find_element_by_css_selector(ex.elements["参考価格"]).send_keys(origin_price)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "参考価格")

        # 買付先名
        retailer = row["retailer"]
        driver.find_element_by_css_selector(ex.elements["買付先名"]).send_keys(retailer)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "買付先名")

        # 買付先URL
        href = row["href"]
        driver.find_element_by_css_selector(ex.elements["買付先URL"]).send_keys(href)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "買付先URL")

        # 説明
        today_ = datetime.today().strftime('%Y/%m/%d') + "時点"
        driver.find_element_by_css_selector(ex.elements["説明"]).send_keys(today_)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "説明")

        # 出品メモ
        memo = [row["retailer_brand"], row["retailer_title"], row["retailer_price"], row["retailer_origin_price"], row["retailer_sku"]]
        memo = ",".join(memo)
        driver.find_element_by_css_selector(ex.elements["出品メモ"]).send_keys(memo)
        chrome.screenshot(filename="/tmp/{0}{1}_{2}.png").format(row["brand"], str(index), "出品メモ")

        # 出品メモ
        driver.find_element_by_css_selector(ex.elements["下書き保存"]).click()
        time.sleep(5)
        driver.find_element_by_css_selector(ex.elements["閉じる"]).click()
        driver.get(ex.URLS["SELL_URL"])

    driver.close()
    driver.quit()


    return True


main(1,1)