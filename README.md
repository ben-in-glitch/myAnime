## MyAnime – Anime Watch Tracker

[English](README.md) | [繁體中文](README_zh-TW.md)

This is a simple anime watch tracking project with a frontend built in HTML/CSS/JS and a backend using FastAPI + SQLite.

---

### Features

- CRUD for Anime, Season, and Episode
- Search and filter functionality
- Rating and watch status tracking
- Interactive frontend (index.html)

---

### Requirements

- Python 3.10+
- FastAPI
- uvicorn
- SQLite3 is built-in with Python

---

### Project Structure

```text
myAnime/
├─ myanimeAPI.py      ← FastAPI app 
├─ myanime.py         ← SQL functions
├─ README.md
├─ .gitignore
├─ requirements.txt
└─ frontEnd/
   ├─ index.html
   ├─ main.css
   ├─ main.js
   └─ img/ 11 Free stock photos provided
```

### Installation & Running

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

````
#### requirements
-fastapi, uvicorn
```bash
pip install -r requirements.txt

```


#### run
```bash
uvicorn myanimeAPI:app --reload

```

---

### learning Resources/Credits
- [SQLite Tutorial](https://www.sqlitetutorial.net/sqlite-python/) – Used for understanding SQLite in Python
- [彭彭的 YouTube 課程](https://www.youtube.com/@cwpeng-course) – Helped with frontend(HTML, JS, CSS) & backend (FastAPI) integration
- ChatGPT – Assisted in explaining all my questions
- Jerry - Provided me ideas for this project and some coding suggestions
- [unsplash](https://unsplash.com/)-images source


### About This Project (2026-02-05)

This is my second project and also serves as my half-year review since I started learning programming in August 2025.  

lots of the skills and knowledge I used were learned **just-in-time**, as I needed them for the project. 

There may still be some bugs, but it's currently workable based on my tests. I might optimize and improve the project over time in the future.  

**My learning journey:**  
- SQLite: 2026-01-05  
- FastAPI: 2026-01-08  
- HTML: 2026-01-15  
- JavaScript: 2026-01-16  
- CSS: 2026-01-29


**known issues**
- watchlist does not refresh after CRUD(current resolve -> F5)


**await optimise(for myself)**
- optimise seasons/episodes layout/CRUD options
- blur search/ status search/ season layout api separate and optimize
