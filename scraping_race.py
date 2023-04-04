from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
import pandas as pd
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bs4 import BeautifulSoup
from parser.dataclass import *
from parser.db_search_parser import all_race
from parser.db_race_parser import *


url = r"https://db.netkeiba.com//?pid=race_list&word=&start_year=1988&start_mon=none&end_year=none&end_mon=none&jyo[0]=01&jyo[1]=02&jyo[2]=03&jyo[3]=04&jyo[4]=05&jyo[5]=06&jyo[6]=07&jyo[7]=08&jyo[8]=09&jyo[9]=10&kyori_min=&kyori_max=&sort=date&list=100&page="
FIREFOX_PROFILE = r"C:\Users\temp\AppData\Roaming\Mozilla\Firefox\Profiles\oi8lq9qu.forselenium"
options = Options()
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILE)


if __name__ == "__main__":
    driver = webdriver.Firefox(
        executable_path=GeckoDriverManager().install(), options=options
    )
    engine = create_engine("sqlite:///racedata.sqlite3")
    Base.metadata.create_all(bind=engine)
    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()

    done = session.query(RaceInfo).all()
    done_id = [i._id for i in done]

    for i in range(141, 1212):
        driver.get(url + str(i))
        driver.implicitly_wait(10)
        original_window = driver.current_window_handle

        raceinfos = all_race(driver.page_source)
        for j in range(len(raceinfos)):
            race = raceinfos[j]
            _id = race._id

            # すでに取得済みのレースはスキップ
            if int(_id) in done_id:
                continue

            driver.switch_to.new_window("tab")
            driver.get(f"https://db.netkeiba.com/race/{race._id}")
            driver.implicitly_wait(10)

            race.set_direction(driver.page_source)

            races = get_race(driver.page_source, _id)
            oddses = get_odds(driver.page_source, _id)
            truck_infos = get_truck_info(driver.page_source, _id)
            corner_infos = get_corner_info(driver.page_source, _id)
            lap_times = get_lap_time(driver.page_source, _id)
            race_analysis = get_race_analysis(driver.page_source, _id)
            short_comment = get_short_comment(driver.page_source, _id)

            session.add_all(races)
            session.add_all(oddses)
            if truck_infos:
                session.add(truck_infos)
            if corner_infos:
                session.add(corner_infos)
            if lap_times:
                session.add(lap_times)
            if race_analysis:
                session.add(race_analysis)
            if short_comment:
                session.add_all(short_comment)

            session.add(race)
            session.commit()
            driver.close()
            driver.switch_to.window(original_window)
