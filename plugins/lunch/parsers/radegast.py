from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from datetime import datetime


def radegast_parser() -> List[Dict]:
    url = "https://www.radegast-sportbar.cz/week-menu"

    response = requests.get(url)

    if response.status_code != 200:
        raise RuntimeError()

    html_content = response.content.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")

    menu_items = []

    days = soup.find_all("strong")  # Nalezení všech prvků označených jako 'strong'

    today = ""
    for day in days:
        menu = {}  # Vytvoření prázdného slovníku pro každý den

        # Název dne
        if any(
            day_text in day.get_text()
            for day_text in ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek"]
        ):
            today = day.get_text()
        day_name = day.get_text()
        menu["Day"] = day_name

        # Nalezení prvků následujících po elementu 'strong' do prvků obsahujících ceny jídel
        items = day.find_next_siblings("span")

        # Extrahování názvů jídel a jejich cen

        for item in items:
            # Text názvu jídla a cena
            food = item.get_text()
            # Vynechání prázdných prvků a prvků neobsahujících cenu
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
        "Na Polívku, burgery a spešl jídla nemám bohužel mozkovou kapacitu. Bot je open, můžeš si to v klidu doprogramovat. GL"
    )

    return menus
