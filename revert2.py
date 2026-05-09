import re

def process():
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # We need to completely replace the Users, Audit Log, and Complaints section
    
    start_users = '    if "Users" in tab_names:'
    end_live_feed = 'elif page == "Live Feed":'
    
    parts = content.split(start_users)
    if len(parts) == 2:
        before = parts[0]
        rest = start_users + parts[1]
        
        sections = rest.split(end_live_feed)
        if len(sections) == 2:
            middle = sections[0]
            after = end_live_feed + sections[1]
            
            # Now we reconstruct middle. We know it has Users, Audit Log, Complaints
            
            # We want to extract the code inside Users
            # The structure is:
            #     if "Users" in tab_names:
            #         with tabs[...]:
            #             st.markdown("### Users")
            #             ... code ...
            
            # Since we can just write the Users block and Complaints block manually to be sure it's perfect:
            users_block = """
# ══════════════════════════════════════════════════════════
# USERS
# ══════════════════════════════════════════════════════════
elif page == "Users":
    if not ADMIN_ONLY: st.warning("Admins only."); st.stop()
    page_header("👥 Users", "All system accounts")
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
    df, _ = get_users()
    if df is None or df.empty:
        st.info("No users found.")
    else:
        cols = st.columns(4)
        for i, row in enumerate(df.itertuples()):
            d        = row._asdict()
            role_val = str(d.get("Role",""))
            badge    = f"badge-{role_val.lower()}"
            initials = "".join(w[0].upper() for w in str(d.get("Full_Name","")).split()[:2])
            with cols[i % 4]:
                st.markdown(f'''
                <div class='source-card'>
                    <div class='source-card-top'>
                        <div class='source-avatar'
                        style='background:linear-gradient(135deg,#b8763a,#d4944e);color:white;font-size:16px;'>
                            {initials}
                        </div>
                        <div>
                            <div class='source-name'>{d.get("Full_Name","")}</div>
                            <div class='source-type'>@{d.get("Username","")}</div>
                        </div>
                    </div>
                    <span class='badge {badge}'>{role_val}</span>
                    <div style='font-size:11px;color:#8a7560;margin-top:8px;'>
                        Joined {str(d.get("Created_At",""))[:10]}
                    </div>
                </div>''', unsafe_allow_html=True)
"""
            complaints_block = """
# ══════════════════════════════════════════════════════════
# COMPLAINTS
# ══════════════════════════════════════════════════════════
elif page == "Complaints":
    page_header("💬 Complaints")
    if ADMIN_ONLY:
        st.markdown('<div class="page-sub">Review and rectify journalist complaints</div>', unsafe_allow_html=True)
        df, _ = get_complaints()
        if df is not None and not df.empty:
            open_df = df[df["Status"]=="Open"]
            res_df  = df[df["Status"]=="Rectified"]
            c1,c2,c3 = st.columns(3)
            for col,(ico,val,lbl,clr) in zip([c1,c2,c3],[
                ("🔴",len(open_df),"Open","#b02020"),
                ("✅",len(res_df),"Rectified","#2a7a40"),
                ("📋",len(df),"Total","#b8763a"),
            ]):
                with col:
                    st.markdown(f'''<div class='stat-card' style='--card-color:{clr}'>
                        <span class='stat-icon'>{ico}</span>
                        <span class='stat-number'>{val}</span>
                        <span class='stat-label'>{lbl}</span>
                    </div>''', unsafe_allow_html=True)
            st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
            if not open_df.empty:
                st.markdown("<div style='font-weight:700;color:#b02020;margin-bottom:10px;'>🔴 Open (" + str(len(open_df)) + ")</div>", unsafe_allow_html=True)
                for row in open_df.itertuples():
                    st.markdown(f'''
                    <div class='complaint-card'>
                        <b style='color:#2c2010;font-size:15px;'>{row.Title}</b>
                        <span class='badge badge-open' style='margin-left:10px;'>Open</span><br>
                        <small style='color:#8a7560;'>By {row.Submitted_By} · {str(row.Created_At)[:16]}</small>
                        <p style='margin:10px 0 0;font-size:14px;color:#2c2010;line-height:1.5;'>{row.Description}</p>
                    </div>''', unsafe_allow_html=True)
                    note = st.text_input(f"Reply / Rectification note for #{row.Complaint_ID}", key=f"rn_{row.Complaint_ID}")
                    if st.button(f"✓ Rectify #{row.Complaint_ID}", key=f"res_{row.Complaint_ID}"):
                        n,e = resolve_complaint(row.Complaint_ID, note)
                        if e: err(e)
                        else: ok("Rectified!"); st.rerun()
            if not res_df.empty:
                st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
                st.markdown("<div style='font-weight:700;color:#2a7a40;margin-bottom:10px;'>✅ Rectified (" + str(len(res_df)) + ")</div>", unsafe_allow_html=True)
                for row in res_df.itertuples():
                    admin_note = getattr(row,"Admin_Note",None)
                    note_html = f'<div style="margin-top:8px;padding:8px;background:#e6f4eb;border-radius:8px;font-size:12px;color:#2a7a40;"><b>Note:</b> {admin_note}</div>' if admin_note else ""
                    st.markdown(f'''
                    <div class='complaint-card' style='border-left-color:#2a7a40;'>
                        <b style='color:#2c2010;'>{row.Title}</b>
                        <span class='badge badge-rectified' style='margin-left:10px;'>Rectified</span><br>
                        <small style='color:#8a7560;'>By {row.Submitted_By}</small>
                        <p style='margin:8px 0 4px;font-size:13px;color:#2c2010;'>{row.Description}</p>
                        {note_html}
                    </div>''', unsafe_allow_html=True)
        else:
            st.info("No complaints yet.")
    else:
        st.markdown('<div class="page-sub">Submit issues or feedback to administrators</div>', unsafe_allow_html=True)
        with st.expander("＋  Submit New Complaint"):
            ct = st.text_input("Title", key="c_t")
            cd = st.text_area("Description", key="c_d")
            if st.button("Submit", key="c_sub"):
                n,e = add_complaint(ct,cd,uname)
                if e: err(e)
                else: ok("Submitted!"); st.rerun()
        df, _ = get_complaints_for_user(uname)
        if df is not None and not df.empty:
            for row in df.itertuples():
                badge_cls = "badge-rectified" if row.Status=="Rectified" else "badge-open"
                admin_note = getattr(row,"Admin_Note",None)
                note_html = f"<div style='margin-top:8px;padding:8px;background:#e6f4eb;border-radius:8px;font-size:12px;color:#2a7a40;'><b>Admin note:</b> {admin_note}</div>" if admin_note else ""
                st.markdown(f'''
                <div class='complaint-card'>
                    <b>{row.Title}</b>
                    <span class='badge {badge_cls}' style='margin-left:8px;'>{row.Status}</span><br>
                    <small style='color:#8a7560;'>{str(row.Created_At)[:16]}</small>
                    <p style='margin:8px 0;font-size:13px;'>{row.Description}</p>
                    {note_html}
                </div>''', unsafe_allow_html=True)
        else:
            st.info("No complaints submitted yet.")
"""
            new_middle = users_block + "\\n" + complaints_block + "\\n"
            content = before + new_middle + after

    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    process()
