//2026-01-16

console.log("main.js loaded", Date.now())

const state = {
    cur_anime_id:null,
    cur_anime_title:null,
    cur_anime_title_jp:null,
    cur_season_id:null,
    cur_finished_season:null,
    today:new Date().toISOString().slice(0, 10),
    isUpdating:false
}

const translate = {
    "spring":"春",
    "summer":"夏",
    "fall":"秋",
    "winter":"冬",
    "plan":"待看中",
    "next":"馬上看",
    "watching":"觀看中",
    "finished":"看完了",
    "quit":"棄追",
    "":"",
    null:""
}

function set_cur_anime_id(id){state.cur_anime_id = id}
function set_cur_anime_title(title){state.cur_anime_title = title}
function set_cur_anime_title_jp(title_jp){state.cur_anime_title_jp = title_jp}
function set_cur_season_id(id){state.cur_season_id = id}
function set_cur_finished_season(n){state.cur_finished_season = n}

// -------others----------------------------------------------------------------

// async function init_db(){
//     const res = await fetch("/init",{method:"POST"});
//     const data = await res.json();
//     return data['init']
// }

async function watch_list(status){
    let url = `/lookup/season_status?status=${status}`;
    let res = await fetch(url).then(response =>(response.json()));
    const container = document.querySelector("#"+status);
    if (!res){return}
    container.innerHTML = res.map(renderListRow).join("");
    }

async function update_watch_list(){
    if(state.isUpdating){return;}

    state.isUpdating = true;

    await Promise.all([
        watch_list("plan"),
        watch_list("next"),
        watch_list("watching")
    ]);

        state.isUpdating = false;
}

async function achievement(){
    const container = document.querySelector("#achievement");
    let n = Math.max(0, Number(state.cur_finished_season) || 0);
    const title =["陌生人","動畫小手","動畫好手","動畫高手","入門宅宅","高級宅宅","走火入魔","尊榮宅宅","至尊宅宅","禁咒宅宅","你宅斃了"];
    const superior = ["轉生者"];
    let step = 10;
    let supreme = 500
    const rank = Math.floor(n / step);
    let user;
    if (rank < title.length){user = title.at(rank);}
    else if (n < supreme){user=title.at(-1);}
    else{user=superior.at(0);}

    container.textContent = user
}

async function count_watched(){
    const finished = await fetch("/count/status?status=finished")
    const season = await finished.json()
    const episodes = await fetch("/count/watched_episodes").then(res=>res.json())
    document.querySelector("#watched_season").innerHTML= season['finished']
    document.querySelector("#watched_episode").innerHTML = episodes['watched_episodes']
    set_cur_finished_season(season['finished'])
    }

function random_img(){
    const imgs=[];
    for (let i=1; i<12;i++){
        imgs.push(`img/img${i}.jpg`);
    }
    const shuffled = imgs.sort(()=> Math.random() -0.5);
    document.querySelector("#img1").src = shuffled[0]
}

function onclick_img1(){
    console.log("宅弊了")
    random_img()
}

// -------CRUD----------------------------------------------------------------

async function append_anime(){
    let title = document.querySelector("#anime_title").value;
    let title_jp = document.querySelector("#anime_title_jp").value;
    if (!title){
    alert("title cannot be blank")
    return
    }
    let response = await fetch("/anime", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title,title_jp })
    });

    let res = await response.json();
    console.log(res)
    document.querySelector("#anime_title").value=""
    document.querySelector("#anime_title_jp").value=""
    await handleSearch(title);
    }

async function update_anime(){
    document.querySelector("#update_title").value = state.cur_anime_title;
    document.querySelector("#update_title_jp").value = state.cur_anime_title_jp;
    const res = await open_dialog("#update_anime");
    if (res){
        const anime_id = state.cur_anime_id
        const title = document.querySelector("#update_title").value;
        const title_jp = document.querySelector("#update_title_jp").value
        const response = await fetch(`/anime/${state.cur_anime_id}`,{
                                      method:"PATCH",
                                      headers: { "Content-Type": "application/json" },
                                      body:JSON.stringify({anime_id,title,title_jp})
                                      })
        const res = await response.json();
        await handleSearch(title);
        console.log(res)
        await update_watch_list();
    }
}

async function delete_anime(){
    const res = await open_dialog("#confirm")
    if(res){
    const response = await fetch(`/anime/${state.cur_anime_id}`,{
      method:"DELETE"
    })
    const data = await response.json();
    console.log(data);
    await window.location.reload();
    }}

async function append_season() {
    const row = document.querySelector("#append_season")
    row.querySelector(".show_anime").textContent = state.cur_anime_title
    const res = await open_dialog("#append_season")
    if (res){
        const data={
        "anime_id":state.cur_anime_id,
        "season":document.querySelector("#season").value,
        "status":document.querySelector("#status").value,
        "season_title":document.querySelector("#season_title").value,
        "total_episodes":document.querySelector("#total_episodes").value,
        "air_year":document.querySelector("#air_year").value,
        "air_season":document.querySelector("#air_season").value,
        "rate":document.querySelector("#rate").value
        }
        console.log(data)
        if (!data.season){alert("season cannot be empty"); return;}

        const response = await fetch(`/anime/${state.cur_anime_id}/seasons`,{
          method:"POST",
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify(data)
        })
        const return_data = await response.json();
        if (response.ok){
            if(!return_data["res"]){alert(return_data["status"]);}
            await get_seasons(state.cur_anime_id);
            await update_watch_list();
        }
        else if (!response.ok){
            console.error(return_data.detail)
        }
    }
    document.querySelector("#append_season form").reset();
}

async function update_season(season_id){
    const row = document.querySelector("#update_seasons")
    row.querySelector(".show_anime").textContent = state.cur_anime_title
    const response = await fetch("/season/resolve?season_id="+season_id).then(response=>(response.json()));
    for (let key in response[0]){
        document.querySelector("#update_"+key).value = response[0][key]
    }
    const res = await open_dialog("#update_seasons")

    const data ={"season_status_id":season_id}
    for (let key in response[0]){
        data[key] = document.querySelector("#update_"+key).value
    }

    if(res){await fetch(`seasons/${season_id}`,{
                                        method:"PATCH",
                                        headers:{"Content-Type": "application/json"},
                                        body:JSON.stringify(data)
        });
        await get_seasons(state.cur_anime_id);
        await update_watch_list();
    }
}

async function delete_season(season_id){
    const res = await open_dialog("#confirm")
    if(res){const response = await fetch(`/seasons/${season_id}`, {method:"DELETE"});
          const data = await response.json();
          console.log(data);
          await update_watch_list()
          await get_seasons(state.cur_anime_id);
    }
}

async function append_episode(season_id,season){
    document.querySelector("#watch_date").value= state.today;
    const row = document.querySelector("#append_episode")
    row.querySelector(".show_anime").textContent = state.cur_anime_title
    row.querySelector(".show_season").textContent = season
    const res = await open_dialog("#append_episode")
    if(res){
        const data = {
          "season_status_id":season_id,
          "episode":document.querySelector("#episode").value,
          "title":document.querySelector("#title").value,
          "watch_date":document.querySelector("#watch_date").value
        }
        if(!data["episode"]){alert("episode cannot be blank"); return}

        const response = await fetch(`/seasons/${season_id}/episodes`,{
          method:"POST",
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify(data)
        })
        const return_data = await response.json()
        if (response.ok){
            if (!return_data['res']){alert(return_data['status']);}
            await get_seasons(state.cur_anime_id);
            await get_episodes(season_id);
            await update_watch_list();
        }
    }
    document.querySelector("#append_episode form").reset()
}

async function finish_all_episode(season_id){
    const confirm = await open_dialog("#finish_all_episodes")
    if (confirm){const response = await fetch("/season/resolve?season_id="+season_id).then(response=>(response.json()))
        const total_episode = response[0]['total_episodes']
        const watch_date = document.querySelector("#all_watch_date").value
        for (let i=1; i<=total_episode;i++){
          await fetch(`/seasons/${season_id}/episodes`,{
                method:"POST",
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({"season_status_id":season_id,
                                      "episode":i,
                                      "title":null,
                                      "watch_date":watch_date})
              }).then(res=>(res.json()))
          }
        document.querySelector("#all_watch_date").value= ""
        await get_seasons(state.cur_anime_id);
        await get_episodes(season_id);
    }
    }

async function update_episode(episode_id,season){
    const response = await fetch("/episode/resolve?episode_id="+episode_id).then(response=>(response.json()))
    for (let key in response[0]){
    document.querySelector("#update_"+key).value = response[0][key]
    }
    const row = document.querySelector("#update_episodes")
    row.querySelector(".show_anime").textContent = state.cur_anime_title
    row.querySelector(".show_season").textContent = season
    const res = await open_dialog("#update_episodes")

    if (res){
        let data={"episode_id":episode_id}
        for (let key in response[0]){
          data[key]=document.querySelector("#update_"+key).value
        }

        const response_sql = await fetch(`/episodes/${episode_id}`,{
                                method:"PATCH",
                                headers:{"Content-Type": "application/json"},
                                body:JSON.stringify(data)
        })
        if(response_sql.ok){
            await get_seasons(state.cur_anime_id);
            await get_episodes(state.cur_season_id);
            await update_watch_list();
        }
    }
}

async function delete_episode(episode_id){
    const res = await open_dialog("#confirm")
    if(res){const response = await fetch(`/episodes/${episode_id}`,{method:"DELETE"});
          const data = await response.json();
          console.log(data);
          await get_seasons(state.cur_anime_id);
          await get_episodes(state.cur_season_id);
          await update_watch_list();
    }
    }

// -------search/dialog----------------------------------------------------------------

function open_dialog(tag_id){
    const confirm = document.querySelector(tag_id);
    confirm.showModal();
    return new Promise((resolve)=>{
    confirm.addEventListener("close",()=> {resolve(confirm.returnValue === "true");},
            {once: true});
    })
    }

async function blur_search(){
    let container = document.querySelector("#blur_search_container");
    let title = document.querySelector("#blur_title").value;
    let url = "/lookup/anime";
    if (title){url += "?title="+title;}
    let res = await fetch(url).then(response => (response.json()));
    document.querySelector("#blur_thead").style.display=""
    container.innerHTML = res.map(renderBlurRow).join("");
    }

function blur_clean(){
    document.querySelector("#blur_thead").style.display= "none"
    document.querySelector("#blur_search_container").innerHTML="";
    }

async function status_search(){
    const data = {
    "status":document.querySelector("#input_status").value,
    "get_season":document.querySelector("#input_season").value,
    "total_episodes":document.querySelector("#input_total_episodes").value,
    "air_year":document.querySelector("#input_air_year").value,
    "air_season":document.querySelector("#input_air_season").value,
    "rate":document.querySelector("#input_rate").value,
    };
    const params = new URLSearchParams();
    for (let key in data){
        if(data[key] !== "" && data[key]!== null && data[key]!==undefined){
          params.append(key,data[key])
        }
        if(key==="get_season"){key="season"}
        document.querySelector("#input_"+key).value = "";
    }
    const url = "lookup/season_status?" + params.toString();
    const response = await fetch(url);
    let res = await response.json();
    document.querySelector("#status_thead").style.display=""
    if(!res){res=[]}
    const container = document.querySelector("#status_search_container");
    container.innerHTML = res.map(renderStatusRow).join("");
    }

function open_search(tag_id){
    const blur = document.querySelector("#blur_search");
    const status = document.querySelector("#status_search");
    if(tag_id==="click_blur_search"){
        if(blur.style.display !== "block"){
            blur.style.display = "block";
            status.style.display= "none";
        }
    }
    else{
        if(status.style.display !== "block"){
            blur.style.display = "none";
            status.style.display= "block";
        }
    }
    }

function status_clean(){
    document.querySelector("#status_thead").style.display= "none"
    document.querySelector("#status_search_container").innerHTML =""
    }

async function handleSearch(keyword){
    const anime_id = await resolve_search(keyword);
    if(!anime_id){alert("failed to find anime"); return}
    await get_seasons(anime_id);
    }

async function resolve_search(title){
    if (!title){
    alert("title必填");
    return;
    }
    const params = new URLSearchParams();
    params.append("title",title);
    const url = "/anime/resolve?" + params.toString()
    const res = await fetch(url).then(function(response){return response.json()});
    if (!res){return false}
    set_cur_anime_id(res[0]["anime_id"])
    set_cur_anime_title(res[0]["anime_title"])
    set_cur_anime_title_jp(res[0]["anime_title_jp"])
    return res[0]["anime_id"]
    }

// -------get----------------------------------------------------------------
async function get_seasons(anime_id){
    let res = await fetch(`/anime/${anime_id}`).then(response =>(response.json()));
    let title = document.querySelector("#anime_info");
    document.querySelector("#season_head").style.display=""
    title.innerHTML = `(ID: ${state.cur_anime_id})${state.cur_anime_title}|${state.cur_anime_title_jp}
                      <button id="updateAnime">修改動畫</button>
                      <button id="deleteAnime">刪除動畫</button>
                     `;

    if (!res){res=[]}
    let output = document.querySelector("#season_info");
    output.innerHTML = res.map(renderSeasonRow).join("");

    document.getElementById("updateAnime").addEventListener("click",()=>(update_anime()))
    document.getElementById("deleteAnime").addEventListener("click", ()=>(delete_anime()))
    document.getElementById("achievement").scrollIntoView({behavior:"smooth"})
    }

async function get_episodes(season_id){
    set_cur_season_id(season_id)
    let output = document.querySelector("#episode_"+season_id);
    let container = output.querySelector(".episode_container");
    if (output.style.display === "none"){
    output.style.display = ""
    if (!container.innerHTML){
      const res =await fetch(`/seasons/${season_id}/episodes`);
      const data = await res.json();
      if(!data){return}
      container.innerHTML += data.map(renderEpisodeRow).join("");
    }
    }
    else {output.style.display = "none"}
    }

function getElement(tag_id){
    let el = document.querySelector(tag_id)
    if (!el){return;}
    if (el.dataset?.value){return el.dataset.value;}
    if(el.value){
    return el.value.trim()
    }
    return el.textContent.trim()
    }

// -------render----------------------------------------------------------------

function renderListRow(data){
    return `<ul class="handle_search hidden_button" data-id="${data['anime_title']}">
          <span>${data['anime_title']}</span>
          ${data['season']? "-S"+data['season'] : ""}
          ${data['cur_episode']? "-EP"+data['cur_episode']:""}
          </ul>`
    }

function renderSeasonRow(data){
    return `<tr class="get_episodes hidden_button" data-id="${data['season_status_id']}">
            <td>
              <button class="delete_season" data-id="${data['season_status_id']}">X</button>
              <button class="update_season" data-id="${data['season_status_id']}">修改</button>
            </td>
            <td>${data['season']}</td>
            <td class="title">${data['season_title']}</td>
            <td>${data['cur_episode']}/${data['total_episodes']}</td>
            <td>${translate[data['status']]}</td>
            <td>${data['air_year']}|${translate[data['air_season']]}</td>
            <td>${data['rate']}</td>
            <td>${data['first_watch_date']}</td>
            <td>${data['last_watch_date']}</td>
      </tr>
      <tr class="inner_card">
        <td colspan="10">
          <table id="episode_${data['season_status_id']}" class="episode_row" style="display:none">
            <thead>
              <tr>
                <td>
                    <button class="append_episode" data-id="${data['season_status_id']}" data-value="${data['season']}">新增</button>
                    <button class="finish_all_episode" data-id="${data['season_status_id']}">看完</button>
                </td>
                <td>集數</td>
                <td>名稱</td>
                <td>觀看日期</td>
              </tr>
            </thead>
            <tbody class="episode_container"></tbody>
          </table>
        </td>
      </tr>
      `;
    }

function renderEpisodeRow(data){
    return `<tr>
          <td>
            <button class="delete_episode" data-id="${data['episode_id']}">X</button>
            <button class="update_episode" data-id="${data['episode_id']}" data-value="${data['season']}">修改</button>
          </td>
          <td>${data['episode']}</td>
          <td class="title">${data['episode_title']}</td>
          <td>${data['watch_date']}</td>
          </tr>`
    }

function renderBlurRow(data){
    return `<tr class="handleSearch hidden_button" data-id="${data['anime_title']}">
          <td class="title">${data['anime_title']}</td>
          <td class="title">${data['anime_title_jp']}</td>
          <td>${data['season_count']}</td>
          <td>${data['total_eps']}</td>
          <td>${data['avg_rate']}</td>
          <td>${data['first_watch_date']}</td>
          <td>${data['last_watch_date']}</td>
          </tr>`
    }

function renderStatusRow(data) {
    return `<tr class="handleSearch  hidden_button" data-id="${data['anime_title']}">
            <td class="title">${data['anime_title']}</td>
            <td>${data['season']}</td>
            <td class="title">${data['season_title']}</td>
            <td>${translate[data['status']]}</td>
            <td>${data['air_year']}</td>
            <td>${translate[data['air_season']]}</td>
            <td>${data['cur_episode']}</td>
            <td>${data['total_episodes']}</td>
            <td>${data['rate']}</td>
          </tr>
              `
    }

async function init(){
    await update_watch_list();
    await count_watched();
    await achievement();
    await random_img()

    }

init().then(()=>{console.log("init finished")})


// --------buttons-----------------------------------------------------------
document.addEventListener("DOMContentLoaded",()=>{
    document.querySelector("#append_anime_confirm").addEventListener("click",append_anime)
});

document.addEventListener("DOMContentLoaded",()=>{
    document.getElementById("addSeason").addEventListener("click", ()=>(append_season()))})

document.addEventListener("DOMContentLoaded",()=>{
    document.querySelector("#img1").addEventListener("click",onclick_img1)})

// --------watch_list-----------------------------------------------------------
document.addEventListener("DOMContentLoaded",()=>{
    const list_container = document.querySelector("#watch_list");
    list_container.addEventListener("click",async(e)=>{
        if (e.target.closest(".handle_search")){
            const row = e.target.closest(".handle_search")
            await handleSearch(row.dataset.id)}
    })
});
// --------season_info-----------------------------------------------------------
document.addEventListener("DOMContentLoaded",()=>{
    document.querySelector(
        "#resolve_search_confirm").addEventListener("click",async()=>{await
            handleSearch(getElement('#resolve_title'))})
});

document.addEventListener("DOMContentLoaded",()=>{
    const container = document.querySelector("#season_info");
    container.addEventListener("click",async(e)=>{
        const id = e.target.dataset.id
        if(e.target.matches(".delete_season")){
            await delete_season(id);
        }
        else if (e.target.matches(".update_season")){
            await update_season(id);
        }
        else if (e.target.closest(".get_episodes")){
            const row = e.target.closest(".get_episodes")
            await get_episodes(row.dataset.id);
        }
        else if(e.target.matches(".append_episode")){
            const season = e.target.dataset.value
            await append_episode(id,season);
        }
        else if(e.target.matches(".finish_all_episode")){
            await finish_all_episode(id);
        }
        else if(e.target.matches(".delete_episode")){
            await delete_episode(id);
        }
        else if(e.target.matches(".update_episode")){
            const season = e.target.dataset.value
            await update_episode(id,season);
        }
    })
});
// --------blur_search-----------------------------------------------------------

document.addEventListener("DOMContentLoaded",()=>{
    document.querySelector("#click_blur_search").addEventListener(
        "click",()=>{open_search("click_blur_search")})
});

document.addEventListener("DOMContentLoaded",()=> {
    const container = document.querySelector("#blur_search");
    container.addEventListener("click",async(e)=>{
        if (e.target.closest(".handleSearch")){
            const row = e.target.closest(".handleSearch")
            await handleSearch(row.dataset.id)
        }
        if (e.target.closest(".blur_search")){
            await blur_search()
        }
        if (e.target.closest(".blur_clean")){
            await blur_clean()
        }
    })
})

// --------status_search-----------------------------------------------------------
document.addEventListener("DOMContentLoaded",()=>{
    document.querySelector("#click_status_search").addEventListener(
        "click",()=>{open_search("click_status_search")})
});

document.addEventListener("DOMContentLoaded",()=> {
    const container = document.querySelector("#status_search");
    container.addEventListener("click",async(e)=>{
        if (e.target.closest(".handleSearch")){
            const row = e.target.closest(".handleSearch")
            await handleSearch(row.dataset.id);
        }
        if (e.target.closest(".status_search")){
            await status_search()
        }
        if (e.target.closest(".status_clean")){
            await status_clean()
        }
    })
})


