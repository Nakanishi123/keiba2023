from sqlalchemy import create_engine
from sqlalchemy import distinct
from sqlalchemy.orm import sessionmaker
from parser.dataclass import *
from parser.db_horse_parser import *
from tqdm import tqdm
import random


if __name__ == "__main__":
    engine = create_engine("sqlite:///racedata.sqlite3")
    Base.metadata.create_all(bind=engine)
    SessionClass = sessionmaker(engine)  # セッションを作るクラスを作成
    session = SessionClass()

    do = set([i[0] for i in session.query(distinct(Race.horse_id)).all()])
    done = set([i[0] for i in session.query(distinct(HorseResult._id)).all()])
    todo = list(do - done)
    todo = random.sample(todo, len(todo))

    # # 出走馬にhorse_idが1984000000以下の馬がふくまれるRaceをすべて取得
    # no_need = session.query(Race).filter(Race.horse_id < 1984000000).all()
    # no_need_id = tuple(set([i._id for i in no_need]))
    # race_del = session.query(Race).filter(Race._id.in_(no_need_id)).delete()
    # raceI_del = (
    #     session.query(RaceInfo).filter(RaceInfo._id.in_(no_need_id)).delete()
    # )
    # session.commit()
    for i in tqdm(todo):
        if i < 1984000000:  # 1984年より前の馬は列がそれ以降と違うのでスキップ
            tqdm.write(str(i))
            continue
        else:
            pass
        url = f"https://db.netkeiba.com/horse/{i}/"
        cj = browser_cookie3.firefox()
        r = requests.get(url, cookies=cj)
        r.encoding = "EUC-JP"
        horse_results = get_horse_result_from_top(r.text, i)
        horse_ped = get_horse_ped_from_top(r.text, i)

        session.add_all(horse_results)
        session.add(horse_ped)
        session.commit()
