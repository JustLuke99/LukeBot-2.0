from typing import List

import requests
from bs4 import BeautifulSoup


def zlatalod_parser() -> List[str]:
    url = "https://www.zlatalod.com/menu/"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(f"zlatalod vrátila status {response.status_code}")

    html_content = response.content.decode("utf-8")
    soup = BeautifulSoup(html_content, "html.parser")
    menu_table = soup.find("table", class_="menu-one-day")
    menus = []

    if menu_table:
        rows = menu_table.find_all("tr")

        polevka = False
        for row in rows:
            if "Polévka" in row.get_text():
                polevka = True

            if "Dezert" in row.get_text():
                break

            if not polevka:
                continue

            columns = row.find_all(["th", "td"])
            if columns:
                meal_name = columns[0].text.strip().replace("\r\n", "").lower()
                meal_price = (
                    columns[1].text.strip().replace("\r\n", "").lower()
                    if len(columns) > 1
                    else ""
                )
                if f"{meal_name} {meal_price}" != " ":
                    menus.append(f"{meal_name} {meal_price}")

    return menus
