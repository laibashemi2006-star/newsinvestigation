import re

def refactor():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update Story Cards (Remove ring)
    content = re.sub(
        r'    filled = sum\(\[interviews>0, documents>0, notes>0, events>0, locations>0\]\)\n    pct    = int\(filled / 5 \* 100\)\n    ring   = progress_ring_svg\(pct, cat_color\)\n\n    st\.markdown\(f\"\"\"\n    <div class=\'intel-card\'>\n        <div class=\'intel-card-cat-strip\' style=\'background:\{cat_color\};\'><\/div>\n        <div class=\'intel-card-header\'>\n            <div class=\'intel-progress-ring\'>\{ring\}<\/div>',
        r'''    st.markdown(f"""
    <div class='intel-card'>
        <div class='intel-card-cat-strip' style='background:{cat_color};'></div>
        <div class='intel-card-header'>''',
        content
    )

    # 2. Sidebar pages
    sidebar_old = '''    if role == "Admin":
        pages = [("◈","Dashboard"),("🃏","Stories"),("👤","Sources"),
                 ("🎙️","Interviews"),("📄","Documents"),("📍","Locations"),
                 ("📝","Notes"),("📅","Timeline"),("👥","Users"),
                 ("📋","Audit Log"),("💬","Complaints"),("🤖","AI Chatbot")]
    elif role == "Journalist":
        pages = [("◈","Dashboard"),("🃏","Stories"),("👤","Sources"),
                 ("🎙️","Interviews"),("📄","Documents"),("📍","Locations"),
                 ("📝","Notes"),("📅","Timeline"),
                 ("💬","Complaints"),("🤖","AI Chatbot")]
    else:
        pages = [("◈","Dashboard"),("🃏","Stories"),("👤","Sources"),
                 ("📡","Live Feed"),("🤖","AI Chatbot")]

    for ico, p in pages:
        label = f"**{ico}  {p}**" if st.session_state.page == p else f"{ico}  {p}"
        if st.button(label, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p; st.rerun()'''

    sidebar_new = '''    if role == "Admin":
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("📡","Live Feed"),("🤖","AI Chatbot")]
    elif role == "Journalist":
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("📡","Live Feed"),("🤖","AI Chatbot")]
    else:
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("📡","Live Feed"),("🤖","AI Chatbot")]

    for ico, p in pages:
        if p == "AI Chatbot":
            # Highly highlighted and attractive button for AI Chatbot
            label = "✨ 🤖 AI Chatbot ✨"
            if st.button(label, key=f"nav_{p}", use_container_width=True, type="primary"):
                st.session_state.page = p; st.rerun()
        else:
            label = f"**{ico}  {p}**" if st.session_state.page == p else f"{ico}  {p}"
            if st.button(label, key=f"nav_{p}", use_container_width=True):
                st.session_state.page = p; st.rerun()'''

    content = content.replace(sidebar_old, sidebar_new)

    # 3. Replace all page == "Stories" and the rest with tabs
    # We will find the start of `elif page == "Stories":`
    start_str = '''# ══════════════════════════════════════════════════════════
# STORIES
# ══════════════════════════════════════════════════════════
elif page == "Stories":'''
    
    end_str = '''# ══════════════════════════════════════════════════════════
# LIVE FEED'''

    parts = content.split(start_str)
    if len(parts) == 2:
        before = parts[0]
        rest = start_str + parts[1]
        sections = rest.split(end_str)
        if len(sections) == 2:
            middle = sections[0]
            after = end_str + sections[1]
            
            # Now we process middle to wrap inside `elif page == "Data Tables":`
            new_middle = '''# ══════════════════════════════════════════════════════════
# DATA TABLES
# ══════════════════════════════════════════════════════════
elif page == "Data Tables":
    page_header("🗂️ Data Tables", "Manage all your records in one place")
    
    if ADMIN_ONLY:
        tab_names = ["Stories", "Sources", "Interviews", "Documents", "Locations", "Notes", "Timeline", "Users", "Audit Log", "Complaints"]
    elif role == "Journalist":
        tab_names = ["Stories", "Sources", "Interviews", "Documents", "Locations", "Notes", "Timeline", "Complaints"]
    else:
        tab_names = ["Stories", "Sources", "Complaints"]

    tabs = st.tabs(tab_names)
    
'''
            # We need to replace all `elif page == "XYZ":` with `if "XYZ" in tab_names:\n        with tabs[tab_names.index("XYZ")]:\n`
            
            blocks = re.split(r'# ══════════════════════════════════════════════════════════\n# (.*?)\n# ══════════════════════════════════════════════════════════\nelif page == "(.*?)":', middle)
            # blocks[0] is empty or just whitespace
            # blocks[1] is 'STORIES'
            # blocks[2] is 'Stories'
            # blocks[3] is the code block for Stories
            # blocks[4] is 'SOURCES' ...
            
            for i in range(1, len(blocks), 3):
                title_upper = blocks[i]
                page_name = blocks[i+1]
                code_block = blocks[i+2]
                
                # Indent code_block by 4 spaces
                indented_code = "\\n".join(["            " + line if line.strip() else "" for line in code_block.split("\\n")])
                
                new_middle += f"""    if "{page_name}" in tab_names:
        with tabs[tab_names.index("{page_name}")]:
            st.markdown("### {page_name}")
{indented_code}
"""
            
            content = before + new_middle + after

    # 4. Complaints UI - Resolved -> Rectified
    content = content.replace('badge-resolved', 'badge-rectified')
    content = content.replace('"Resolved"', '"Rectified"')
    content = content.replace("'Resolved'", "'Rectified'")
    content = content.replace('✅ Resolved', '✅ Rectified')
    content = content.replace('resolve_complaint', 'resolve_complaint') # DB func stays same but status is rectified
    content = content.replace('Resolve #', 'Rectify #')
    content = content.replace('Resolution note for', 'Reply / Rectification note for')

    # CSS for badge-rectified
    content = content.replace('.badge-resolved   { background: #e6f4eb; color: #2a7a40; }', '.badge-rectified   { background: #e6f4eb; color: #2a7a40; }')

    # Add user management UI logic
    # In the Users tab logic, let's insert the add user form
    # The users section is blocks[3] where page_name is Users
    # Let's find "page_header("👥 Users", "All system accounts")"
    users_old = '''            page_header("👥 Users", "All system accounts")
            df, _ = get_users()'''
    users_new = '''            page_header("👥 Users", "All system accounts")
            with st.expander("＋ Add New User"):
                with st.form("add_user_form", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    new_uname = c1.text_input("Username")
                    new_pwd = c2.text_input("Password", type="password")
                    new_fn = st.text_input("Full Name")
                    new_role = st.selectbox("Role", ["Admin", "Journalist", "Viewer"])
                    if st.form_submit_button("Create User"):
                        if new_uname and new_pwd and new_fn:
                            aff, err = add_user(new_uname, new_pwd, new_role, new_fn)
                            if err:
                                st.error(err)
                            else:
                                st.success("User created successfully!")
                                st.rerun()
                        else:
                            st.error("Please fill in all fields.")
            df, _ = get_users()'''
    content = content.replace(users_old, users_new)

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

refactor()
