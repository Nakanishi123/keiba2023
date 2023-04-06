from .dataclass import *
from bs4 import BeautifulSoup
import browser_cookie3
import requests
import bs4


def get_horse_result_from_top(html: str, _id: int) -> list[HorseResult] | None:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="db_h_race_results")
    if table is None:
        return None
    trs = table.find_all("tr")
    res = []
    for tr in trs[1:]:
        temp = HorseResult()
        temp.set_id(_id)
        temp.from_tr(tr)
        res.append(temp)
    return res


def get_horse_ped_from_top(html: str, _id: int) -> HorsePed | None:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="blood_table")
    if table is None:
        return None
    res = HorsePed()
    res.set_id(_id)
    res.from_table_ichiran(table)
    return res


if __name__ == "__main__":
    url = "https://db.netkeiba.com/horse/2019104462"
    cj = browser_cookie3.chrome()
    r = requests.get(url, cookies=cj)
    pass
