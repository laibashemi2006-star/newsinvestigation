import mysql.connector
import pandas as pd
import streamlit as st


# ══════════════════════════════════════════════════════════
# CONNECTION
# ══════════════════════════════════════════════════════════
def get_connection():
    try:
        return mysql.connector.connect(
            host     = st.secrets["db"]["host"],
            user     = st.secrets["db"]["user"],
            password = st.secrets["db"]["password"],
            port     = int(st.secrets["db"]["port"]),
            database = st.secrets["db"]["database"],
            connection_timeout = 10,
        )
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None


def run_query(sql, params=None, fetch=True):
    conn = get_connection()
    if conn is None:
        return None, "Connection failed"
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            df   = pd.DataFrame(rows)
            return df, None
        else:
            conn.commit()
            return cur.rowcount, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════
def verify_login(username, password):
    sql = """
        SELECT User_ID, Username, Role, Full_Name
        FROM Users
        WHERE Username = %s AND Password = SHA2(%s, 256)
    """
    df, err = run_query(sql, (username, password))
    if err or df is None or df.empty:
        return None
    return df.iloc[0].to_dict()


# ══════════════════════════════════════════════════════════
# DASHBOARD STATS
# ══════════════════════════════════════════════════════════
def get_stats():
    queries = {
        "stories":    "SELECT COUNT(*) AS n FROM Story",
        "ongoing":    "SELECT COUNT(*) AS n FROM Story WHERE Status='Ongoing'",
        "completed":  "SELECT COUNT(*) AS n FROM Story WHERE Status='Completed'",
        "sources":    "SELECT COUNT(*) AS n FROM Source",
        "interviews": "SELECT COUNT(*) AS n FROM Interview",
        "documents":  "SELECT COUNT(*) AS n FROM Document",
        "locations":  "SELECT COUNT(*) AS n FROM Location",
        "events":     "SELECT COUNT(*) AS n FROM Timeline_Event",
        "notes":      "SELECT COUNT(*) AS n FROM Note",
        "complaints":  "SELECT COUNT(*) AS n FROM Complaints WHERE Status='Open'",
    }
    stats = {}
    for key, sql in queries.items():
        df, _ = run_query(sql)
        stats[key] = int(df.iloc[0]["n"]) if df is not None and not df.empty else 0
    return stats


# ══════════════════════════════════════════════════════════
# STORIES
# ══════════════════════════════════════════════════════════
def get_stories():
    return run_query("""
        SELECT st.Story_ID, st.Title, st.Category, st.Status, st.Start_Date,
               COUNT(DISTINCT i.Interview_ID)  AS Total_Interviews,
               COUNT(DISTINCT d.Document_ID)   AS Total_Documents,
               COUNT(DISTINCT n.Note_ID)       AS Total_Notes,
               COUNT(DISTINCT te.Event_ID)     AS Total_Events,
               COUNT(DISTINCT l.Location_ID)   AS Total_Locations
        FROM Story st
        LEFT JOIN Interview    i  ON st.Story_ID = i.Story_ID
        LEFT JOIN Document     d  ON st.Story_ID = d.Story_ID
        LEFT JOIN Note         n  ON st.Story_ID = n.Story_ID
        LEFT JOIN Timeline_Event te ON st.Story_ID = te.Story_ID
        LEFT JOIN Location     l  ON st.Story_ID = l.Story_ID
        GROUP BY st.Story_ID, st.Title, st.Category, st.Status, st.Start_Date
        ORDER BY st.Story_ID DESC
    """)


# ══════════════════════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════════════════════
def get_sources():
    return run_query("""
        SELECT s.Source_ID, s.Name, s.Type, s.Contact_Info,
               CASE s.Credibility_Level
                   WHEN 1 THEN 'Low'
                   WHEN 2 THEN 'Medium'
                   WHEN 3 THEN 'High'
               END AS Credibility,
               COUNT(DISTINCT i.Interview_ID) AS Total_Interviews
        FROM Source s
        LEFT JOIN Interview i ON s.Source_ID = i.Source_ID
        GROUP BY s.Source_ID, s.Name, s.Type, s.Contact_Info, s.Credibility_Level
        ORDER BY s.Source_ID
    """)


# ══════════════════════════════════════════════════════════
# INTERVIEWS
# ══════════════════════════════════════════════════════════
def get_interviews():
    return run_query("""
        SELECT i.Interview_ID, i.Interview_Date, i.Mode, i.Transcript,
               s.Name AS Source_Name, s.Type AS Source_Type,
               CASE s.Credibility_Level
                   WHEN 1 THEN 'Low'
                   WHEN 2 THEN 'Medium'
                   WHEN 3 THEN 'High'
               END AS Credibility,
               st.Title AS Story_Title, st.Category, st.Status
        FROM Interview i
        JOIN Source s  ON i.Source_ID = s.Source_ID
        JOIN Story  st ON i.Story_ID  = st.Story_ID
        ORDER BY i.Interview_Date DESC
    """)


# ══════════════════════════════════════════════════════════
# DOCUMENTS
# ══════════════════════════════════════════════════════════
def get_documents():
    return run_query("""
        SELECT d.Document_ID, d.Title AS Document_Title,
               d.Type AS Document_Type, d.Upload_Date,
               st.Title AS Story_Title, st.Category, st.Status
        FROM Document d
        JOIN Story st ON d.Story_ID = st.Story_ID
        ORDER BY d.Upload_Date DESC
    """)


# ══════════════════════════════════════════════════════════
# LOCATIONS
# ══════════════════════════════════════════════════════════
def get_locations():
    return run_query("""
        SELECT l.Location_ID, l.Place_Name, l.City, l.State, l.Country,
               st.Title AS Story_Title, st.Category, st.Status
        FROM Location l
        JOIN Story st ON l.Story_ID = st.Story_ID
        ORDER BY l.City
    """)


# ══════════════════════════════════════════════════════════
# NOTES
# ══════════════════════════════════════════════════════════
def get_notes():
    return run_query("""
        SELECT n.Note_ID, n.Content, n.Created_Date,
               st.Title AS Story_Title, st.Category
        FROM Note n
        JOIN Story st ON n.Story_ID = st.Story_ID
        ORDER BY n.Created_Date DESC
    """)


# ══════════════════════════════════════════════════════════
# TIMELINE
# ══════════════════════════════════════════════════════════
def get_timeline():
    return run_query("""
        SELECT te.Event_ID, te.Event_Title, te.Event_Date,
               te.Description AS Event_Description,
               st.Title AS Story_Title, st.Category, st.Status
        FROM Timeline_Event te
        JOIN Story st ON te.Story_ID = st.Story_ID
        ORDER BY te.Event_Date DESC
    """)


# ══════════════════════════════════════════════════════════
# USERS  (Admin only)
# ══════════════════════════════════════════════════════════
def get_users():
    return run_query("""
        SELECT User_ID, Username, Role, Full_Name, Created_At
        FROM Users
        ORDER BY Created_At DESC
    """)


def add_user(username, password, role, full_name):
    return run_query("""
        INSERT INTO Users (Username, Password, Role, Full_Name)
        VALUES (%s, SHA2(%s, 256), %s, %s)
    """, (username, password, role, full_name), fetch=False)


# ══════════════════════════════════════════════════════════
# COMPLAINTS
# ══════════════════════════════════════════════════════════
def get_complaints():
    return run_query("""
        SELECT Complaint_ID, Title, Description, Status,
               Submitted_By, Admin_Note, Created_At
        FROM Complaints
        ORDER BY Created_At DESC
    """)


def get_complaints_for_user(username):
    return run_query("""
        SELECT Complaint_ID, Title, Description, Status,
               Admin_Note, Created_At
        FROM Complaints
        WHERE Submitted_By = %s
        ORDER BY Created_At DESC
    """, (username,))


def add_complaint(title, description, submitted_by):
    if not title or not description:
        return None, "Title and description are required."
    return run_query("""
        INSERT INTO Complaints (Title, Description, Submitted_By, Status)
        VALUES (%s, %s, %s, 'Open')
    """, (title, description, submitted_by), fetch=False)


def resolve_complaint(complaint_id, admin_note):
    return run_query("""
        UPDATE Complaints
        SET Status = 'Rectified', Admin_Note = %s
        WHERE Complaint_ID = %s
    """, (admin_note, complaint_id), fetch=False)


# ══════════════════════════════════════════════════════════
# AUDIT LOG  (Admin only)
# ══════════════════════════════════════════════════════════
def get_audit_log():
    return run_query("""
        SELECT Log_ID, Table_Name, Operation, Record_ID,
               Changed_By, Change_Time, Old_Value, New_Value
        FROM Audit_Log
        ORDER BY Change_Time DESC
        LIMIT 100
    """)


# ══════════════════════════════════════════════════════════
# GENERIC — used by chatbot for raw SQL execution
# ══════════════════════════════════════════════════════════
def run_raw_query(sql):
    return run_query(sql)