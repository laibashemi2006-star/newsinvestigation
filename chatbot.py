from groq import Groq
import pandas as pd
import streamlit as st
from database import get_conn, read_df
from db_schema import DB_SCHEMA

def _get_client():
    """Initialise Groq client using the API key stored in st.secrets."""
    api_key = st.secrets["groq"]["api_key"]
    return Groq(api_key=api_key)

def generate_sql(question, role):
    if role == "Viewer":
        restriction = "Only Story, Source, Location, Timeline_Event and their views. No Audit_Log, Users, Notes, Interviews."
    elif role == "Journalist":
        restriction = "All tables and views EXCEPT Users and Audit_Log."
    else:
        restriction = "All tables and views including Audit_Log and Users."

    prompt = f"""{DB_SCHEMA}
ROLE RESTRICTION: {restriction}
Convert to MySQL SELECT query: {question}
Return ONLY the SQL. No explanation. No markdown. No backticks."""

    client = _get_client()
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    sql = resp.choices[0].message.content.strip()
    return sql.replace("```sql", "").replace("```", "").strip()

def explain_results(question, df):
    if df is None or df.empty:
        return "No results found for your question."
    prompt = f"""A journalist asked: "{question}"
Results: {df.head(20).to_string(index=False)}
Write a concise plain English summary. No SQL terms."""
    client = _get_client()
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content.strip()

def ask_chatbot(question, role):
    sql = generate_sql(question, role)
    df, error = read_df(sql)
    if error:
        return {"sql": sql, "dataframe": None,
                "answer": f"Database error: {error}"}
    answer = explain_results(question, df)
    return {"sql": sql, "dataframe": df, "answer": answer}