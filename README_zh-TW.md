## MyAnime – 動畫觀看紀錄系統 (Anime Watch Tracker)

這是一個簡單的動畫觀看紀錄專案，前端使用 HTML/CSS/JS，後端使用 FastAPI + SQLite。  
This is a simple anime watch tracking project with a frontend built in HTML/CSS/JS and a backend using FastAPI + SQLite.

---

### 功能 (Features)

- 動畫、Season、Episode 的 CRUD  
  CRUD for Anime, Season, and Episode
- 搜尋與基本篩選功能  
  Search and filter functionality
- 評分與觀看狀態管理  
  Rating and watch status tracking
- 前端互動頁面（index.html）  
  Interactive frontend (index.html)

---

### 環境需求 (Requirements)

- Python 3.10+
- FastAPI
- uvicorn
- SQLite3（Python 內建）  
  SQLite3 is built-in with Python

---

### 專案結構 (Project Structure)

```text
myAnime/
├─ myanimeAPI.py      ← FastAPI app 主程式
├─ myanime.py         ← 資料庫操作與邏輯(SQL functions)
├─ README.md
├─ .gitignore
├─ requirements.txt
└─ frontEnd/
   ├─ index.html
   ├─ main.css
   ├─ main.js
   └─ img/ (找自己喜歡的圖片放進資料夾(請自己創建) 並按照格式命名: img1.jpg(目前可放1-11)
```

### 安裝與啟動(Installation & Running)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

````
#### 安裝套件(requirements.txt)
-fastapi, uvicorn
```bash
pip install -r requirements.txt

```


#### 執行(run)
```bash
uvicorn myanimeAPI:app --reload

```

---

### 專案學習資源(learning Resources/Credits)
- [SQLite Tutorial](https://www.sqlitetutorial.net/sqlite-python/) – Used for understanding SQLite in Python
- [彭彭的 YouTube 課程](https://www.youtube.com/@cwpeng-course) – Helped with frontend(HTML, JS, CSS) & backend (FastAPI) integration
- ChatGPT – Assisted in explaining all my questions
- Jerry - Provided me ideas for this project and some coding suggestions


### About This Project (2026-02-05)

This is my second project and also serves as my half-year review since I started learning programming in August 2025.  

ost of the skills and knowledge I used were learned **just-in-time**, as I needed them for the project. 

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
- img/ img related functions optimise or provide some images first