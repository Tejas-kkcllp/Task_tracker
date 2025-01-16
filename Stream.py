import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import os

# Function to list all database files in the current directory
def list_databases():
    if not os.path.exists('data'):
        os.makedirs('data')
    return [db for db in os.listdir('data') if db.endswith(".db")]

# Initialize the Database
def init_db(db_name):
    db_path = os.path.join('data', db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS work_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        client_name TEXT,
                        client_location TEXT,
                        work_of_visit TEXT,
                        requirements TEXT,
                        note TEXT,
                        hours_worked REAL)'''
    )
    conn.commit()
    conn.close()

# Add Entry to Database
def add_entry(db_name, client_name, client_location, work_of_visit, requirements, note, hours_worked):
    date = datetime.now().strftime("%Y-%m-%d")
    db_path = os.path.join('data', db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO work_entries (date, client_name, client_location, work_of_visit, 
                      requirements, note, hours_worked) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (date, client_name, client_location, work_of_visit, requirements, note, hours_worked))
    conn.commit()
    conn.close()

# Load Data from Database
def load_data(db_name):
    db_path = os.path.join('data', db_name)
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM work_entries", conn)
    conn.close()
    return df

# Clear Data from Database
def clear_data(db_name):
    db_path = os.path.join('data', db_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM work_entries")
    conn.commit()
    conn.close()

# Export Data to Excel
@st.cache_data
def export_data(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine="xlsxwriter")
    processed_data = output.getvalue()
    return processed_data

# Page Configuration
st.set_page_config(
    page_title="Work Tracker Tool",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'databases' not in st.session_state:
    st.session_state.databases = list_databases()

# Sidebar
st.sidebar.title("📁 Database Manager")
selected_db = st.sidebar.selectbox("Select Database", st.session_state.databases)

if st.sidebar.button("Create New Database"):
    new_db_name = f"work_tracker_{datetime.now().strftime('%B_%Y')}.db"
    if new_db_name not in st.session_state.databases:
        init_db(new_db_name)
        st.session_state.databases = list_databases()
        st.sidebar.success(f"🎉 New database '{new_db_name}' created!")
        st.rerun()  # Changed from experimental_rerun() to rerun()
    else:
        st.sidebar.warning("⚠️ Database already exists!")

if st.sidebar.button("Clear Current Database"):
    if selected_db:
        clear_data(selected_db)
        st.sidebar.success("✅ Current database cleared!")

# Main Content
if not selected_db:
    st.warning("⚠️ Please select or create a database from the sidebar.")
else:
    init_db(selected_db)
    st.sidebar.markdown(f"**Current Database:** `{selected_db}`")

    # Title Section
    st.title("🌟 Work Tracker Tool")
    st.markdown("Keep track of your tasks and activities with an intuitive interface!")

    # Add Entry Form
    with st.form("entry_form", clear_on_submit=True):
        st.markdown("### 📝 Add New Entry")
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("👤 Client Name", placeholder="Enter the client name")
            work_of_visit = st.text_input("🔧 Work of Visit", placeholder="Describe the purpose of the visit")
            requirements = st.text_area("📋 Requirements", placeholder="Enter client requirements")
        
        with col2:
            client_location = st.text_input("📍 Client Location", placeholder="Enter the client's location")
            hours_worked = st.number_input("⏱️ Hours of Working", min_value=0.0, step=0.5)
            note = st.text_area("📝 Note", placeholder="Add any additional notes")
        
        submitted = st.form_submit_button("Submit ✅")

        if submitted:
            if client_name and client_location and work_of_visit and requirements and hours_worked > 0:
                add_entry(selected_db, client_name, client_location, work_of_visit, requirements, note, hours_worked)
                st.success("🎉 Entry added successfully!")
            else:
                st.error("⚠️ All fields are required!")

    # Display Data Section
    st.markdown("### 📊 View Work Entries")
    data = load_data(selected_db)
    if not data.empty:
        st.dataframe(data.style.set_properties(**{'text-align': 'left'}), use_container_width=True)

        excel_data = export_data(data)
        st.download_button(
            label="📥 Export Data to Excel",
            data=excel_data,
            file_name=f"{selected_db.replace('.db', '')}_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ℹ️ No entries found. Add some tasks to get started!")

    st.markdown(
        '<div style="text-align: center; padding: 10px; margin-top: 20px; color: white; background-color: #007acc;">'
        '<h4>💼 Created by Tejas Gavale</h4>'
        '</div>', 
        unsafe_allow_html=True
    )
