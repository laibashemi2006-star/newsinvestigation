def fix_indent():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    in_tab = False
    
    for i, line in enumerate(lines):
        # We need to indent everything between:
        # `    if "Stories" in tab_names:` and `elif page == "Live Feed":`
        # But wait, there are multiple `if "..." in tab_names:` blocks.
        
        # Actually, any line between 660 and 1092 (roughly) that starts with 4 spaces needs to have 8 spaces added, EXCEPT if it's already properly indented for the `if` and `with` statements.
        
        # Let's detect `    if "..." in tab_names:`
        # When we hit that, we set a flag. But we also have the `with` statement immediately following it.
        pass

    # A better way is to read the file, and whenever we see `    if "XYZ" in tab_names:`, the next line is `        with tabs...`, the next line is `            st.markdown...`. The lines AFTER that until the next `    if "XYZ"` or `elif page` or `# ====` need to be indented by 8 spaces.

    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    
    # We will find all blocks starting with `    if "[Name]" in tab_names:\n        with tabs[tab_names.index("[Name]")]:\n            st.markdown("### [Name]")`
    # and indent the content that follows until the next block or `    if "..."`
    
    # Let's just use string replacement or line by line
    
    new_lines = []
    indent_next = False
    for line in lines:
        if re.match(r'^    if ".*?" in tab_names:$', line):
            indent_next = True
            new_lines.append(line)
        elif line.startswith('        with tabs['):
            new_lines.append(line)
        elif line.startswith('            st.markdown("### '):
            new_lines.append(line)
        elif line.startswith('elif page == "Live Feed":') or line.startswith('# ══════════════════════════════════════════════════════════'):
            if 'LIVE FEED' in line or 'AI CHATBOT' in line or line.startswith('elif page'):
                if line.startswith('elif page'):
                    indent_next = False
            new_lines.append(line)
        else:
            if indent_next and line.startswith('    ') and not line.startswith('        '):
                # it has exactly 4 spaces (or maybe more but we want to add 8 spaces to whatever it has)
                # wait, if it's `    page_header(...)`, we want to add 8 spaces to make it 12 spaces.
                # Just add 8 spaces to every line that has at least some content, or just blindly add 8 spaces.
                if line.strip() == '':
                    new_lines.append(line)
                else:
                    # Strip the first 4 spaces and add 12 spaces
                    if line.startswith('    '):
                        new_lines.append('        ' + line)
                    else:
                        new_lines.append('            ' + line)
            else:
                if indent_next and line.strip() != '':
                    if line.startswith('    '):
                        new_lines.append('        ' + line)
                    else:
                        new_lines.append('            ' + line)
                else:
                    new_lines.append(line)
            
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    fix_indent()
