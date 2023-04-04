from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
from ..parse.race_parser import race_parser

FIREFOX_PROFILE = r"C:\Users\temp\AppData\Roaming\Mozilla\Firefox\Profiles\oi8lq9qu.forselenium"


def main(url: str):
    options = Options()
    options.profile = FIREFOX_PROFILE
    service = Service(executable_path=GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(url)
