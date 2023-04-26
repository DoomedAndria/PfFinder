import time
import asyncio
from selenium import webdriver
from bs4 import BeautifulSoup

pic = "https://avatars.cloudflare.steamstatic.com/68c6254baedf2455107a2793d1080848a9526c56_medium.jpg"

name = "scumbagwill"


def find_profile(name, pic):
    pic2 = pic.replace('cloudflare','akamai')
    url = "https://steamcommunity.com/search/users/#page={page}&text=" + name
    page_src = ""

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    for i in range(1, 60):
        driver.get(url.format(page=i))
        time.sleep(1)
        html = driver.page_source

        if pic in html:
            # print("page you are looking for is " + str(i))
            page_src = html
            break
        elif pic2 in html:
            pic = pic2
            page_src = html
            break
    driver.quit()
    if not page_src:
        print("could not find")

    soup = BeautifulSoup(page_src, 'html.parser')
    a = soup.find("img", src=pic).parent
    p_link = a.get('href')
    return p_link

# print(find_profile(name,pic))
