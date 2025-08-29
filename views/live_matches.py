import streamlit as st
import requests
import pandas as pd

RAPID_API_KEY = "a31eb0d242mshdafc06af0f001fcp1d8716jsn1466a0d8542b"
HEADERS = {
    "x-rapidapi-key": RAPID_API_KEY,
    "x-rapidapi-host": "cricbuzz-cricket.p.rapidapi.com"
}

# ✅ Fetch matches (live or recent)
def fetch_matches(endpoint):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/matches/v1/{endpoint}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"⚠️ API Error {resp.status_code}: {resp.text[:200]}")
            return {}
    except Exception as e:
        st.error(f"⚠️ Failed to fetch {endpoint} matches: {e}")
        return {}

# ✅ Fetch Match Info (metadata)
def fetch_match_info(match_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"⚠️ API Error {resp.status_code}: {resp.text[:200]}")
            return {}
    except Exception as e:
        st.error(f"⚠️ Failed to fetch match info: {e}")
        return {}


# ✅ Fetch scorecard
def fetch_scorecard(match_id):
    url = f"https://cricbuzz-cricket.p.rapidapi.com/mcenter/v1/{match_id}/scard"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"⚠️ API Error {resp.status_code}: {resp.text[:200]}")
            return {}
    except Exception as e:
        st.error(f"⚠️ Failed to fetch scorecard: {e}")
        return {}

# ✅ Main UI Renderer
def render():
    st.set_page_config(page_title="Cricbuzz Live", layout="wide")
    st.title("🏟 Live / Recent Matches")

    # Get matches
    data = fetch_matches("live")
    if not data or "typeMatches" not in data or all(len(tm.get("seriesMatches", [])) == 0 for tm in data["typeMatches"]):
        st.warning("⚡ No live matches, showing recent matches instead")
        data = fetch_matches("recent")

    if not data or "typeMatches" not in data:
        st.error("No match data available at the moment.")
        return

    # Dropdown
    matches_dict = {}
    for type_block in data["typeMatches"]:
        for series_block in type_block.get("seriesMatches", []):
            if "seriesAdWrapper" not in series_block:
                continue
            series_info = series_block["seriesAdWrapper"]
            series_name = series_info.get("seriesName", "")
            for match in series_info.get("matches", []):
                info = match.get("matchInfo", {})
                match_id = info.get("matchId")
                desc = f"{series_name} - {info.get('matchDesc','')} ({info.get('matchFormat','')})"
                matches_dict[desc] = match_id

    if not matches_dict:
        st.warning("No matches available to select.")
        return

    st.subheader("🎯 Select a Match")
    selected_match = st.selectbox("Available Matches", list(matches_dict.keys()))
    match_id = matches_dict[selected_match]

    score_data = fetch_scorecard(match_id)
    if not score_data:
        st.error("Could not load scorecard")
        return

    st.header(f"📊 {selected_match}")

    # Tabs
    tab1, tab2 = st.tabs(["📋 Match Summary", "📊 Full Scorecard"])

    # ---- Match Summary ----
    with tab1:
        
        # ✅ Fetch once to avoid multiple API calls
        match_json = fetch_match_info(match_id)
        match_info = match_json.get("matchInfo", {})
        venue_info = match_json.get("venueInfo", {})

        # 🔹 Status Row
        col1, col2, col3 = st.columns(3)
        col1.metric("Format", match_info.get("matchFormat", "N/A"))
        col2.metric("Status", match_info.get("state", "N/A"))
        col3.metric("Year", match_info.get("year", "N/A"))

        # 🔹 Venue & Toss
        st.markdown("### 📍 Venue & Toss")
        venue_str = f"{venue_info.get('ground','')}, {venue_info.get('city','')} ({venue_info.get('country','')})"
        st.write(f"**Venue:** {venue_str}")
        toss = match_info.get("tossResults", {})
        st.write(f"**Toss:** {toss.get('tossWinnerName','N/A')} won the toss and chose to **{toss.get('decision','N/A')}**")

        # 🔹 Result
        state = match_info.get("state", "").lower()
        match_format = match_info.get("matchFormat", "").upper()
    
        if state == "inprogress":
            # ✅ Live Match → Show Score Summary
            scorecard = fetch_scorecard(match_id)
            live_scores = scorecard.get("scorecard", [])

            if live_scores:
                st.markdown("## 🏏 Live Score")

                # CSS for cards
                st.markdown("""
                    <style>
                    .live-card {
                        background: #f8f9fa;
                        border-radius: 12px;
                        padding: 15px;
                        margin-bottom: 15px;
                        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
                    }
                    .live-card h4 {
                        margin: 0;
                        font-size: 20px;
                        color: #2c3e50;
                    }
                    .live-card p {
                        margin: 4px 0;
                        font-size: 18px;
                        color: #444;
                    }
                    .sub {
                        font-size: 15px;
                        color: #555;
                        margin-left: 10px;
                    }
                    </style>
                """, unsafe_allow_html=True)

                if match_format in ["ODI", "T20", "IPL"]:
                    for inng in live_scores:
                        team = inng.get("batteamname", "N/A")
                        runs = inng.get("score", 0)
                        wkts = inng.get("wickets", 0)
                        overs = inng.get("overs", 0.0)
                        target = inng.get("target", None)

                        batsmen = inng.get("batsman", [])[:2]  # last 2 batsmen
                        bowlers = inng.get("bowler", [])[:2]   # last 2 bowlers

                        # 🟢 Score Card
                        st.markdown(f"""
                            <div class="live-card">
                                <h4>{team}</h4>
                                <p><b>Score:</b> {runs}/{wkts} ({overs} ov)</p>
                                <p><b>CRR:</b> {round(runs/overs,2) if overs>0 else '-'} </p>
                            </div>
                        """, unsafe_allow_html=True)

                        # 🏏 Current Batsmen
                        if batsmen:
                            st.markdown("**🦸‍♂️ Batsmen at Crease**")
                            for b in batsmen:
                                st.write(f"- {b.get('name')} : {b.get('runs')}-{b.get('balls')}  (4s: {b.get('fours')}, 6s: {b.get('sixes')}, SR: {b.get('strkrate')})")

                        # 🎯 Current Bowlers
                        if bowlers:
                            st.markdown("**🎯 Current Bowlers**")
                            for bw in bowlers:
                                st.write(f"- {bw.get('name')} : {bw.get('overs')} overs, {bw.get('maidens')} maidens, {bw.get('runs')} runs, {bw.get('wickets')} wkts, ECO {bw.get('economy')}")

                        # 🟡 Chase Banner
                        if target and target > 0:
                            remaining_runs = target - runs
                            max_overs = 50 if match_format == "ODI" else 20
                            remaining_overs = max_overs - overs
                            if remaining_runs > 0 and remaining_overs > 0:
                                rrr = round(remaining_runs / remaining_overs, 2)
                                st.markdown(f"""
                                    <div style='background:#fff3cd;padding:12px;
                                                border-radius:10px;font-size:16px;
                                                text-align:center;font-weight:bold;'>
                                        {team} need {remaining_runs} runs in {remaining_overs} overs (RRR {rrr})
                                    </div>
                                """, unsafe_allow_html=True)

                elif match_format == "TEST":
                    for inng in live_scores:
                        team = inng.get("batteamname", "N/A")
                        runs = inng.get("score", 0)
                        wkts = inng.get("wickets", 0)
                        overs = inng.get("overs", 0.0)

                        batsmen = inng.get("batsman", [])[:2]
                        bowlers = inng.get("bowler", [])[:2]

                        # 🟢 Score Card
                        st.markdown(f"""
                            <div class="live-card">
                                <h4>{team}</h4>
                                <p><b>Score:</b> {runs}/{wkts} ({overs} ov)</p>
                            </div>
                        """, unsafe_allow_html=True)

                        # 🏏 Batsmen
                        if batsmen:
                            st.markdown("**🦸‍♂️ Batsmen at Crease**")
                            for b in batsmen:
                                st.write(f"- {b.get('name')} : {b.get('runs')}-{b.get('balls')}  (4s: {b.get('fours')}, 6s: {b.get('sixes')}, SR: {b.get('strkrate')})")

                        # 🎯 Bowlers
                        if bowlers:
                            st.markdown("**🎯 Current Bowlers**")
                            for bw in bowlers:
                                st.write(f"- {bw.get('name')} : {bw.get('overs')} overs, {bw.get('maidens')} maidens, {bw.get('runs')} runs, {bw.get('wickets')} wkts, ECO {bw.get('economy')}")

                        lead_by = inng.get("leadBy", None)
                        trail_by = inng.get("trailBy", None)
                        if lead_by:
                            st.success(f"{team} lead by {lead_by} runs")
                        if trail_by:
                            st.warning(f"{team} trail by {trail_by} runs")

        else:
            # ✅ Completed Match → Show Result
            result = match_info.get("result", {})
            if result:
                if result.get("winByRuns"):
                    res_str = f"{result.get('winningTeam')} won by {result.get('winningMargin')} runs"
                elif result.get("winByInnings"):
                    res_str = f"{result.get('winningTeam')} won by innings and {result.get('winningMargin')} runs"
                else:
                    res_str = f"{result.get('winningTeam')} won"

                st.success(f"✅ Result: {res_str}")

            # 🏅 Player of the Match
            pom = match_info.get("playersOfTheMatch", [])
            if pom:
                pom_player = pom[0]
                st.markdown("### 🏅 Player of the Match")
                st.info(f"{pom_player.get('name')} ({pom_player.get('teamName')})")


        # 🔹 Umpires & Referee
        st.markdown("### 👨‍⚖️ Match Officials")
        st.write(f"**Umpires:** {match_info.get('umpire1',{}).get('name','')} , {match_info.get('umpire2',{}).get('name','')}")
        st.write(f"**Referee:** {match_info.get('referee',{}).get('name','')}")


    # with tab1:
    #     st.subheader("📋 Match Summary")

    #     match_header = score_data.get("matchHeader", {})
    #     venue = match_header.get("venue", {})
    #     toss = match_header.get("tossResults", {})

    #     # 🔹 Match Info Cards
    #     st.markdown("""
    #         <style>
    #         .card {
    #             background-color: #f8f9fa;
    #             padding: 15px;
    #             border-radius: 10px;
    #             box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    #             text-align: center;
    #             margin-bottom: 10px;
    #         }
    #         .card h3 { margin: 0; font-size: 18px; color: #2c3e50; }
    #         .card p { margin: 0; font-size: 14px; color: #555; }
    #         </style>
    #     """, unsafe_allow_html=True)

    #     col1, col2, col3, col4 = st.columns(4)
    #     col1.markdown(f"<div class='card'><h3>{match_header.get('matchDescription','')}</h3><p>Match</p></div>", unsafe_allow_html=True)
    #     col2.markdown(f"<div class='card'><h3>{match_header.get('matchFormat','')}</h3><p>Format</p></div>", unsafe_allow_html=True)
    #     col3.markdown(f"<div class='card'><h3>{venue.get('ground','')}, {venue.get('city','')}</h3><p>Venue</p></div>", unsafe_allow_html=True)
    #     col4.markdown(f"<div class='card'><h3>{toss.get('text','N/A')}</h3><p>Toss</p></div>", unsafe_allow_html=True)

    #     # 🔹 Status Row
    #     col5, col6 = st.columns(2)
    #     col5.markdown(f"<div class='card'><h3>{match_header.get('status','')}</h3><p>Status</p></div>", unsafe_allow_html=True)
    #     col6.markdown(f"<div class='card'><h3>{match_header.get('seriesName','')}</h3><p>Series</p></div>", unsafe_allow_html=True)

    #     # 🔹 Innings Summary
    #     for inng in score_data.get("scorecard", []):
    #         team_name = inng.get("batteamname", "Unknown Team")
    #         total_runs = inng.get("runs", "-")
    #         total_wkts = inng.get("wickets", "-")
    #         overs = inng.get("overs", "-")
    #         cr = inng.get("crrunrate", "-")

    #         st.markdown(f"### {team_name} {total_runs}/{total_wkts} ({overs} ov) | CRR: {cr}")

    # ---- Full Scorecard ----
    with tab2:
        for inng in score_data.get("scorecard", []):
            team_name = inng.get("batteamname", "Unknown Team")
            st.markdown(f"## 🏏 {team_name} Innings")

            # Batting
            bats = []
            for b in inng.get("batsman", []):
                bats.append([b.get("name"), b.get("runs"), b.get("balls"), b.get("fours"), b.get("sixes"), b.get("strkrate")])
            if bats:
                st.markdown("### Batting")
                df_bat = pd.DataFrame(bats, columns=["Batsman", "R", "B", "4s", "6s", "SR"])
                st.table(df_bat)

            # Bowling
            bowls = []
            for bw in inng.get("bowler", []):
                bowls.append([bw.get("name"), bw.get("overs"), bw.get("maidens"), bw.get("runs"), bw.get("wickets"), bw.get("economy")])
            if bowls:
                st.markdown("### Bowling")
                df_bowl = pd.DataFrame(bowls, columns=["Bowler", "O", "M", "R", "W", "ECO"])
                st.table(df_bowl)

            # Fall of Wickets (Inline Style)
            fow_data = inng.get("fow", {}).get("fow", [])
            if fow_data:
                fow_list = []
                for w in fow_data:
                    runs = w.get("runs", "-")
                    player = w.get("batsmanname", "Unknown")
                    over = w.get("overnbr", "-")
                    fow_list.append(f"{runs} ({player}, {over} ov)")

                fow_str = " , ".join(fow_list)
                st.markdown("### 🧨 Fall of Wickets")
                st.write(f"**FoW:** {fow_str}")


            # # Partnerships
            # if "partnerships" in inng:
            #     partners = []
            #     for p in inng["partnerships"]:
            #         partners.append([f"{p.get('bat1Name')} & {p.get('bat2Name')}", p.get("runs"), p.get("balls")])
            #     if partners:
            #         st.markdown("### 🤝 Partnerships")
            #         df_part = pd.DataFrame(partners, columns=["Batsmen", "Runs", "Balls"])
            #         st.table(df_part)