import streamlit as st
import requests
import pandas as pd

RAPID_API_KEY = "a31eb0d242mshdafc06af0f001fcp1d8716jsn1466a0d8542b"
HEADERS = {
    "x-rapidapi-key": RAPID_API_KEY,
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

# ✅ Search player by name
def search_player(name):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/search?plrN={name}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json().get("player", [])
    return []

# ✅ Player profile
def fetch_player_details(player_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()
    return {}

# ✅ Batting stats
def fetch_player_batting_details(player_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/batting"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()
    return {}

# ✅ Bowling stats
def fetch_player_bowling_details(player_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/stats/v1/player/{player_id}/bowling"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()
    return {}

# ✅ Convert Cricbuzz stats JSON into dict {Format: {Stat: Value}}
def stats_json_to_dict(data):
    headers = data.get("headers", [])[1:]  # skip ROWHEADER
    values = data.get("values", [])
    stats_by_format = {fmt: {} for fmt in headers}

    for row in values:
        row_vals = row.get("values", [])
        if row_vals:
            stat_name = row_vals[0]
            for i, fmt in enumerate(headers):
                stats_by_format[fmt][stat_name] = row_vals[i + 1]

    return stats_by_format


def render():
    st.title("⭐ Player Stats Explorer")

    player_name = st.text_input("🔍 Enter Player Name")

    st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #4a66d5;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                height: 40px;
                width: 160px;
            }
            div.stButton > button:first-child:hover {
                background-color: #3b53b0;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)


    # 🔎 Search button
    if st.button("🔎 Search Player") and player_name:
        players = search_player(player_name)
        if not players:
            st.warning("⚠️ No players found.")
        else:
            st.session_state.players = players

    # ✅ If players exist in session
    if "players" in st.session_state and st.session_state.players:
        player_dict = {f"{p['name']} ({p.get('teamName','')})": p["id"] for p in st.session_state.players}
        selected_player = st.selectbox("Select Player", list(player_dict.keys()))
        player_id = player_dict[selected_player]

        # Fetch details
        details = fetch_player_details(player_id)
        if details:
            st.subheader(f"📌 {details.get('name','')}")

            # Tabs
            tab1, tab2, tab3 = st.tabs(["ℹ️ Player Info", "🏏 Batting Stats", "🎯 Bowling Stats"])

            # ---- Player Info ----
            with tab1:
                st.markdown(f"**Role:** {details.get('role','')}")
                st.markdown(f"**Batting Style:** {details.get('bat','')}")
                st.markdown(f"**Bowling Style:** {details.get('bowl','')}")
                st.markdown(f"**DOB:** {details.get('DoB','')}")
                st.markdown(f"**Bio:** {details.get('bio','')[:2200]}...")

            # ---- Batting Stats ----
            with tab2:
                batting = fetch_player_batting_details(player_id)
                if batting:
                    stats = stats_json_to_dict(batting)

                    desired_order = ["ODI", "T20", "Test", "IPL"]
                    formats = [fmt for fmt in desired_order if fmt in stats]
                    if formats:
                        sub_tabs = st.tabs(formats)
                        for i, fmt in enumerate(formats):
                            with sub_tabs[i]:
                                stat_dict = stats[fmt]
                                col1, col2, col3 = st.columns(3)
                                col1.metric("Matches", stat_dict.get("Matches", "-"))
                                col2.metric("Innings", stat_dict.get("Innings", "-"))
                                col3.metric("Runs", stat_dict.get("Runs", "-"))
                                col1.metric("Highest", stat_dict.get("Highest", "-"))
                                col2.metric("Average", stat_dict.get("Average", "-"))
                                col3.metric("Strike Rate", stat_dict.get("SR", "-"))
                                col1.metric("50s", stat_dict.get("50s", "-"))
                                col2.metric("100s", stat_dict.get("100s", "-"))
                                col3.metric("Ducks", stat_dict.get("Ducks", "-"))
                else:
                    st.info("No batting stats available.")

            # ---- Bowling Stats ----
            with tab3:
                bowling = fetch_player_bowling_details(player_id)
                if bowling:
                    stats = stats_json_to_dict(bowling)

                    desired_order = ["ODI", "T20", "Test", "IPL"]
                    formats = [fmt for fmt in desired_order if fmt in stats]

                    #formats = list(stats.keys())
                    if formats:
                        sub_tabs = st.tabs(formats)
                        for i, fmt in enumerate(formats):
                            with sub_tabs[i]:
                                stat_dict = stats[fmt]
                                col1, col2, col3 = st.columns(3)
                                col1.metric("Matches", stat_dict.get("Matches", "-"))
                                col2.metric("Innings", stat_dict.get("Innings", "-"))
                                col3.metric("Wickets", stat_dict.get("Wickets", "-"))
                                col1.metric("Average", stat_dict.get("Avg", "-"))
                                col2.metric("Economy", stat_dict.get("Eco", "-"))
                                col3.metric("Strike Rate", stat_dict.get("SR", "-"))
                                col1.metric("Best Bowling", stat_dict.get("BBI", "-"))
                                col2.metric("5W", stat_dict.get("5w", "-"))
                                col3.metric("10W", stat_dict.get("10w", "-"))
                else:
                    st.info("No bowling stats available.")