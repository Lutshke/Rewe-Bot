from typing import List
from bs4 import BeautifulSoup, Tag
from Klassen.angebot import Angebot
import Klassen.config as config
from selenium.webdriver import Firefox
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep

from Klassen.webhook import send_message

CONFIG = config.get_config()

xpaths = [
    '//*[@id="sos-filter-category-checkbox-kuehlung"]',
    '//*[@id="sos-filter-category-checkbox-tiefkuehl"]',
    '//*[@id="sos-filter-category-checkbox-suesses-und-salziges"]',
    '//*[@id="sos-filter-category-checkbox-alkoholfreie-getraenke"]',
    '//*[@id="sos-filter-category-checkbox-bier"]',
    '//*[@id="sos-filter-category-checkbox-wein-und-spirituosen"]'
]


def accept_cookies(driver):

    wait = WebDriverWait(driver, 30)
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "/html/body/div[8]/div[3]/div/div[2]/div")))

    sleep(1.5)

    driver.find_element_by_xpath('//*[@id="uc-btn-accept-banner"]').click()


def get_driver():
    if CONFIG['webdriver'] == 'firefox':
        return Firefox(executable_path="./web/geckodriver.exe", service_log_path="./logs/firefox.log")
    return Chrome(executable_path="./web/chromedriver.exe", service_log_path="./logs/chrome.log")


def get_source() -> str:
    driver = get_driver()
    driver.get(CONFIG.get("rewe_url"))

    accept_cookies(driver)

    for xpath in xpaths:
        driver.find_element_by_xpath(xpath).click()

    driver.find_element_by_xpath(
        "/html/body/div[2]/div[1]/div[3]/div[1]/div[2]/div/div[2]/button[1]").click()

    found_button = driver.find_elements_by_class_name("sos-category__button")

    buttons = [found_button[index]
               for index in range(len(found_button)) if found_button[index].text]

    for button in buttons:
        driver.execute_script("return arguments[0].scrollIntoView()", (button))
        button.click()

    html_source_code: str = driver.execute_script(
        "return document.body.innerHTML;")

    driver.close()

    return html_source_code


def filter_source(source: str) -> List[str]:
    source = source.replace("\n", "").replace("\t", "")
    html_soup = BeautifulSoup(source, 'html.parser')

    kategorien = html_soup.find_all("div", class_="sos-category")

    for kategorie in kategorien:
        kategorie: Tag = kategorie
        category_name = kategorie.find(
            "span", class_="sos-category__header__text").string
        category_angebote = kategorie.find(
            "div", class_="sos-category__grid").find_all("article")

        if category_name in CONFIG["ignore"]:
            continue

        kategorien: List[Angebot] = []
        for angebot in category_angebote:
            try:
                name = angebot.find(
                    "div", class_="cor-offer-title").string.replace("REWE to go", "").replace("ue", "ü")
                price = angebot.find(
                    "div", class_="cor-offer-price").find(
                        "div", class_="cor-offer-price-amount").string
                kategorien.append(Angebot(name, price))
            except Exception:
                continue

        send_message(category_name, kategorien)


if __name__ == "__main__":
    source = get_source()
    filter_source(source)
