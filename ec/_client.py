from bs4 import BeautifulSoup
import pandas as pd

class Client():
    url = None
    soup = None

    def __init__(self, channel=None):
        self.channel = channel

    def scoop(self):
        self.soup = BeautifulSoup(self.channel.html, 'html.parser')

    def search(self, keywords: list = [], **kwargs):
        self.keyword = "+".join(keywords)
        url = self.channel.activate_search(keywords, **kwargs)
        self.channel.search(url)
        self.scoop()
        self.channel.driver.exit()

    def collect(self, **add_property):
        return self.channel.collect(self, **add_property)

    def activate_search(self, keywords: list = []):
        return self.channel.activate_search(keywords)

    def activate_collect(self, keywords:list=[]):
        self._channel.search_properties["AND_METHOD"].join(keywords)

    def check_status(self):
        pass

    def to_df(self, data:dict={}, columns:list=[], save:str=False):
        df = pd.DataFrame.from_dict(data, orient="index", columns=columns)
        df = df.dropna()
        if save is not False:
            df.to_csv(save)
        return df