import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

DB = Path(__file__).with_name("projects.db")
st.set_page_config(page_title="Project AI Assistant", page_icon="📊", layout="wide")

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, location TEXT, client TEXT, target TEXT,
        actual TEXT, manpower INTEGER DEFAULT 0, material_pending TEXT,
        issues TEXT, last_update TEXT)""")
    c.commit(); c.close()

def projects():
    c = db()
    rows = [dict(r) for r in c.execute("SELECT * FROM projects ORDER BY id DESC")]
    c.close()
    return rows

def save_project(values):
    c = db()
    c.execute("""INSERT INTO projects
    (name,location,client,target,actual,manpower,material_pending,issues,last_update)
    VALUES (?,?,?,?,?,?,?,?,?)""", values)
    c.commit(); c.close()

def answer(q, rows):
    if not rows:
        return "No project data yet. Add a project from the sidebar."
    q = q.lower()
    p = next((x for x in rows if x["name"].lower() in q or
              (x["location"] and x["location"].lower() in q)), rows[0])

    if any(k in q for k in ["material","pending","required"]):
        return f"**{p['name']} — Material pending:**\n\n{p['material_pending'] or 'None recorded.'}"
    if any(k in q for k in ["manpower","labour","labor","workers"]):
        return f"**{p['name']} — Manpower:** {p['manpower']}"
    if any(k in q for k in ["issue","problem","delay","reason"]):
        return f"**{p['name']} — Issues/Delays:**\n\n{p['issues'] or 'None recorded.'}"
    if any(k in q for k in ["target","actual","progress","achievement"]):
        return f"**{p['name']} — Progress**\n\n- Target: {p['target'] or '-'}\n- Actual: {p['actual'] or '-'}"
    if any(k in q for k in ["summary","status","overview"]):
        return (f"### {p['name']}\n- Location: {p['location'] or '-'}\n"
                f"- Target: {p['target'] or '-'}\n- Actual: {p['actual'] or '-'}\n"
                f"- Manpower: {p['manpower']}\n- Material pending: {p['material_pending'] or '-'}\n"
                f"- Issues: {p['issues'] or '-'}\n- Last update: {p['last_update'] or '-'}")
    return "Try asking: **What is the status?**, **What material is pending?**, **How many workers?**, or **What are the issues?**"

init_db()
st.title("📊 Project AI Assistant — Version 1")
st.caption("Local project database + natural-language questions")

with st.sidebar:
    st.header("Add Project")
    with st.form("add"):
        name = st.text_input("Project name *")
        location = st.text_input("Location")
        client = st.text_input("Client")
        target = st.text_input("Target")
        actual = st.text_input("Actual progress")
        manpower = st.number_input("Manpower", 0, 100000, 0)
        material = st.text_area("Material pending")
        issues = st.text_area("Issues / delays")
        date = st.date_input("Last update")
        if st.form_submit_button("Save project"):
            if name.strip():
                save_project((name.strip(),location,client,target,actual,int(manpower),material,issues,str(date)))
                st.success("Project saved.")
                st.rerun()
            else:
                st.error("Project name is required.")

rows = projects()
if rows:
    st.subheader("Ask about your project")
    q = st.text_input("Question", placeholder="What material is pending?")
    if q: st.markdown(answer(q, rows))
    st.divider()
    st.subheader("Project database")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("Add your first project using the sidebar.")

st.divider()
st.caption("Version 1 stores data locally. No API key is required.")
