from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from typing import List, Dict

def vlk_parser() -> List[str]:
    driver = webdriver.Chrome()
    driver.get('https://www.drevenyvlk.cz/cz/page/tydenni-menu.html')

    wait = WebDriverWait(driver, 10)
    iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'iframe')))

    driver.switch_to.frame(iframe)

    iframe_content = driver.page_source

    driver.quit()

    soup = BeautifulSoup(iframe_content, "html.parser")
    menu_items = soup.find_all('div', class_='inner-layer item')

    menu = []
    for item in menu_items:
        name = item.find('div', class_='item-name').get_text(strip=True)
        price = item.find('div', class_='item-price-down').get_text(strip=True)
        menu.append(f"{name} {price}")

    return menu