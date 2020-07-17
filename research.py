from ec._client import Client
from ec.channels.curators import Lyst
from ec.channels.retailers import Ruelala, Mytheresa, Farfetch, Vitkac, Modes, Forzieri, Mybag, Coggles
from ec.channels.malls import BuymaItems

import pandas as pd
import re

def test(event, context):
    # keywords = ["FURLA"]

    # lyst = Lyst()
    # c = Client(lyst)
    # c.search(keywords=keywords)
    # data, columns = c.collect()
    # # print(data)
    # path = "~/Desktop/%s&%s.collected.csv" % (c.channel.name, "+".join(keywords),)
    # df_curator = c.to_df(data=data, columns=columns, save=path)

    keywords = ["FURLA"]
    path = "~/Desktop/Lyst.com&FURLA.collected.csv"

    df_curator = pd.read_csv(path)
    print(df_curator.head())

    data_dict = {}
    for index, row in df_curator.iterrows():
        retailer_name = row["retailer"].replace(" ", "").capitalize().strip()
        if retailer_name in ("Ruelala", "Mytheresa", "Farfetch", "Vitkac", "Modes", "Forzieri", "Mybag", "Coggles",):
            retailer = globals()[retailer_name](row["href"])
            c = Client(retailer)
            c.search()
            data, columns = c.collect()
            print(data)
            try:
                data_dict[index] = data[0]
            except KeyError:
                data_dict[index] = [None,None,None,None,None]

    path = "~/Desktop/%s&%s.retailer.csv" % (c.channel.name, "+".join(keywords),)
    retailer_df = c.to_df(data=data_dict, columns=columns, save=path)

    path = "~/Desktop/%s&%s.curator-retailer.csv" % (c.channel.name, "+".join(keywords),)
    df2 = pd.concat([df_curator, retailer_df], axis=1)
    df2.to_csv(path)

    # df2 = pd.read_csv(path)
    df2 = df2.dropna()
    buymaItems = BuymaItems()

    ptn = r".+[^\-A-Z0-9]([\-A-Z0-9]+$)"
    prc_ptn = r"[^0-9\.]"
    active_dict = {}
    for index, row in df2.iterrows():
        sku = re.sub(ptn, r"\1", row["retailer_sku"])
        cheapest_price = row["retailer_price"] if any(row["retailer_price"]) else "9999999999"  # if "通過" があるので str 型にしておく

        if "€" in cheapest_price:
            # cheapest_price = float(cheapest_price.replace("€", "").replace(",", "").strip()) * 120
            cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 120
        elif "£" in cheapest_price:
            # cheapest_price = float(cheapest_price.replace("£", "").replace(",", "").strip()) * 135
            cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 135
        elif "$" in cheapest_price:
            # cheapest_price = float(cheapest_price.replace("$", "").replace(",", "").strip()) * 108
            cheapest_price = float(re.sub(prc_ptn, "", cheapest_price)) * 108
        elif "¥" in cheapest_price or "JPY" in cheapest_price:
            # cheapest_price = float(cheapest_price.replace("¥", "").replace("JPY", "").replace(",", "").strip())
            cheapest_price = float(re.sub(prc_ptn, "", cheapest_price))

        c = Client(buymaItems)
        c.search(keywords=[sku])
        data, columns = c.collect()
        prices = [v for k, values in data.items() for v in values]
        active_dict[index] = BuymaItems.compare(cheapest_price, prices)

    path = "~/Desktop/%s&%s.malls.csv" % (c.channel.name, "+".join(keywords),)
    mall_df = c.to_df(data=active_dict, columns=["active"], save=path)
    # mall_df = pd.DataFrame.from_dict(active_dict, orient="index", columns=["active"])
    df3 = pd.concat([df2, mall_df], axis=1)

    active_df = df3[df3["active"]==1]
    path = "~/Desktop/%s&%s.researched.csv" % (c.channel.name, "+".join(keywords),)
    active_df.to_csv(path)

    return True



test(1,1)
