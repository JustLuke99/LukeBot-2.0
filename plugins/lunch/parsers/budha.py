from datetime import datetime
from typing import List, Dict

import requests
from bs4 import BeautifulSoup


def budha_parser() -> List[Dict]:
    url = "http://www.indian-restaurant-buddha.cz/"

    current_date = datetime.now().strftime("%d. %m.")
    if current_date[0] == "0":
        current_date = current_date[1:]

    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError()

    html_content = response.content.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    date_headings = soup.find_all("h2")

    for heading in date_headings:
        if current_date in heading.text:
            next_element = heading.find_next_sibling()
            while next_element and (
                next_element.name != "h2" or current_date in next_element.text
            ):
                if next_element.name != "h2":
                    return next_element.text.strip().replace("\r\r", "").split("\n")
