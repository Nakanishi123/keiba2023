from .dataclass import *
from bs4 import BeautifulSoup


def all_race(page_source: str) -> list[RaceInfo]:
    soup = BeautifulSoup(page_source, "html.parser")
    table = soup.findAll("table")[0]  # 全体のテーブル
    trs = table.find_all("tr")  # 行のリスト
    race_infos = []
    for tr in trs[1:]:
        temp = RaceInfo()
        temp.from_search(tr)
        race_infos.append(temp)

    return race_infos


if __name__ == "__main__":
    all_race("UNKO")
    pass
