from myanime import AnimeDB
from fastapi import FastAPI, Query,Body,HTTPException
from datetime import date, datetime
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated,Literal
from fastapi.staticfiles import StaticFiles

#2026-01-08

db = AnimeDB()
db.init_db()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

StatusType = Literal["plan","next","watching","finished","quit"]
# --------------------------------------index/set-up-----------------------------------------------
# @app.get("/")
# def index():
#     return FileResponse("frontEnd/index.frontEnd")

@app.post("/init")
def init():
    initialized = db.init_db()
    status = "database created and initialized" if initialized else "database already exists"
    return {"init":initialized,
            "status":status}

@app.delete("/delete_db")
def delete_db():
    return db.remove_db()

# --------------------------------------anime----------------------------------------------------
@app.get("/anime")
def anime():
    return db.lookup_anime()

@app.post("/anime")
def anime(body=Body(None)):
    title = str(body["title"])
    title_jp = str(body["title_jp"]) if body["title_jp"] else None
    validate_input(title=title, title_jp=title_jp)

    add, anime_id = db.anime_get_or_create(title,title_jp)
    status = "anime created successfully" if add else f"{title} is already in your list"
    return {"status": status,
            "title": title,
            "title_jp": title_jp,
            "id":anime_id}


@app.patch("/anime/{anime_id}")
def anime(body=Body(None)):
    anime_id=body["anime_id"]
    title = str(body["title"])
    title_jp = body["title_jp"]
    validate_input(title=title, title_jp=title_jp)
    if db.anime_update(anime_id,title,title_jp):
        return {"status": "anime updated successfully"}

    return {"status": "failed to update anime"}

@app.delete("/anime/{anime_id}")
def anime(anime_id:int):
    delete, anime_title = db.anime_delete(anime_id)
    status = f"{anime_title} was deleted successfully" if delete else "failed to delete anime"
    return {"status": status,
            "id":anime_id}
# --------------------------------------season_status----------------------------------------------------
@app.get("/anime/{anime_id:int}")
def season_status(anime_id:int):
    return db.lookup_season_status(anime_id=anime_id)

@app.post("/anime/{anime_id}/seasons")
def season_status(body = Body(None)):
    anime_id: int =body["anime_id"]
    post_season :str = str(body["season"])
    status: str = body["status"] if body["status"] else "plan"
    season_title: str = body["season_title"]
    total_episodes: int = int(body["total_episodes"]) if body["total_episodes"] else 12
    air_year: int = body["air_year"]
    air_season: str = body["air_season"]
    rate: int = int(body["rate"]) if body["rate"] else -1
    validate_input(get_season=post_season,status=status,season_title=season_title,total_episodes=total_episodes,air_year=air_year,air_season=air_season,rate=rate)

    add, season_status_id = db.season_status_get_or_create(anime_id,post_season,status,season_title,total_episodes,air_year,air_season,rate)
    status = "new season created successfully" if add else "failed to created new season"
    return {"res":add,
            "status": status}

@app.patch("/seasons/{season_status_id}")
def season_status(body=Body(None)):
    season_status_id = body["season_status_id"]
    update_season= str(body["season"])
    status = body["status"] if body["status"] else None
    season_title = body["season_title"]
    total_episodes = int(body["total_episodes"]) if body["total_episodes"] else 12
    air_year = body["air_year"]
    air_season = body["air_season"]
    rate = int(body["rate"]) if body["rate"] else -1

    validate_input(get_season=update_season,status=status,season_title=season_title,total_episodes=total_episodes,air_year=air_year,air_season=air_season,rate=rate)

    if db.season_status_update(
            pk=season_status_id,
            season=update_season,
            status=status,
            season_title=season_title,
            total_episodes=total_episodes,
            air_year=air_year,
            air_season=air_season,
            rate=rate
):
        return {"status": "season status updated successfully"}
    return {"status": "failed to update season status"}

@app.delete("/seasons/{season_status_id}")
def season_status(season_status_id:int):
    delete, anime_info = db.season_status_delete(season_status_id)
    title, delete_season = anime_info if anime_info else (None,None)
    status = "season status deleted successfully" if delete else "failed to delete season status"
    return {"status": status,
            "season_status_id": season_status_id,
            "anime": title,
            "season": delete_season}
# --------------------------------------episode_log----------------------------------------------------
@app.get("/seasons/{season_status_id}/episodes")
def episode_log(season_status_id:int):
    return db.lookup_episode_log(season_status_id)

@app.post("/seasons/{seasons_status_id}/episodes")
def episode_log(body = Body(None)):
    season_status_id = body["season_status_id"]
    post_episode = int(body["episode"])
    title = body["title"] if body["title"] else str(post_episode)
    watch_date = body["watch_date"] if body["watch_date"] else date.today().isoformat()

    validate_input(episodes=post_episode,episode_title=title,watch_date=watch_date)

    add,episode_log_id = db.episode_log_get_or_create(season_status_id,post_episode,title,watch_date)
    db.update_status(season_status_id)
    status = "episode log added successfully" if add else "episode already exists"
    return {"res":add,
            "status": status,
            "episode_log_id": episode_log_id,
            "episode" : post_episode,
            "title": title,
            "watch_date": watch_date}


@app.patch("/episodes/{episode_id}")
def episode_log(body=Body(None)):
    episode_id = body["episode_id"]
    update_episode = int(body["episode"])
    episode_title = body["episode_title"]
    watch_date = body["watch_date"] if body["watch_date"] else date.today().isoformat()
    validate_input(episodes=update_episode,episode_title=episode_title,watch_date=watch_date)

    update = db.episode_log_update(pk=episode_id,episode=update_episode,episode_title=episode_title,watch_date=watch_date)
    status = "episode log updated successfully" if update else "failed to update episode log"
    return {
        "res": update,
        "status": status
    }

@app.delete("/episodes/{episode_id}")
def episode_log(episode_id:int):
    delete,episode_info = db.episode_log_delete(episode_id)
    title, delete_season,delete_episode, episode_title = episode_info if episode_info else (None,None,None,None)
    status = "episode log deleted successfully" if delete else "failed to delete episode log"
    return {"status": status,
            "title": title,
            "season": delete_season,
            "episode": delete_episode}
# --------------------------------------look_up----------------------------------------------------
@app.get("/lookup/anime")
def anime(title=""):
    return db.lookup_anime(title)

@app.get("/lookup/season_status")
def season_status(anime_id:int = None,
                  get_season:str = None,
                  status:str = None,
                  season_title:str = None,
                  total_episodes:int = None,
                  air_year:int = None,
                  air_season:str = None,
                  rate:int = None):
    status = status.lower() if status is not None else None
    air_season = air_season.lower() if air_season is not None else None
    return db.lookup_season_status(anime_id,get_season,status,season_title,total_episodes,air_year,air_season,rate)

@app.get("/lookup/episode_log")
def episode_log(season_status_id:int = None, get_episode:int = None,title:str = None, watch_date:str = None):
    return db.lookup_episode_log(season_status_id=season_status_id,episode=get_episode,episode_title=title,watch_date=watch_date)

@app.get("/anime/resolve")
def anime(title:str, get_season:str = None, get_episode:int = None):
    return db.lookup_anime_resolve(title,get_season,get_episode)

@app.get("/season/resolve")
def season(season_id):
    return db.lookup_season_resolve(season_id)

@app.get("/episode/resolve")
def episode(episode_id):
    return db.lookup_episode_resolve(episode_id)

# --------------------------------------others----------------------------------------------------
@app.get("/count/status")
def count(status:Annotated[StatusType,Query(...)]):
    res = db.count_status(status)
    return {status: res}

@app.get("/count/watched_episodes")
def count():
    res = db.count_watched_episode()
    return {"watched_episodes": res}

@app.get("/count/episodes")
def count(anime_id:int, season_status_id:int = None):
    res = db.count_watched_episode(anime_id,season_status_id)
    total = db.count_total_episodes(anime_id,season_status_id)
    return {"anime_id":anime_id,
            "season_status_id": season_status_id,
            "total_episodes": total,
            "watched_episodes": res}


def validate_input(**kwargs):
    if "title" in kwargs:
        if not kwargs["title"] or len(kwargs["title"]) > 50:
            raise HTTPException(status_code=400,detail="Too long title")
    if "title_jp" in kwargs:
        if kwargs["title_jp"] and len(kwargs["title_jp"]) > 50:
            raise HTTPException(status_code=400,detail="Too long title")
    if "season_title" in kwargs:
        if kwargs["season_title"] and len(kwargs["season_title"]) > 50:
            raise HTTPException(status_code=400,detail="Too long title")
    if "episode_title" in kwargs:
        if kwargs["episode_title"] and len(kwargs["episode_title"]) > 50:
            raise HTTPException(status_code=400,detail="Too long title")
    if "get_season" in kwargs:
        if kwargs["get_season"] and len(kwargs["get_season"]) > 50:
            raise HTTPException(status_code=400, detail="Season out of range")
    if "air_year" in kwargs:
        if kwargs["air_year"] not in(None,"") and not (1900<int(kwargs["air_year"])<2999):
            raise HTTPException(status_code=400, detail="Invalid air_year")
    if "air_season" in kwargs:
        if kwargs["air_season"] and kwargs["air_season"] not in ("spring", "summer", "fall", "winter"):
            raise HTTPException(status_code=400, detail="Invalid air_season")
    if "rate" in kwargs:
        if kwargs["rate"] and kwargs["rate"] not in (-1,0,1,2,3,4,5):
            raise HTTPException(status_code=400, detail="Invalid rate")
    if "status" in kwargs:
        if kwargs["status"] and kwargs["status"] not in ("watching","plan","next","finished","quit"):
            raise HTTPException(status_code=400, detail="Invalid status")
    if "total_episodes" in kwargs:
        if kwargs["total_episodes"] and not (0<kwargs["total_episodes"]<1000):
            raise HTTPException(status_code=400, detail="Total episodes out of range")
    if "episodes" in kwargs:
        if kwargs["episodes"] and not (0<kwargs["episodes"]<1000):
            raise HTTPException(status_code=400, detail="Episodes out of range")
    if "watch_date" in kwargs:
        try:
            parsed = datetime.strptime(kwargs["watch_date"], "%Y-%m-%d")
            if not (1900 <= parsed.year <= 2099):
                raise HTTPException
        except:
            raise HTTPException(400, "Invalid date")



#-----------------staticfiles---------------------------------------
app.mount("/", StaticFiles(directory="frontEnd",html=True))