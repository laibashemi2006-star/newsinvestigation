import re

def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the sidebar
    old_sidebar = '''    if role == "Admin":
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("📡","Live Feed"),("🤖","AI Chatbot")]
    elif role == "Journalist":
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("📡","Live Feed"),("🤖","AI Chatbot")]
    else:
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("📡","Live Feed"),("🤖","AI Chatbot")]'''

    new_sidebar = '''    if role == "Admin":
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("👥","Users"),("💬","Complaints"),("📡","Live Feed"),("🤖","AI Chatbot")]
    elif role == "Journalist":
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("💬","Complaints"),("📡","Live Feed"),("🤖","AI Chatbot")]
    else:
        pages = [("◈","Dashboard"),("🗂️","Data Tables"),("💬","Complaints"),("📡","Live Feed"),("🤖","AI Chatbot")]'''
    
    content = content.replace(old_sidebar, new_sidebar)

    # 2. Update tab_names in Data Tables
    old_tabs = '''    if ADMIN_ONLY:
        tab_names = ["Stories", "Sources", "Interviews", "Documents", "Locations", "Notes", "Timeline", "Users", "Audit Log", "Complaints"]
    elif role == "Journalist":
        tab_names = ["Stories", "Sources", "Interviews", "Documents", "Locations", "Notes", "Timeline", "Complaints"]
    else:
        tab_names = ["Stories", "Sources", "Complaints"]'''

    new_tabs = '''    if ADMIN_ONLY:
        tab_names = ["Stories", "Sources", "Interviews", "Documents", "Locations", "Notes", "Timeline"]
    elif role == "Journalist":
        tab_names = ["Stories", "Sources", "Interviews", "Documents", "Locations", "Notes", "Timeline"]
    else:
        tab_names = ["Stories", "Sources"]'''

    content = content.replace(old_tabs, new_tabs)

    # 3. Extract Users and Complaints, remove Audit Log
    # Using regex to find the blocks and outdent them
    
    # We will find `    if "Users" in tab_names:\n        with tabs[tab_names.index("Users")]:\n            st.markdown("### Users")`
    # and replace with `elif page == "Users":`
    # And then outdent the rest of the block until the next `    if "..." in tab_names:` or `elif page == "Live Feed":`
    
    lines = content.split('\\n')
    new_lines = []
    
    state = 'normal'
    
    for line in lines:
        if line.startswith('    if "Users" in tab_names:'):
            state = 'users'
            new_lines.append('# ══════════════════════════════════════════════════════════')
            new_lines.append('# USERS')
            new_lines.append('# ══════════════════════════════════════════════════════════')
            new_lines.append('elif page == "Users":')
            continue
            
        elif line.startswith('    if "Audit Log" in tab_names:'):
            state = 'audit_log'
            continue
            
        elif line.startswith('    if "Complaints" in tab_names:'):
            state = 'complaints'
            new_lines.append('# ══════════════════════════════════════════════════════════')
            new_lines.append('# COMPLAINTS')
            new_lines.append('# ══════════════════════════════════════════════════════════')
            new_lines.append('elif page == "Complaints":')
            continue
            
        elif line.startswith('elif page == "Live Feed":') or line.startswith('# ══════════════════════════════════════════════════════════') and 'LIVE FEED' in line:
            if 'LIVE FEED' in line:
                # wait, the comment for live feed might be what we hit first
                pass
            if line.startswith('elif page == "Live Feed":'):
                state = 'normal'
                # fallback, just in case
            
        if state == 'audit_log':
            # Skip all lines of audit log
            if line.startswith('elif page == "Live Feed":') or line.startswith('# ══════════════════════════════════════════════════════════') and 'LIVE FEED' in line:
                state = 'normal'
            elif line.startswith('    if "Complaints" in tab_names:'):
                state = 'complaints'
                new_lines.append('# ══════════════════════════════════════════════════════════')
                new_lines.append('# COMPLAINTS')
                new_lines.append('# ══════════════════════════════════════════════════════════')
                new_lines.append('elif page == "Complaints":')
                continue
            else:
                continue

        if state == 'users' or state == 'complaints':
            if line.startswith('        with tabs['):
                continue
            elif line.startswith('            st.markdown("###'):
                continue
            elif line.startswith('elif page == "Live Feed":'):
                state = 'normal'
                new_lines.append(line)
            elif line.startswith('# ══════════════════════════════════════════════════════════'):
                if 'LIVE FEED' in line:
                    pass # it's just the comment above it, let's keep state
                new_lines.append(line)
            else:
                # outdent by 8 spaces
                if line.startswith('            '):
                    new_lines.append(line[8:])
                elif line.startswith('        '): # e.g. blank lines or something
                    if line.strip() == '':
                        new_lines.append('')
                    else:
                        new_lines.append(line[8:])
                else:
                    new_lines.append(line)
        else:
            new_lines.append(line)
            
    content = '\\n'.join(new_lines)
    
    # AI Chatbot examples
    old_chatbot = '''    if user_input:
        with st.spinner("Analysing…"):'''

    new_chatbot = '''    # AI Chatbot Examples
    st.markdown("<div style='margin-bottom: 10px; color: #8a7560; font-size: 13px;'><b>Example Questions:</b></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("📊 Show all ongoing stories"): user_input = "Show all ongoing stories"
    if c2.button("👥 List high credibility sources"): user_input = "List high credibility sources"
    if c3.button("📅 Show recent timeline events"): user_input = "Show recent timeline events"

    if user_input:
        with st.spinner("Analysing…"):'''

    content = content.replace(old_chatbot, new_chatbot)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    main()
