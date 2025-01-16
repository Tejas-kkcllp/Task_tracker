import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
from io import BytesIO
import os

# Function to list all database files in the current directory
def list_databases():
    return [db for db in os.listdir() if db.endswith(".db")]

# Initialize the Database
def init_db(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    # Check if the table exists before creating
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
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO work_entries (date, client_name, client_location, work_of_visit, 
                      requirements, note, hours_worked) VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (date, client_name, client_location, work_of_visit, requirements, note, hours_worked))
    conn.commit()
    conn.close()

# Load Data from Database
def load_data(db_name):
    conn = sqlite3.connect(db_name)
    df = pd.read_sql_query("SELECT * FROM work_entries", conn)
    conn.close()
    return df

# Clear Data from Database
def clear_data(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM work_entries")
    conn.commit()
    conn.close()

# Export Data to Excel
def export_data(df):
    output = BytesIO()
    df.to_excel(output, index=False, engine="xlsxwriter")
    processed_data = output.getvalue()
    return processed_data

# Streamlit App Customization
st.set_page_config(
    page_title="Work Tracker Tool",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar: Select or create a database
st.sidebar.title("📁 Database Manager")
databases = list_databases()
selected_db = st.sidebar.selectbox("Select Database", databases)

if st.sidebar.button("Create New Database"):
    new_db_name = f"work_tracker_{datetime.now().strftime('%B_%Y')}.db"
    if new_db_name not in databases:
        init_db(new_db_name)
        st.sidebar.success(f"🎉 New database '{new_db_name}' created!")
        st.experimental_rerun()  # Refresh the app state
    else:
        st.sidebar.warning("⚠️ Database already exists!")

if st.sidebar.button("Clear Current Database"):
    if selected_db:
        clear_data(selected_db)
        st.sidebar.success("✅ Current database cleared!")

# Ensure a database is selected
if not selected_db:
    st.warning("⚠️ Please select or create a database from the sidebar.")
else:
    # Initialize the selected database
    init_db(selected_db)
    st.sidebar.markdown(f"**Current Database:** `{selected_db}`")

    # Add App Logo and Title
    st.image("https://via.placeholder.com/728x90.png?text=Work+Tracker+Tool", use_column_width=True)
    st.title("🌟 Work Tracker Tool")
    st.markdown("Keep track of your tasks and activities with an intuitive and visually appealing interface!")

    # Add Entry Form
    with st.form("entry_form"):
        st.markdown("### 📝 Add New Entry")
        client_name = st.text_input("👤 Client Name", placeholder="Enter the client name")
        client_location = st.text_input("📍 Client Location", placeholder="Enter the client's location")
        work_of_visit = st.text_input("🔧 Work of Visit", placeholder="Describe the purpose of the visit")
        requirements = st.text_area("📋 Requirements", placeholder="Enter client requirements")
        note = st.text_area("📝 Note", placeholder="Add any additional notes")
        hours_worked = st.number_input("⏱️ Hours of Working", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("Submit ✅")

        if submitted:
            if client_name and client_location and work_of_visit and requirements and hours_worked > 0:
                add_entry(selected_db, client_name, client_location, work_of_visit, requirements, note, hours_worked)
                st.success("🎉 Entry added successfully!")
            else:
                st.error("⚠️ All fields are required!")

    # Display Stored Data
    st.markdown("### 📊 View Work Entries")
    data = load_data(selected_db)
    if not data.empty:
        st.dataframe(data, use_container_width=True)

        # Export Data Button
        excel_data = export_data(data)
        st.download_button(
            label="📥 Export Data to Excel",
            data=excel_data,
            file_name=f"{selected_db.replace('.db', '')}_{datetime.now().strftime('%Y_%m_%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("ℹ️ No entries found. Add some tasks to get started!")

    # Footer
    st.markdown(
        '<div style="text-align: center; padding: 10px; margin-top: 20px; color: white; background-color: #007acc;">'
        '<h4>💼 Created by Tejas Gavale</h4>'
        '</div>', unsafe_allow_html=True
    )
