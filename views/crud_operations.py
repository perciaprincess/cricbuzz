import streamlit as st
import pandas as pd
from utils.db_connection import get_connection

# ===============================
# Custom CSS for UI Styling
# ===============================
st.markdown("""
    <style>
    div[data-testid="stCaptionContainer"] p {
        font-size:18px !important;
        color:#333 !important;
        font-weight:600 !important;
    }

    /* 🔹 Normal buttons */
    div.stButton > button {
        background-color: #4a66d5 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        height: 42px !important;
        width: 170px !important;
        border: none !important;
    }

    /* 🔹 Form submit buttons (st.form_submit_button) */
    button[data-testid="stFormSubmitButton"] {
        background-color: #4a66d5 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        height: 42px !important;
        width: 170px !important;
        border: none !important;
    }

    /* 🔹 Hover effect */
    div.stButton > button:hover,
    button[data-testid="stFormSubmitButton"]:hover {
        background-color: #3b53b0 !important;
        color: white !important;
    }

    </style>
""", unsafe_allow_html=True)

def render():
    st.title("🏏 CRUD Operations - Player Stats")
    st.caption("Easily manage player statistics with CRUD operations")

    # Tabs for each operation
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add", "✏️ Update", "🗑 Delete", "📊 View"])

    conn = get_connection()
    cursor = conn.cursor()

    # =========================================
    # Add Player
    # =========================================
    with tab1:
        with st.form("add_form"):
            st.subheader("➕ Add New Player")
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Player Name")
                matches = st.number_input("Matches", 0)
                innings = st.number_input("Innings", 0)
            with col2:
                runs = st.number_input("Runs", 0)
                batting_avg = st.number_input("Batting Avg", 0.0)

            submitted = st.form_submit_button("✅ Add Player")
            if submitted:
                cursor.execute("""
                    INSERT INTO batting_stats 
                        (player_name, runs, matches, innings, batting_avg, year) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (name, runs, matches, innings, batting_avg, 0))
                conn.commit()
                st.success(f"🎉 Player {name} added!")

    # =========================================
    # Update Player (by Name)
    # =========================================
    with tab2:
        with st.form("update_form"):
            st.subheader("✏️ Update Player Stats")
            player_name = st.text_input("Enter Player Name")
            new_runs = st.number_input("New Runs", 0)

            submitted = st.form_submit_button("🔄 Update Player")
            if submitted:
                cursor.execute("UPDATE batting_stats SET runs=%s WHERE player_name=%s", (new_runs, player_name))
                conn.commit()
                st.success(f"✅ Player '{player_name}' updated!")

    # =========================================
    # Delete Player (by Name)
    # =========================================
    with tab3:
        with st.form("delete_form"):
            st.subheader("🗑 Delete Player")
            player_name = st.text_input("Enter Player Name to Delete")

            submitted = st.form_submit_button("🚨 Delete Player")
            if submitted:
                cursor.execute("DELETE FROM batting_stats WHERE player_name=%s", (player_name,))
                conn.commit()
                st.error(f"❌ Player '{player_name}' deleted!")

    # =========================================
    # View Players
    # =========================================
    with tab4:
        st.subheader("📊 Player Records")
        cursor.execute("SELECT player_name, matches, innings, runs, batting_avg FROM batting_stats WHERE year=0")
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows)  
            st.dataframe(df, use_container_width=True, height=400)
        else:
            st.warning("⚠️ No player data found!")

    cursor.close()
    conn.close()