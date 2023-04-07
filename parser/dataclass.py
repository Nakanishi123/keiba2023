from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float, Text
import bs4
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import re

Base = declarative_base()


def parse_time(time_str: str) -> float:
    try:
        minutes, seconds = time_str.split(":")
        return float(minutes) * 60 + float(seconds)
    except:
        return None


def to_float(num_str: str) -> float:
    try:
        return float(num_str)
    except:
        return None


class RaceInfo(Base):
    __tablename__ = "race_info"

    _id = Column(Integer, primary_key=True)
    date = Column(Date)
    place = Column(Text)
    weather = Column(String(2))
    R = Column(Integer)
    name = Column(Text)
    movie_link = Column(Text)
    track = Column(String(1))  # 芝/ダート/障害
    distance = Column(Integer)  # 距離
    direction = Column(String(1))  # 左/右
    firm = Column(String(1))  # 良/稍重/重/不良
    num = Column(Integer)  # 頭数

    def from_search(self, tr: bs4.element.ResultSet) -> None:
        """
        検索結果のtrからレース情報を取得する.\n
        どちら周りかは取得できないのでset_directionで取得する必要がある.

        Args:
            tr (bs4.element.ResultSet): 検索結果のtr
        """
        tds = tr.find_all("td")
        self._id = re.findall(r"\d+", tds[4].find("a").get("href"))[0]
        self.date = datetime.date.fromisoformat(tds[0].text.replace("/", "-"))
        self.place = re.sub(r"\d", "", tds[1].text)
        self.weather = tds[2].text.strip()
        self.R = tds[3].text.strip()
        self.name = tds[4].text.strip()
        self.movie_link = (tds[5].find("a") or tds[5]).get(
            "href", None
        )  # 動画がない場合はNone
        self.track = tds[6].text.strip()[0]
        self.distance = int(tds[6].text.strip()[1:])
        self.firm = tds[8].text
        self.num = tds[7].text

    def set_direction(self, html: str) -> None:
        direction = re.findall(r"(左|右)\s*\d{3,5}m", html)
        self.direction = direction[0] if direction else None

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                [
                    self._id,
                    self.date,
                    self.place,
                    self.weather,
                    self.R,
                    self.name,
                    self.movie_link,
                    self.track,
                    self.distance,
                    self.direction,
                    self.firm,
                    self.num,
                ]
            ],
            columns=[
                "id",
                "開催日",
                "場所",
                "天気",
                "R",
                "レース名",
                "映像",
                "種類",
                "距離",
                "向き",
                "馬場",
                "頭数",
            ],
        )


class Race(Base):
    __tablename__ = "race"

    # 表からは直接見えないID関係
    _id = Column(Integer, primary_key=True)
    horse_id = Column(Integer, primary_key=True)
    kishu_id = Column(Integer)
    chokyoshi_id = Column(Integer)
    banushi_id = Column(Integer)

    # 表から見える情報
    chakujun = Column(Integer)  # 着順
    wakuban = Column(Integer)  # 枠番
    umaban = Column(Integer)  # 馬番
    bamei = Column(String(30))  # 馬名
    sex = Column(String(1))  # 性齢(左)
    age = Column(Integer)  # 性齢(右)
    kinryo = Column(Integer)  # 斤量
    kishu_name = Column(String(30))  # 騎手
    time = Column(Float)  # タイム
    chakusa = Column(String(10))  # 着差
    time_index = Column(Integer)  # タイム指数
    tsuka_1 = Column(Integer)
    tsuka_2 = Column(Integer)
    tsuka_3 = Column(Integer)
    tsuka_4 = Column(Integer)
    nobori = Column(Float)  # 上り
    tansho = Column(Float)  # 単勝
    ninki = Column(Integer)  # 人気
    bataiju = Column(Integer)  # 馬体重(左)
    zougen = Column(Integer)  # 馬体重(右)
    chokyo_time = Column(Text)  # 調教タイム
    umaya_comment = Column(Text)  # 厩舎コメント
    bikou = Column(String(30))  # 備考
    chokyoshi = Column(String(30))  # 調教師
    banushi = Column(String(30))  # 馬主
    shokin = Column(Float)  # 賞金

    def from_tr(self, tr: bs4.element.ResultSet) -> None:
        tds = tr.find_all("td")
        chakujun_num = re.findall(r"\d+", tds[0].get_text(strip=True))
        if chakujun_num == []:
            self.chakujun = None
        else:
            self.chakujun = int(chakujun_num[0])

        self.wakuban = tds[1].get_text(strip=True)
        self.umaban = tds[2].get_text(strip=True)
        self.bamei = tds[3].get_text(strip=True)
        self.horse_id = re.findall(r"\d{5,}", tds[3].find("a").get("href"))[0]
        self.sex = tds[4].get_text(strip=True)[0]
        self.age = int(tds[4].get_text(strip=True)[1:])
        self.kinryo = tds[5].get_text(strip=True)
        self.kishu_name = tds[6].get_text(strip=True)
        self.kishu_id = re.findall(r"\d+", tds[6].find("a").get("href"))[0]
        self.time = parse_time(tds[7].get_text(strip=True))
        self.chakusa = (
            tds[8].get_text(strip=True)
            if tds[8].get_text(strip=True)
            else None
        )
        self.time_index = (
            int(tds[9].get_text(strip=True))
            if tds[9].get_text(strip=True)
            else None
        )
        self.parse_tsuka(tds[10].get_text(strip=True))
        self.nobori = to_float(tds[11].get_text(strip=True))
        self.tansho = to_float(tds[12].get_text(strip=True))
        self.ninki = (
            tds[13].get_text(strip=True)
            if tds[13].get_text(strip=True).isdecimal()
            else None
        )
        self.parse_taiju(tds[14].get_text(strip=True))
        self.chokyo_time = (tds[15].find("a") or tds[15]).get("href", None)
        self.umaya_comment = (tds[16].find("a") or tds[16]).get("href", None)
        self.bikou = tds[17].get_text(strip=True)
        self.chokyoshi = tds[18].get_text(strip=True)
        self.chokyoshi_id = re.findall(r"\d+", tds[18].find("a").get("href"))[
            0
        ]
        self.banushi = tds[19].text.strip()
        banushi_id_a = tds[19].find("a")
        if banushi_id_a is not None:  # たまにIDのない馬主がいる
            self.banushi_id = re.findall(r"\d+", banushi_id_a.get("href"))[0]
        self.shokin = to_float(tds[20].text)

    def parse_tsuka(self, tsuka: str) -> None:
        if len(tsuka) == 0:  # 空白の時
            return
        tsukas = tsuka.split("-")
        if len(tsukas) == 0:
            return
        if len(tsukas) >= 1:
            self.tsuka_1 = int(tsukas[0])
        if len(tsukas) >= 2:
            self.tsuka_2 = int(tsukas[1])
        if len(tsukas) >= 3:
            self.tsuka_3 = int(tsukas[2])
        if len(tsukas) >= 4:
            self.tsuka_4 = int(tsukas[3])

    def parse_taiju(self, taiju: str) -> None:
        if taiju:
            taiju = taiju.split("(")
            try:
                self.bataiju = int(taiju[0])
            except:
                pass
            try:
                self.zougen = int(taiju[1][:-1])
            except:
                pass

    def set_id(self, id: int) -> None:
        self._id = id

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                [
                    self._id,
                    self.chakujun,
                    self.wakuban,
                    self.umaban,
                    self.bamei,
                    self.sex,
                    self.age,
                    self.kinryo,
                    self.kishu_name,
                    self.time,
                    self.chakusa,
                    self.time_index,
                    self.tsuka_1,
                    self.tsuka_2,
                    self.tsuka_3,
                    self.tsuka_4,
                    self.nobori,
                    self.tansho,
                    self.ninki,
                    self.bataiju,
                    self.zougen,
                    self.chokyo_time,
                    self.umaya_comment,
                    self.bikou,
                    self.chokyoshi,
                    self.banushi,
                    self.shokin,
                    self.horse_id,
                    self.kishu_id,
                    self.chokyoshi_id,
                    self.banushi_id,
                ]
            ],
            columns=[
                "id",
                "着順",
                "枠番",
                "馬番",
                "馬名",
                "性齢",
                "馬体重",
                "斤量",
                "騎手",
                "タイム",
                "着差",
                "タイム指数",
                "通過1",
                "通過2",
                "通過3",
                "通過4",
                "上り",
                "単勝",
                "人気",
                "馬体重",
                "増減",
                "調教タイム",
                "厩舎コメント",
                "備考",
                "調教師",
                "馬主",
                "賞金",
                "馬ID",
                "騎手ID",
                "調教師ID",
                "馬主ID",
            ],
        )


class Odds(Base):
    __tablename__ = "odds"

    _id = Column(Integer, primary_key=True)
    kind = Column(String(3), primary_key=True)  # 単勝/複勝/枠連/馬連/ワイド/馬単/3連複/3連単
    umaban1 = Column(Integer, primary_key=True)
    umaban2 = Column(Integer)
    umaban3 = Column(Integer)
    _return = Column(Integer)
    popularity = Column(Integer, primary_key=True)  # 人気

    def __init__(
        self, _id: int, kind: str, umabans: str, _return: str, popularity: str
    ):
        self._id = _id
        self.kind = kind
        self._return = re.sub(r"[^0-9]", "", _return)
        self.popularity = re.sub(r"[^0-9]", "", popularity)
        umaban_list = re.split(r"[-→]", umabans)
        if len(umaban_list) >= 1:
            self.umaban1 = int(umaban_list[0])
        if len(umaban_list) >= 2:
            self.umaban2 = int(umaban_list[1])
        if len(umaban_list) >= 3:
            self.umaban3 = int(umaban_list[2])

    def to_df(self) -> None:
        return self.__dict__


class TruckInfo(Base):
    __tablename__ = "track_info"

    _id = Column(Integer, primary_key=True)
    track_index = Column(Integer)  # 馬場指数
    track_comment = Column(Text)  # 馬場コメント

    def __init__(self, _id: int, table: bs4.element.ResultSet):
        tds = table.find_all("td")
        if tds is None:
            return

        self._id = _id
        self.track_index = re.findall(r"^-*\d+", tds[0].text)[0]
        if len(tds) >= 2:
            self.track_comment = tds[1].get_text(strip=True)


class CornerInfo(Base):
    __tablename__ = "corner_info"

    _id = Column(Integer, primary_key=True)
    corner1 = Column(String(100))
    corner2 = Column(String(100))
    corner3 = Column(String(100))
    corner4 = Column(String(100))

    def __init__(self, _id: int, table: bs4.element.ResultSet):
        trs = table.find_all("tr")
        for i in trs:
            num = re.findall(r"\d", i.text)
            if num is None:
                continue
            self._id = _id
            num = num[0]
            text = i.find("td").get_text(strip=True)
            if num == "1":
                self.corner1 = text
            elif num == "2":
                self.corner2 = text
            elif num == "3":
                self.corner3 = text
            elif num == "4":
                self.corner4 = text


class LapTime(Base):
    __tablename__ = "lap_time"

    _id = Column(Integer, primary_key=True)
    lap = Column(String(100))
    pace = Column(String(100))

    def __init__(self, _id: int, table: bs4.element.ResultSet):
        tds = table.find_all("td")
        if len(tds) == 0:
            return

        self._id = _id
        self.lap = tds[0].get_text(strip=True)
        self.pace = tds[1].get_text(strip=True)


class RaceAnalysis(Base):
    __tablename__ = "race_analysis"

    _id = Column(Integer, primary_key=True)
    comment = Column(Text)

    def __init__(self, _id: int, table: bs4.element.ResultSet):
        tds = table.find_all("td")
        if len(tds) == 0:
            return

        self._id = _id
        self.comment = tds[0].get_text(strip=True)


class ShortComment(Base):
    __tablename__ = "short_comment"

    _id = Column(Integer, primary_key=True)
    chakujun = Column(Integer, primary_key=True)
    name = Column(String(40), primary_key=True)
    comment = Column(Text)

    def init_thtd(
        self, _id: int, th: bs4.element.ResultSet, td: bs4.element.ResultSet
    ):
        self._id = _id

        # 出走できなかった馬にコメントを出している場合があるのでこうした．
        # 主キーにしてるのでとりあえず-1にしておく
        chakujun = re.findall(r"\d{1,2}", th.get_text(strip=True))
        if chakujun == []:
            self.chakujun = -1
        else:
            self.chakujun = chakujun[0]
        self.name = th.get_text(strip=True).split(":")[1]
        self.comment = td.get_text(strip=True)
        return self


class HorsePed(Base):
    __tablename__ = "horse_ped"
    _id = Column(String(15), primary_key=True)
    father = Column(String(15))  # 父
    mother = Column(String(15))  # 母

    def from_table_ichiran(self, table: bs4.element.ResultSet) -> None:
        """
        馬のTOPページから父母のIDを取得する
        血統のページでないので注意

        Args:
            table (bs4.element.ResultSet): 馬のTOPページの血統表
        """
        ids = [td.find("a").get("href") for td in table.find_all("td")]
        self.father = ids[0].replace("/horse/ped/", "").replace("/", "")
        self.mother = ids[3].replace("/horse/ped/", "").replace("/", "")

    def set_id(self, id: int) -> None:
        self._id = id


class HorseResult(Base):
    __tablename__ = "horse_result"

    _id = Column(Integer, primary_key=True)
    race_id = Column(String(10), primary_key=True)
    kishu_id = Column(String(10))

    date = Column(Date)
    place = Column(Text)
    weather = Column(String(2))
    R = Column(Integer)
    name = Column(Text)
    movie_link = Column(Text)
    num = Column(Integer)  # 頭数
    wakuban = Column(Integer)  # 枠番
    umaban = Column(Integer)  # 馬番
    odds = Column(Float)  # 単勝オッズ
    ninki = Column(Integer)  # 人気
    chakujun = Column(Integer)  # 着順
    kishu_name = Column(String(30))  # 騎手
    kinryo = Column(Integer)  # 斤量
    track = Column(String(1))  # 芝/ダート/障害
    distance = Column(Integer)  # 距離
    firm = Column(String(1))  # 良/稍重/重/不良
    truck_index = Column(Integer)  # 馬場指数
    time = Column(Float)  # タイム
    chakusa = Column(String(10))  # 着差
    time_index = Column(Integer)  # タイム指数
    tsuka_1 = Column(Integer)
    tsuka_2 = Column(Integer)
    tsuka_3 = Column(Integer)
    tsuka_4 = Column(Integer)
    pace = Column(String(25))  # ペース
    nobori = Column(Float)  # 上り
    bataiju = Column(Integer)  # 馬体重(左)
    zougen = Column(Integer)  # 馬体重(右)
    umaya_comment = Column(Text)  # 厩舎コメント
    bikou = Column(String(30))  # 備考
    winner = Column(String(30))  # 勝ち馬
    shokin = Column(Float)  # 賞金

    def from_tr(self, tr: bs4.element.ResultSet) -> None:
        tds = tr.find_all("td")

        self.date = datetime.date.fromisoformat(
            tds[0].get_text(strip=True).replace("/", "-")
        )
        self.place = re.sub(r"\d", "", tds[1].get_text(strip=True))
        self.weather = tds[2].get_text(strip=True)
        self.R = tds[3].get_text(strip=True)
        self.name = tds[4].get_text(strip=True)
        self.race_id = (
            tds[4].find("a").get("href").replace("race", "").replace("/", "")
        )
        self.movie_link = (tds[5].find("a") or tds[5]).get(
            "href", None
        )  # 動画がない場合はNone
        self.num = tds[6].get_text(strip=True)
        self.wakuban = tds[7].get_text(strip=True)
        self.umaban = tds[8].get_text(strip=True)
        self.odds = to_float(tds[9].get_text(strip=True))
        self.ninki = (
            tds[10].get_text(strip=True)
            if tds[10].get_text(strip=True).isdecimal()
            else None
        )
        chakujun_num = re.findall(r"\d+", tds[11].get_text(strip=True))
        if chakujun_num == []:
            self.chakujun = None
        else:
            self.chakujun = int(chakujun_num[0])
        self.kishu_name = tds[12].get_text(strip=True)
        kishu_id = tds[12].find("a")
        if kishu_id is not None:
            self.kishu_id = tds[12].find("a").get("href").split("/")[-2]
        self.kinryo = tds[13].get_text(strip=True)
        track_and_distance = tds[14].get_text(strip=True)
        track = re.findall(r"[芝ダ障]", track_and_distance)
        distance = re.findall(r"\d+", track_and_distance)
        if track != []:
            self.track = track[0]
        else:
            pass
        if distance != []:
            self.distance = int(distance[0])
        else:
            pass
        self.firm = tds[15].get_text(strip=True)
        self.truck_index = tds[16].get_text(strip=True)
        self.time = parse_time(tds[17].get_text(strip=True))
        self.chakusa = (
            tds[18].get_text(strip=True)
            if tds[18].get_text(strip=True)
            else None
        )
        self.time_index = (
            int(tds[19].get_text(strip=True))
            if tds[19].get_text(strip=True)
            else None
        )
        self.parse_tsuka(tds[20].get_text(strip=True))
        self.pace = tds[21].get_text(strip=True)
        self.nobori = to_float(tds[22].get_text(strip=True))
        self.parse_taiju(tds[23].get_text(strip=True))
        self.umaya_comment = (tds[24].find("a") or tds[24]).get("href", None)
        self.bikou = tds[25].get_text(strip=True)
        self.winner = tds[26].get_text(strip=True)
        self.shokin = to_float(tds[27].get_text(strip=True))

    def parse_tsuka(self, tsuka: str) -> None:
        if len(tsuka) == 0:  # 空白の時
            return
        tsukas = tsuka.split("-")
        if len(tsukas) == 0:
            return
        if len(tsukas) >= 1:
            self.tsuka_1 = int(tsukas[0])
        if len(tsukas) >= 2:
            self.tsuka_2 = int(tsukas[1])
        if len(tsukas) >= 3:
            self.tsuka_3 = int(tsukas[2])
        if len(tsukas) >= 4:
            self.tsuka_4 = int(tsukas[3])

    def parse_taiju(self, taiju: str) -> None:
        if taiju:
            taiju = taiju.split("(")
            try:
                self.bataiju = int(taiju[0])
            except:
                pass
            try:
                self.zougen = int(taiju[1][:-1])
            except:
                pass

    def set_id(self, id: int) -> None:
        self._id = id
