# ============================================================
# DATABASE.PY — All DB connections and CRUD operations
# ============================================================

import mysql.connector
import pandas as pd
import streamlit as st
from datetime import date
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ── CONNECTION ─────────────────────────────────────────────
def _cfg():
    """Read DB credentials from st.secrets (Streamlit Cloud deployment)."""
    return dict(
        host     = st.secrets["db"]["host"],
        user     = st.secrets["db"]["user"],
        password = st.secrets["db"]["password"],
        port     = int(st.secrets["db"]["port"]),
        database = st.secrets["db"]["database"],
    )

def get_conn():
    cfg = _cfg()
    return mysql.connector.connect(**cfg)

def get_engine():
    cfg = _cfg()
    # Use SQLAlchemy URL object — safely handles special chars in password
    url = URL.create(
        drivername = "mysql+pymysql",
        username   = cfg["user"],
        password   = cfg["password"],   # no manual URL-encoding needed
        host       = cfg["host"],
        port       = cfg["port"],
        database   = cfg["database"],
    )
    return create_engine(url)

# ── GENERIC HELPERS ────────────────────────────────────────
def read_df(sql, params=None):
    try:
        engine = get_engine()
        with engine.connect() as conn:
            df = pd.read_sql(text(sql), conn, params=params)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

def run_write(sql, params=None):
    try:
        conn = get_conn()
        cur  = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        affected = cur.rowcount
        cur.close(); conn.close()
        return affected, None
    except Exception as e:
        return 0, str(e)

# ── AUTH ───────────────────────────────────────────────────
def verify_login(username, password):
    try:
        conn = get_conn()
        cur  = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT User_ID, Username, Role, Full_Name FROM Users "
            "WHERE Username=%s AND Password=SHA2(%s,256)",
            (username, password)
        )
        user = cur.fetchone()
        cur.close(); conn.close()
        return user
    except:
        return None

# ── DASHBOARD STATS ────────────────────────────────────────
def get_stats():
    conn  = get_conn()
    cur   = conn.cursor(dictionary=True)
    stats = {}
    queries = {
        "stories"   : "SELECT COUNT(*) AS n FROM Story",
        "ongoing"   : "SELECT COUNT(*) AS n FROM Story WHERE Status='Ongoing'",
        "completed" : "SELECT COUNT(*) AS n FROM Story WHERE Status='Completed'",
        "sources"   : "SELECT COUNT(*) AS n FROM Source",
        "interviews": "SELECT COUNT(*) AS n FROM Interview",
        "documents" : "SELECT COUNT(*) AS n FROM Document",
        "locations" : "SELECT COUNT(*) AS n FROM Location",
        "notes"     : "SELECT COUNT(*) AS n FROM Note",
        "events"    : "SELECT COUNT(*) AS n FROM Timeline_Event",
        "users"     : "SELECT COUNT(*) AS n FROM Users",
        "complaints": "SELECT COUNT(*) AS n FROM Complaints WHERE Status='Open'",
    }
    for key, q in queries.items():
        try:
            cur.execute(q)
            stats[key] = cur.fetchone()["n"]
        except:
            stats[key] = 0
    cur.close(); conn.close()
    return stats

# ── STORY ──────────────────────────────────────────────────
def get_stories():
    return read_df("SELECT * FROM v_story_overview ORDER BY Story_ID DESC")

def add_story(title, desc, category, start_date, status):
    return run_write(
        "INSERT INTO Story (Title,Description,Category,Start_Date,Status) VALUES (%s,%s,%s,%s,%s)",
        (title, desc, category, start_date, status)
    )

def update_story(story_id, title, desc, category, start_date, status):
    return run_write(
        "UPDATE Story SET Title=%s,Description=%s,Category=%s,Start_Date=%s,Status=%s WHERE Story_ID=%s",
        (title, desc, category, start_date, status, story_id)
    )

def delete_story(story_id):
    return run_write("DELETE FROM Story WHERE Story_ID=%s", (story_id,))

def get_story_ids():
    df, _ = read_df("SELECT Story_ID, Title FROM Story ORDER BY Story_ID")
    return df

# ── SOURCE ─────────────────────────────────────────────────
def get_sources():
    return read_df("SELECT * FROM v_source_overview ORDER BY Source_ID DESC")

def add_source(name, stype, contact, credibility):
    return run_write(
        "INSERT INTO Source (Name,Type,Contact_Info,Credibility_Level) VALUES (%s,%s,%s,%s)",
        (name, stype, contact, credibility)
    )

def update_source(source_id, name, stype, contact, credibility):
    return run_write(
        "UPDATE Source SET Name=%s,Type=%s,Contact_Info=%s,Credibility_Level=%s WHERE Source_ID=%s",
        (name, stype, contact, credibility, source_id)
    )

def delete_source(source_id):
    return run_write("DELETE FROM Source WHERE Source_ID=%s", (source_id,))

def get_source_ids():
    df, _ = read_df("SELECT Source_ID, Name FROM Source ORDER BY Source_ID")
    return df

# ── INTERVIEW ──────────────────────────────────────────────
def get_interviews():
    return read_df("SELECT * FROM v_interview_details ORDER BY Interview_ID DESC")

def add_interview(idate, mode, transcript, story_id, source_id):
    return run_write(
        "INSERT INTO Interview (Interview_Date,Mode,Transcript,Story_ID,Source_ID) VALUES (%s,%s,%s,%s,%s)",
        (idate, mode, transcript, story_id, source_id)
    )

def update_interview(iid, idate, mode, transcript, story_id, source_id):
    return run_write(
        "UPDATE Interview SET Interview_Date=%s,Mode=%s,Transcript=%s,Story_ID=%s,Source_ID=%s WHERE Interview_ID=%s",
        (idate, mode, transcript, story_id, source_id, iid)
    )

def delete_interview(iid):
    return run_write("DELETE FROM Interview WHERE Interview_ID=%s", (iid,))

# ── DOCUMENT ───────────────────────────────────────────────
def get_documents():
    return read_df("SELECT * FROM v_document_details ORDER BY Document_ID DESC")

def add_document(title, dtype, upload_date, story_id):
    return run_write(
        "INSERT INTO Document (Title,Type,Upload_Date,Story_ID) VALUES (%s,%s,%s,%s)",
        (title, dtype, upload_date, story_id)
    )

def update_document(did, title, dtype, upload_date, story_id):
    return run_write(
        "UPDATE Document SET Title=%s,Type=%s,Upload_Date=%s,Story_ID=%s WHERE Document_ID=%s",
        (title, dtype, upload_date, story_id, did)
    )

def delete_document(did):
    return run_write("DELETE FROM Document WHERE Document_ID=%s", (did,))

# ── LOCATION ───────────────────────────────────────────────
def get_locations():
    return read_df("SELECT * FROM v_location_story ORDER BY Location_ID DESC")

def add_location(place, city, state, country, story_id):
    return run_write(
        "INSERT INTO Location (Place_Name,City,State,Country,Story_ID) VALUES (%s,%s,%s,%s,%s)",
        (place, city, state, country, story_id)
    )

def update_location(lid, place, city, state, country, story_id):
    return run_write(
        "UPDATE Location SET Place_Name=%s,City=%s,State=%s,Country=%s,Story_ID=%s WHERE Location_ID=%s",
        (place, city, state, country, story_id, lid)
    )

def delete_location(lid):
    return run_write("DELETE FROM Location WHERE Location_ID=%s", (lid,))

# ── NOTE ───────────────────────────────────────────────────
def get_notes():
    return read_df("""
        SELECT n.Note_ID, n.Content, n.Created_Date, s.Title AS Story_Title
        FROM Note n JOIN Story s ON n.Story_ID = s.Story_ID
        ORDER BY n.Note_ID DESC
    """)

def add_note(content, created_date, story_id):
    return run_write(
        "INSERT INTO Note (Content,Created_Date,Story_ID) VALUES (%s,%s,%s)",
        (content, created_date, story_id)
    )

def delete_note(nid):
    return run_write("DELETE FROM Note WHERE Note_ID=%s", (nid,))

# ── TIMELINE ───────────────────────────────────────────────
def get_timeline():
    return read_df("SELECT * FROM v_timeline_details ORDER BY Event_Date DESC")

def add_event(title, event_date, desc, story_id):
    return run_write(
        "INSERT INTO Timeline_Event (Event_Title,Event_Date,Description,Story_ID) VALUES (%s,%s,%s,%s)",
        (title, event_date, desc, story_id)
    )

def delete_event(eid):
    return run_write("DELETE FROM Timeline_Event WHERE Event_ID=%s", (eid,))

# ── USERS ──────────────────────────────────────────────────
def get_users():
    return read_df(
        "SELECT User_ID, Username, Role, Full_Name, Created_At FROM Users ORDER BY User_ID"
    )

def add_user(username, password, role, full_name):
    return run_write(
        "INSERT INTO Users (Username,Password,Role,Full_Name) VALUES (%s,SHA2(%s,256),%s,%s)",
        (username, password, role, full_name)
    )

def delete_user(uid):
    return run_write("DELETE FROM Users WHERE User_ID=%s", (uid,))

# ── AUDIT LOG ──────────────────────────────────────────────
def get_audit_log():
    return read_df("SELECT * FROM v_audit_trail LIMIT 100")

# ── COMPLAINTS ─────────────────────────────────────────────
def get_complaints():
    return read_df("SELECT * FROM Complaints ORDER BY Created_At DESC")

def get_complaints_for_user(username):
    return read_df(
        "SELECT * FROM Complaints WHERE Submitted_By=:username ORDER BY Created_At DESC",
        params={"username": username}
    )

def add_complaint(title, desc, submitted_by):
    return run_write(
        "INSERT INTO Complaints (Title,Description,Submitted_By,Status) VALUES (%s,%s,%s,'Open')",
        (title, desc, submitted_by)
    )

def resolve_complaint(cid, admin_note):
    return run_write(
        "UPDATE Complaints SET Status='Rectified', Admin_Note=%s WHERE Complaint_ID=%s",
        (admin_note, cid)
    )

def delete_complaint(cid):
    return run_write("DELETE FROM Complaints WHERE Complaint_ID=%s", (cid,))

# ── STORY PROGRESS ─────────────────────────────────────────
def get_story_progress(story_id):
    checks = {
        "Interview"     : "SELECT COUNT(*) AS n FROM Interview WHERE Story_ID=%s",
        "Document"      : "SELECT COUNT(*) AS n FROM Document WHERE Story_ID=%s",
        "Location"      : "SELECT COUNT(*) AS n FROM Location WHERE Story_ID=%s",
        "Note"          : "SELECT COUNT(*) AS n FROM Note WHERE Story_ID=%s",
        "Timeline_Event": "SELECT COUNT(*) AS n FROM Timeline_Event WHERE Story_ID=%s",
    }
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    score   = 0
    details = {}
    for label, q in checks.items():
        cur.execute(q, (story_id,))
        n = cur.fetchone()["n"]
        details[label] = n
        if n > 0:
            score += 1
    cur.close(); conn.close()
    progress = int((score / len(checks)) * 100)
    return progress, details
