import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import os

# Initialize session state for database management
if 'databases' not in st.session_state:
    st.session_state.databases = [db for db in os.listdir() if db.endswith(".db")]

# Function to list all database files in the current directory
def list_databases():
    return [db for db in os.listdir() if db.endswith(".db")]

# Function to rename database
def rename_database(old_name, new_name):
    if not new_name.endswith('.db'):
        new_name = f"{new_name}.db"
    try:
        os.rename(old_name, new_name)
        return True
    except Exception as e:
        st.error(f"Error renaming database: {str(e)}")
        return False

# Initialize the Database
def init_db(db_name):
    if not db_name.endswith('.db'):
        db_name = f"{db_name}.db"
    conn = sqlite3.connect(db_name)
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

# Other database functions remain the same
def add_entry(db_name, client_name, client_location, work_of_visit, requirements, note, hours_worked):
    date = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO work_entries (date, client_name, client_location, work_of_visit, 
                      requirements, note, hours_worked) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (date, client_name, client_location, work_of_visit, requirements, note, hours_worked))
    conn.commit()
    conn.close()

def load_data(db_name):
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("SELECT * FROM work_entries", conn)
    conn.close()
    return df

def clear_data(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM work_entries")
    conn.commit()
    conn.close()

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

# Sidebar Database Management
st.sidebar.title("📁 Database Manager")

# Database Creation Section
st.sidebar.subheader("Create New Database")
new_db_name = st.sidebar.text_input("Database Name", key="new_db")
if st.sidebar.button("Create Database"):
    if new_db_name:
        if not new_db_name.endswith('.db'):
            new_db_name = f"{new_db_name}.db"
        if new_db_name not in st.session_state.databases:
            init_db(new_db_name)
            st.session_state.databases = list_databases()
            st.sidebar.success(f"🎉 New database '{new_db_name}' created!")
            st.rerun()
        else:
            st.sidebar.warning("⚠️ Database already exists!")
    else:
        st.sidebar.warning("⚠️ Please enter a database name!")

# Database Selection
selected_db = st.sidebar.selectbox(
    "Select Database",
    st.session_state.databases,
    index=0 if st.session_state.databases else None
)

# Database Renaming Section
if selected_db:
    st.sidebar.subheader("Rename Selected Database")
    new_name = st.sidebar.text_input("New Name", key="rename_db")
    if st.sidebar.button("Rename Database"):
        if new_name:
            if rename_database(selected_db, new_name):
                st.session_state.databases = list_databases()
                st.sidebar.success(f"✅ Database renamed to '{new_name}'!")
                st.rerun()
        else:
            st.sidebar.warning("⚠️ Please enter a new name!")

    # Clear Database Button
    if st.sidebar.button("Clear Current Database"):
        clear_data(selected_db)
        st.sidebar.success("✅ Current database cleared!")

    # Delete Database Button
    if st.sidebar.button("Delete Current Database", type="primary"):
        if st.sidebar.button("Confirm Delete"):
            try:
                os.remove(selected_db)
                st.session_state.databases = list_databases()
                st.sidebar.success("✅ Database deleted successfully!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error deleting database: {str(e)}")

# Main Content
if not selected_db:
    st.warning("⚠️ Please select or create a database from the sidebar.")
else:
    init_db(selected_db)
    st.sidebar.markdown(f"**Current Database:** `{selected_db}`")

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
