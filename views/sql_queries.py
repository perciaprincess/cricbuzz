import streamlit as st
import pandas as pd
from utils.db_connection import get_connection
from utils.queries_mapping import PREDEFINED_QUERIES

def run_query(query):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows)
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return pd.DataFrame()
    finally:
        cursor.close()
        conn.close()

# --- Streamlit Page ---
def render():
    st.title("🔍 SQL Queries & Analytics")

    # Dropdown for 25 predefined queries
    st.subheader("📌 Predefined Queries")
    selected = st.selectbox("Choose a question to run", list(PREDEFINED_QUERIES.keys()))

    if st.button("Run Selected Query"):
        query = PREDEFINED_QUERIES[selected]
        st.code(query.strip(), language="sql")
        df = run_query(query)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("⚠️ No results found for this query.")

    st.markdown("---")

    # Custom Query Section
    st.subheader("📝 Custom SQL Query")
    query = st.text_area("Write your SQL here")
    if st.button("Run Custom Query"):
        if query.strip() != "":
            df = run_query(query)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("⚠️ No results found.")
        else:
            st.warning("⚠️ Please enter a query before running.")