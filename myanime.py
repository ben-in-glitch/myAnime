import sqlite3, os
from datetime import date
from contextlib import contextmanager
from pathlib import Path

#2026-01-05
#----------------------------SQL structure------------------------------------
anime = '''CREATE TABLE IF NOT EXISTS anime (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL UNIQUE,
                title_jp TEXT
)'''

season_status = '''CREATE TABLE IF NOT EXISTS season_status (
                id INTEGER PRIMARY KEY,
                anime_id INTEGER NOT NULL,
                season INTEGER NOT NULL,
                status TEXT NOT NULL
                    CHECK(status IN ('plan','watching','finished','next','quit')),
                season_title TEXT,
                total_episodes INTEGER DEFAULT 12,
                air_year INTEGER,
                air_season TEXT CHECK (air_season IN ('','winter','spring','summer','fall')) DEFAULT '',
                rate INTEGER CHECK(rate between -1 and 5) DEFAULT -1,
                UNIQUE (anime_id, season),
                FOREIGN KEY (anime_id)
                    REFERENCES anime(id)
                    ON DELETE CASCADE
)'''

episode_log = '''CREATE TABLE IF NOT EXISTS episode_log (
                id INTEGER PRIMARY KEY,
                season_status_id INTEGER NOT NULL,
                episode INTEGER NOT NULL,
                episode_title TEXT NOT NULL,
                watch_date DATE DEFAULT CURRENT_DATE,

                UNIQUE (season_status_id, episode),
                FOREIGN KEY (season_status_id) 
                    REFERENCES season_status(id)
                    ON DELETE CASCADE
)'''

#----------------------------SQL Functions-----------------------------------
class AnimeDB:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.DB_PATH = self.BASE_DIR / "myanime.db"
        self.db_path = self.DB_PATH

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        if os.path.exists(self.db_path):
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=ON")
                cur.execute(anime)
                cur.execute(episode_log)
                cur.execute(season_status)
            return True

        return False

    def remove_db(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            return True
        return False

# ----------------------------anime-----------------------------------------
    def anime_get_or_create(self,title,title_jp=None):
        select = "SELECT * FROM anime WHERE title = ?"
        insert = "INSERT INTO anime (title,title_jp) VALUES (?,?)"
        with self.get_connection() as conn:
            cur = conn.cursor()
            res = cur.execute(select,(title,)).fetchone()
            if not res:
                cur.execute(insert,(title,title_jp))
                return True, cur.lastrowid
            else:
                return False, res[0]

    def anime_delete(self, pk):
        select = "SELECT anime.title FROM anime WHERE id = ?"
        delete = "DELETE FROM anime WHERE id = ?"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            row = cur.execute(select,(pk,)).fetchone()
            if row:
                res = cur.execute(delete, (pk,))
                return res.rowcount > 0, row[0]
            else:
                return False, row

    def anime_update(self,pk,title=None,title_jp=None):
        fields,params = [], []
        if title is not None:
            fields.append("title = ?")
            params.append(title)
        if title_jp is not None:
            fields.append("title_jp = ?")
            params.append(title_jp)

        if not fields:
            return False

        params.append(pk)
        update = f"UPDATE anime SET {', '.join(fields)} WHERE id = ?"
        with self.get_connection() as conn:
            cur = conn.cursor()
            return cur.execute(update,params).rowcount > 0

# ----------------------------season_status---------------------------------
    def season_status_get_or_create(self,fk,season,status="plan",season_title = None,total_episodes = None,air_year = None,air_season = None,rate = None):
        select = "SELECT * FROM season_status WHERE anime_id = ? AND season = ?"
        insert = "INSERT INTO season_status (anime_id,season,status,season_title,total_episodes,air_year,air_season,rate) VALUES (?,?,?,?,?,?,?,?)"
        with self.get_connection() as conn:
            cur = conn.cursor()
            res = cur.execute(select,(fk,season)).fetchone()
            if not res:
                air_season = air_season.lower() if air_season else None
                params = [fk, season, status.lower(), season_title, total_episodes, air_year, air_season, rate]
                cur.execute(insert,params)
                return True, cur.lastrowid

            return False, res[0]

    def season_status_delete(self, pk):
        select = ("SELECT a.title AS anime_title, s.season AS season "
                  "FROM season_status s "
                  "LEFT JOIN anime a ON s.anime_id = a.id "
                  "WHERE s.id = ?")
        delete = "DELETE FROM season_status WHERE id = ?"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            row = cur.execute(select,(pk,)).fetchone()
            if row:
                res = cur.execute(delete, (pk,))
                return res.rowcount > 0, row

            return False, row

    def season_status_update(self,pk,anime_id = None,season=None,status=None,season_title=None,total_episodes = None,air_year = None,air_season = None,rate = None):
        fields,params =self.season_status_arguments(anime_id,season,status,season_title,total_episodes,air_year,air_season,rate)
        if not fields:
            return False
        params.append(pk)
        update = f"UPDATE season_status SET {', '.join(fields)} WHERE id = ?"

        with self.get_connection() as conn:
            cur = conn.cursor()
            return cur.execute(update,params).rowcount > 0

    @staticmethod
    def season_status_arguments(anime_id=None,season=None,status=None,season_title=None,total_episodes = None,air_year = None,air_season = None,rate = None):
        fields, params = [], []
        convert = {"anime_id":anime_id,
                   "season": season,
                   "status": status,
                   "season_title": season_title,
                   "total_episodes": total_episodes,
                   "air_year": air_year,
                   "air_season": air_season,
                   "rate": rate}
        for i, key in convert.items():
            if key is not None:
                fields.append(f"{i} = ?")
                params.append(key)
        return fields, params

# ----------------------------episode_log-----------------------------------
    def episode_log_get_or_create(self,fk,episode,episode_title = None,watch_date = date.today().isoformat()):
        select = "SELECT * FROM episode_log WHERE season_status_id = ? AND episode = ?"
        insert = "INSERT INTO episode_log (season_status_id,episode,episode_title,watch_date) VALUES (?,?,?,?)"
        with self.get_connection() as conn:
            cur = conn.cursor()
            res = cur.execute(select, (fk, episode)).fetchone()
            if not res:
                params = [fk, episode, episode_title, watch_date]
                cur.execute(insert,params)
                return True, cur.lastrowid

            return False, res[0]

    def episode_log_delete(self,pk):
        select = ("SELECT "
                  "a.title AS title, "
                  "s.season AS season, "
                  "e.episode AS episode, "
                  "e.episode_title AS episode_title "
                  "FROM episode_log e "
                  "LEFT JOIN season_status s "
                  "ON s.id = e.season_status_id "
                  "LEFT JOIN anime a "
                  "ON a.id = s.anime_id "
                  "WHERE e.id = ?")
        delete = "DELETE FROM episode_log WHERE id = ?"
        with self.get_connection() as conn:
            cur = conn.cursor()
            row = cur.execute(select, (pk,)).fetchone()
            if row:
                res = cur.execute(delete,(pk,))
                return res.rowcount > 0, row
            return False, row

    def episode_log_update(self,pk,season_status_id=None,episode=None,episode_title = None,watch_date = None):
        fields,params = self.episode_log_arguments(season_status_id,episode,episode_title,watch_date)
        if not fields:
            return False
        params.append(pk)
        update = f"UPDATE episode_log SET {', '.join(fields)} WHERE id = ?"
        with self.get_connection() as conn:
            cur = conn.cursor()
            res = cur.execute(update,params).rowcount
            return res > 0

    @staticmethod
    def episode_log_arguments(season_status_id=None,episode=None,episode_title=None,watch_date=None):
        fields, params = [], []
        convert = {"season_status_id":season_status_id,
                   "episode": episode,
                   "episode_title": episode_title,
                   "watch_date": watch_date}
        for i, key in convert.items():
            if key is not None:
                fields.append(f"{i} = ?")
                params.append(key)

        return fields, params

# ----------------------------read------------------------------------------
    def lookup_anime(self,title=""):
        select = ("SELECT a.id AS id, "
                  "a.title AS anime_title, "
                  "a.title_jp AS anime_title_jp, "
                  "ss.season_count AS season_count, "
                  "ss.total_eps AS total_eps, "
                  "ss.avg_rate AS avg_rate, "
                  "MIN(e.watch_date) AS first_watch_date, "
                  "MAX(e.watch_date) AS last_watch_date "
                  "FROM anime a "
                  "LEFT JOIN (SELECT anime_id, COUNT(*) AS season_count, SUM(total_episodes) AS total_eps, ROUND(AVG(rate),2) AS avg_rate "
                  "FROM season_status "
                  "GROUP BY anime_id) ss ON ss.anime_id = a.id "
                  "LEFT JOIN season_status s ON a.id = s.anime_id "
                  "LEFT JOIN episode_log e ON s.id = e.season_status_id "
                  "WHERE a.title like ? "
                  "GROUP BY a.id")
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(select,("%" + title + "%", ))
            return fetch_all_as_dict(cur)

    def lookup_season_status(self,anime_id=None,season=None,status=None,season_title =None,total_episodes = None,air_year = None,air_season = None,rate = None):
        fields, params = self.season_status_arguments(anime_id,season,status,season_title,total_episodes,air_year,air_season,rate)
        select = (f"SELECT a.id AS id, "
                  f"s.id AS season_status_id, "
                  f"a.title AS anime_title, "
                  f"s.season AS season, "
                  f"s.season_title AS season_title, "
                  f"s.total_episodes AS total_episodes, "
                  f"MAX(e.episode) AS cur_episode, "
                  f"s.status AS status, "
                  f"s.air_year AS air_year, "
                  f"s.air_season AS air_season, "
                  f"s.rate AS rate, "
                  f"MIN(e.watch_date) AS first_watch_date, "
                  f"MAX(e.watch_date) AS last_watch_date "
                  f"FROM anime a "
                  f"LEFT JOIN season_status s ON a.id = s.anime_id "
                  f"LEFT JOIN episode_log e ON s.id = e.season_status_id ")
        if fields:
            select += " WHERE " + " AND ".join(fields)
        select += " GROUP BY a.id, a.title, s.season"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(select, params)
            return fetch_all_as_dict(cur)

    def lookup_episode_log(self,season_status_id=None,episode= None,episode_title = None,watch_date = None):
        fields, params = self.episode_log_arguments(season_status_id,episode,episode_title,watch_date)
        select = ("SELECT "
                  "e.id AS episode_id, "
                  "e.episode AS episode, "
                  "e.episode_title AS episode_title, "
                  "e.watch_date AS watch_date "
                  "FROM anime a "
                  "LEFT JOIN season_status s ON a.id = s.anime_id "
                  "LEFT JOIN episode_log e ON s.id = e.season_status_id ")

        if fields:
            for i in range(len(fields)):
                fields[i] = "e." + fields[i]
                select += " WHERE " + " AND ".join(fields)
            select += " ORDER BY a.id, s.season, e.episode ASC"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(select,params)
            return fetch_all_as_dict(cur)

    def lookup_first_and_last_watch_date(self,anime_id,season):
        select = ("SELECT MIN(e.watch_date), MAX(e.watch_date) "
                  "FROM season_status s "
                  "Left JOIN episode_log e "
                  "ON s.id = e.season_status_id "
                  "WHERE anime_id = ? AND season = ? "
                  "GROUP BY s.id")
        with self.get_connection() as conn:
            cur = conn.cursor()
            res = cur.execute(select, (anime_id,season)).fetchone()
        return res if res else None

    def lookup_anime_resolve(self,title,season=None,episode=None):
        select = ("SELECT a.id AS anime_id, "
                  "a.title AS anime_title, "
                  "a.title_jp AS anime_title_jp, "
                  "s.id AS season_id, "
                  "s.season_title AS season_title, "
                  "e.id AS episode_id, "
                  "e.episode AS episode "
                  "FROM anime a "
                  "LEFT JOIN season_status s ON a.id = s.anime_id "
                  "LEFT JOIN episode_log e ON s.id = e.season_status_id "
                  "WHERE a.title = ?")

        field, param = [],[title]
        if season:
            field.append("s.season = ?")
            param.append(season)
        if episode:
            field.append("e.episode = ?")
            param.append(episode)
        if field:
            select += " AND " + " AND ".join(field)
        select += " GROUP BY a.id"
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(select, param)
            res = fetch_all_as_dict(cur)
            return res if res else None

    def lookup_season_resolve(self,season_id):
        select = ("SELECT "
                  "season, "
                  "status, "
                  "season_title, "
                  "air_year, "
                  "air_season, "
                  "rate, "
                  "total_episodes "
                  "FROM season_status WHERE id = ?")

        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(select, (season_id,))
            res = fetch_all_as_dict(cur)
            return res if res else None

    def lookup_episode_resolve(self,episode_id):
        select = ("SELECT episode, episode_title, watch_date "
                  "FROM episode_log "
                  "WHERE id = ?")

        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute(select, (episode_id,))
            res = fetch_all_as_dict(cur)
            return res if res else None

#----------------------------others-----------------------------------------
    def count_status(self,status):
        select = "SELECT COUNT(*) FROM season_status WHERE status = ?"
        with self.get_connection() as conn:
            cur = conn.cursor()
            res = cur.execute(select, (status,)).fetchone()
        return res[0]

    def count_watched_episode(self,anime_id = None,season_status_id = None):
        select = ("SELECT "
                  "COUNT(*) AS watched_episodes "
                  "FROM episode_log e "
                  "JOIN season_status s ON s.id = e.season_status_id ")
        field, params = [], []
        if anime_id:
            field.append("anime_id = ?")
            params.append(anime_id)
        if season_status_id:
            field.append("season_status_id = ?")
            params.append(season_status_id)
        if field:
            select += " WHERE " + " AND ".join(field)
        with self.get_connection() as conn:
            cur = conn.cursor()
            res =cur.execute(select,params).fetchall()
            return sum(i[0] for i in res)

    def count_total_episodes(self,anime_id,season_status_id = None):
        select = "SELECT total_episodes FROM season_status WHERE anime_id = ?"
        params = [anime_id]
        if season_status_id:
            select += " AND id = ?"
            params.append(season_status_id)
        with self.get_connection() as conn:
            cur = conn.cursor()
            count = cur.execute(select, params).fetchall()
        return sum(i[0] for i in count)

    def update_status(self,season_status_id):
        select = ("SELECT total_episodes, status FROM season_status "
                  "WHERE id = ?")
        with self.get_connection() as conn:
            cur = conn.cursor()
            total_episodes,cur_status = cur.execute(select,(season_status_id, )).fetchone()
            status= "watching"
            if not total_episodes:
                total_episodes = 0
            if total_episodes is not None and self.count_watched_episode(season_status_id=season_status_id) >= total_episodes :
                status = "finished"
            if cur_status != status:
                self.season_status_update(season_status_id,status=status)
                return True
            return False

#----------------------------functions-----------------------------------------
def fetch_all_as_dict(cur):
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]

#----------------------------testing-----------------------------------------
# db = AnimeDB()
# print(db.lookup_anime("我內心"))
# x = db.lookup_episode_log(season_status_id = 20)
# for i in x:
#     print(i)

# print(db.season_status_update(23,None,1,"watching","run",1,2025,"fall",5))



