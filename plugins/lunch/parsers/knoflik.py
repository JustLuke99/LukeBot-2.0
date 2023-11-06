from typing import List, Dict

import requests
from bs4 import BeautifulSoup


def knoflik_parser() -> List[Dict]:
    url = "http://brnorestaurace.cz/tydenni-menu/"

    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError()

    html_content = response.content.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    table = soup.find("table", id="dmenu-small")
    rows = table.find_all("tr")

    result = []
    for row in rows:
        tag = row.find_all("strong")
        tag2 = tag[0].get_text(strip=True)
        food_name = tag[0].next_sibling.strip()
        price = row.find(class_="mright").get_text(strip=True)
        result.append(f"{tag2} {food_name} {price}")

    return result
