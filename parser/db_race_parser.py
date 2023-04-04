from .dataclass import *
from bs4 import BeautifulSoup
import itertools


def get_race(html: str, _id: int) -> list[Race]:
    soup = BeautifulSoup(html, "html.parser")
    table = soup.findAll("table")
    race_table = table[0]

    res = []
    for tr in race_table.find_all("tr")[1:]:
        temp = Race()
        temp.from_tr(tr)
        temp.set_id(_id)
        res.append(temp)
    return res


def get_odds(html: str, _id: int) -> list[Odds]:
    soup = BeautifulSoup(html, "html.parser")
    pay_block = soup.find(class_="pay_block")
    trs = pay_block.find_all("tr")
    res = []
    for tr in trs:
        kind = tr.find("th").text
        atari, henkin, ninki = tr.find_all("td")
        atari = atari.get_text("UNKO").split("UNKO")
        henkin = henkin.get_text("UNKO").split("UNKO")
        ninki = ninki.get_text("UNKO").split("UNKO")
        res += [
            Odds(_id, kind, a, h, n) for a, h, n in zip(atari, henkin, ninki)
        ]

        # 種類と1頭目と人気が同じものがあるのでその時は人気を＋１する
        for i, j in itertools.combinations(range(len(res)), 2):
            if (
                res[i].kind == res[j].kind
                and res[i].umaban1 == res[j].umaban1
                and res[i].popularity == res[j].popularity
            ):
                res[i].popularity = int(res[i].popularity) + 1

    return res


def get_truck_info(html: str, _id: int) -> TruckInfo | None:
    soup = BeautifulSoup(html, "html.parser")
    result_info = soup.find_all(class_="result_info")
    tables_left = result_info[0].find_all("table")
    for table in tables_left:
        if re.search(r"馬場指数", table.text):
            baba_index = table
            break
    else:
        return None
    return TruckInfo(_id, baba_index)


def get_corner_info(html: str, _id: int) -> CornerInfo | None:
    soup = BeautifulSoup(html, "html.parser")
    result_info = soup.find_all(class_="result_info")
    tables_left = result_info[0].find_all("table")
    for table in tables_left:
        if re.search(r"コーナー通過順位", table.text):
            corner_index = table
            break
    else:
        return None
    return CornerInfo(_id, corner_index)


def get_lap_time(html: str, _id: int) -> LapTime | None:
    soup = BeautifulSoup(html, "html.parser")
    result_info = soup.find_all(class_="result_info")
    tables_left = result_info[0].find_all("table")
    for table in tables_left:
        if re.search(r"ラップタイム", table.text):
            lap_time = table
            break
    else:
        return None
    return LapTime(_id, lap_time)


def get_race_analysis(html: str, _id: int) -> RaceAnalysis | None:
    soup = BeautifulSoup(html, "html.parser")
    result_info = soup.find_all(class_="result_info")
    tables_right = result_info[1].find_all("table")
    for table in tables_right:
        if re.search(r"レース分析", table.text):
            race_anal_table = table
            break
    else:
        return None
    return RaceAnalysis(_id, race_anal_table)


def get_short_comment(html: str, _id: int) -> ShortComment | None:
    soup = BeautifulSoup(html, "html.parser")
    result_info = soup.find_all(class_="result_info")
    tables_right = result_info[1].find_all("table")
    for table in tables_right:
        if re.search(r"レース後の短評", table.text):
            race_tanpyo_table = table
            break
    else:
        return None

    ths = race_tanpyo_table.find_all("th")
    tds = race_tanpyo_table.find_all("td")
    if ths is None or tds is None:
        return
    return [ShortComment().init_thtd(_id, th, td) for th, td in zip(ths, tds)]
