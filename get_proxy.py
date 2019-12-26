# generates proxy and checks it's usability

from proxyscrape import create_collector, get_collector
import requests


def gen_collection(uid):
    # generate acollection
    try:
        collector = create_collector(str(uid) + '-my-collector', ['http'])
    except:
        raise
    return collector, str(uid) + '-my-collector'


def generate_proxy(collector):
    # Retrieve any proxy
    proxy = collector.get_proxy()
    # checks the proxy if it works for google
    try:
        # implement and use check_proxy
        if proxy:
            return proxy
        else:
            generate_proxy(collector)
    except:
        generate_proxy(collector)


def check_proxy(proxy):
    proxy_dict = {
        proxy.type: proxy.host + ":" + proxy.port
    }
    res = requests.get("https://www.google.co.in/search?q=India", proxies=proxy_dict)
    if res.status_code == 200:
        return True
    else:
        return False
# collector, collector_name = gen_collection("dfg")
# proxy = generate_proxy(collector)
# print(proxy)
