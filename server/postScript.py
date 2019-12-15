from concurrent.futures import ThreadPoolExecutor
import socket
from bottle import Bottle, request, template, run, static_file
import requests


def get_it(url):
    try:
        for i in range(5):
            res = requests.post('http://{}{}'.format(url, "/board_concurrent"),
                                data="post " + str(i))

            print("[response] " + str(res))

        return

    except Exception as e:
        print("[ERROR] " + str(e))
        pass


urls = [
    "10.1.0.1",
    "10.1.0.2",
    "10.1.0.3",
    "10.1.0.4",
    "10.1.0.5",
    "10.1.0.6",
    "10.1.0.7",
    "10.1.0.8"
]

with ThreadPoolExecutor(max_workers=8) as pool:
    for _ in pool.map(get_it, urls):
        pass
