from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup


def radegast_parser() -> List[str]:
    url = "https://www.radegast-sportbar.cz/week-menu"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(f"radegast vrátil status {response.status_code}")

    html_content = response.content.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    menu_items = []
    days = soup.find_all("strong")

    today = ""
    for day in days:
        menu = {}

        if any(
            day_text in day.get_text()
            for day_text in ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek"]
        ):
            today = day.get_text()
        day_name = day.get_text()
        menu["Day"] = day_name

        items = day.find_next_siblings("span")

        for item in items:
            food = item.get_text()
            if food.strip() and food.endswith(",-"):
                menu_item = food.strip()
                menu_items.append({"Day": day_name, "Food": menu_item, "xd": today})

    current_date = datetime.now().strftime("%d.%m.")
    if current_date[0] == "0":
        current_date = current_date[1:]

    menus = []
    for item in menu_items:
        if current_date in item["xd"]:
            menus.append(f"{item['Food']}")

    menus.append(
        "Na Polívku, burgery a spešl jídla nemám bohužel mozkovou kapacitu. "
        "Bot je open, můžeš si to v klidu doprogramovat. GL"
    )

    return menus
