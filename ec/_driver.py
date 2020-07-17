from abc import ABCMeta, abstractmethod
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import requests
import time


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


class Requests(Driver):    
    _driver = None
    _user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"

    def __init__(self):
        self._driver = requests

    def access(self, url: str = ""):
        # self._driver.get(url)
        pass

    def get_html(self, url: str):
        headers = {'User-Agent': self._user_agent}
        response = self._driver.get(url, headers=headers)
        # TODO:: ErrorHandling
        if str(response.status_code) == "429":
            print("-- Maybe Too Many Requests... 3seconds Wait...")
            print(response.status_code)
            print(response.headers)
            print(response.request.headers)
            time.sleep(int(response.headers["Retry-After"]))
            return self.get_html(url)
        return response.text

    def exit(self):
        pass
