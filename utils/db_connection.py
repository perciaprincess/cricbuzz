import streamlit as st
import pymysql

def get_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="123456",
            database="cricbuzz_live",
            cursorclass=pymysql.cursors.DictCursor 
        )
        return conn
    except pymysql.MySQLError as err:
        st.error(f"Database connection failed: {err}")
        return None
