import math
import time
import requests
from bs4 import BeautifulSoup as bs
import threading
import json
from datetime import datetime
from test2 import find_profile
import queue
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://bibiashviliandria:andria1234@cluster0.ub53t9l.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['Seterebi']
col = db['users']



ACTIVITY_URL = "https://steamcommunity.com/market/itemordersactivity" \
               "?item_nameid=176118270&country=RU&language=english&currency=1&&two_factor=0&norender=1"  # not using it cause idk where it came from its cheating so ima do all myself

url = 'https://steamcommunity.com/market/itemordersactivity?country=RU&language=english&currency=1&item_nameid={' \
      'item_id}&two_factor=0 '

with open('listings.json', 'r', encoding='utf-8') as f:
    listings = json.load(f)

listings_list = [k for k, v in listings.items()]


# takes html block as an argument and scrapes useful data from it
def html_to_info(st, item_id):
    if "listed this item for sale" not in st:
        return
    ret = {}
    arr = st.split('\n')

    ret["name"] = arr[6].strip()
    ret["price"] = arr[8].replace('listed this item for sale for ', '')
    ret["img url: "] = arr[3][13:-3].replace('https://avatars.akamai.steamstatic.com/', 'https://avatars.cloudflare'
                                                                                        '.steamstatic.com/').replace(
        '.jpg', '_medium.jpg')
    ret["item_id"] = item_id
    # ret["prof_link"] = find_profile(ret["name"], ret["img url: "])
    ret['updated_at'] = datetime.now()
    return ret


# looks returns people if its item is in listings.json file(expensive)
def get_people_with_itemID(item_id):
    global q
    r = requests.get(url.format(item_id=item_id))
    time.sleep(1)
    activity = r.json()['activity']
    for element in activity:
        html = bs(element, 'html.parser').prettify()
        ret = html_to_info(html, item_id)
        if ret:
            ret['item'] = listings[item_id]

            q.put(ret)
            return ret


# gets people from desired segment(listing.json is devided in 50 parts) reason for
# this is to make threads life easier and make program faster i mean not to make threads do same stuff twise or more

num_of_threads = 100
browser_threads = 1
def get_people(num):
    try:
        segment = math.floor(len(listings_list) / num_of_threads)
        while True:
            for j in range(segment):
                index = num * segment + j
                get_people_with_itemID(listings_list[index])
    except Exception:
        get_people(num)


threads = []
b_threads = []
q = queue.Queue()
def do_search():
    global q
    while True:
        if not q.empty():
            ret = q.get()
            try:
                link = find_profile(ret["name"], ret["img url: "])
            except Exception:
                print("error finding profile")
                continue
            if link:
                try:
                    ret["prof_link"] = link
                    # if not(col.find_one({'name':ret['name'],'img url: ': ret['img url: ']})):
                    #     print(ret)
                    #     col.insert_one(ret)
                    # else:
                    #     print('already in db')
                    print(ret)
                    col.insert_one(ret)
                except Exception:
                    print("error inserting row")

# start getting people with 50 thread
def start():
    for i in range(num_of_threads):
        t = threading.Thread(target=get_people, args=(i,))
        t.daemon = True
        threads.append(t)
    for i in range(browser_threads):
        t = threading.Thread(target=do_search)
        t.daemon = True
        b_threads.append(t)
    for i in threads:
        i.start()
    for i in b_threads:
        i.start()
    for i in threads:
        i.join()
    for i in b_threads:
        i.join()


start()


"https://avatars.cloudflare.steamstatic.com/9e298df12906c30b60377632be52a6fcc5d77031_medium.jpg"
"https://avatars.akamai.steamstatic.com/79a33a352f7e02d2e0bc0eb0928fe2e584edef87_medium.jpg"
