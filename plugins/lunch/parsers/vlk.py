import datetime
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def vlk_parser() -> List[str]:
    driver = webdriver.Chrome()
    driver.get("https://www.drevenyvlk.cz/cz/page/tydenni-menu.html")

    wait = WebDriverWait(driver, 10)
    iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))

    driver.switch_to.frame(iframe)

    iframe_content = driver.page_source

    driver.quit()

    soup = BeautifulSoup(iframe_content, "html.parser")

    menu_items = []
    current_date = None

    for div in soup.find_all("div"):
        if "date inner-layer" in " ".join(div.get("class", "")):
            current_date = div.text.strip()

        if "inner-layer item" in " ".join(div.get("class", "")):
            menu_item = {
                "date": current_date,
                "name": div.find("div", {"class": "item-name"}).text.strip(),
                "description": div.find(
                    "div", {"class": "item-description"}
                ).text.strip(),
                "price": div.find("div", {"class": "item-price-down"}).text.strip(),
            }
            menu_items.append(menu_item)

    today_menu = []
    today_day = datetime.datetime.now().strftime("%A")
    for item in menu_items:
        if today_day in item["date"]:
            today_menu.append(f"{item['name']} {item['price']}")

    return today_menu
