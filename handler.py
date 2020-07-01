import json
import boto3

# TODO:: toLayer
import constants
from shop import Shop

import requests
from bs4 import BeautifulSoup


def hello(event, context):

    print(event)

    data = json.loads(json.dumps(event))
    response = requests.get(data["page"])
    soup = BeautifulSoup(response.text, 'html.parser')
    hrefs = [c["href"] for c in soup.select('p.buyeritem_name a')]
    titles = [c.get_text().strip() for c in soup.select('p.buyeritem_name a')]

    items = []

    for href, title in zip(hrefs, titles):
        items.append([href, title])

    print("hrefs is ...", hrefs)
    print("titles is ...", titles)

    print("items is ...", items)

    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """


def test(event, context):

    shop = Shop(constants.shopper_list[0])

    # payload = json.dumps(event)

    # for i in range(1, shop.sales_total_pages + 1):
    for i in range(1, 10 + 1):
        url = shop.get_sales_now_url(i)
        payload = {
            "name": shop.name,
            "id": shop.id,
            "page": url
        }
        payload = json.dumps(payload)
        print(payload)
        response = boto3.client('lambda').invoke(
            FunctionName='buyma-app-dev-hello',
            InvocationType='Event',  # Event or RequestResponse
            Payload=payload
        )

    return response["Payload"].read().decode("utf-8")


