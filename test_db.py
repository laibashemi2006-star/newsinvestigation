from database import get_conn, add_story, get_stories

# ── Test 1: Connection ──────────────────────────────────────
print("\n🔌 Testing connection...")
try:
    conn = get_conn()
    print("✅ Connected successfully!")
    conn.close()
except Exception as e:
    print(f"❌ Connection FAILED: {e}")
    exit()

# ── Test 2: Check tables exist ──────────────────────────────
print("\n📋 Checking tables...")
try:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    tables = [row[0] for row in cur.fetchall()]
    print(f"✅ Tables found: {tables}")
    conn.close()
except Exception as e:
    print(f"❌ Could not list tables: {e}")

# ── Test 3: Insert a story ──────────────────────────────────
print("\n➕ Inserting a test story...")
rows, error = add_story(
    "TEST STORY",
    "This is a test",
    "Crime",
    "2026-01-01",
    "Ongoing"
)
if error:
    print(f"❌ Insert FAILED: {error}")
else:
    print(f"✅ Insert worked! Rows affected: {rows}")

# ── Test 4: Read it back ────────────────────────────────────
print("\n📖 Reading stories back...")
df, error = get_stories()
if error:
    print(f"❌ Read FAILED: {error}")
elif df.empty:
    print("⚠️  Table is empty — insert may have failed silently")
else:
    print(f"✅ Found {len(df)} story/stories:")
    print(df[["Story_ID", "Title", "Status"]].to_string())