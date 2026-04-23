"""
Surgically removes orphaned HTML fragments from pse_service.py.
Orphan 1: lines 451-512 (0-indexed 450-511) - leftover hr-hard HTML
Orphan 2: in the ceo-hard region - leftover old ceo-hard HTML body
"""
with open("pse_service.py", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines before: {len(lines)}")

# --- Orphan 1: lines 451-512 (1-indexed) ---
# These are raw HTML rows that start with <tr> and end with </html>""", 
# sitting between the new hr-hard entry (ending at line 446) and 
# the CEO section comment (line 514).
# Remove lines 451 to 512 (inclusive, 1-indexed → 0-indexed 450..511)
del lines[450:512]

print(f"Total lines after orphan1 removal: {len(lines)}")

# --- Orphan 2: old ceo-hard body ---
# After orphan1 removal, find the old ceo-hard body by looking for a unique marker
content = "".join(lines)

# The old ceo-hard body starts just after the new ceo-hard template ends (after """,\n    },)
# and before the closing } of TEMPLATES.
# We look for the old pattern between tpl-ceo-hard and the aliases section.

# Find the new ceo-hard template's end (the new body ends with our new html)
new_ceo_end_marker = '© 2025 NexaCore Systems · CR No. 1010XXXXXX · Riyadh, Saudi Arabia</p>\n      </td></tr>\n    </table>\n  </td></tr>\n</table>\n<img src="{pixel_url}" width="1" height="1" style="display:none;" />\n</body>\n</html>""",\n    },\n'
old_ceo_start_marker = '<html lang="en">\n<head>\n  <meta charset="UTF-8">\n\n  <table width="100%"'

idx_new_end = content.find('CR No. 1010XXXXXX')
idx_old_start = content.find('<html lang="en">\n<head>\n  <meta charset="UTF-8">\n\n  <table width="100%"')

print(f"New CEO end at char: {idx_new_end}")
print(f"Old CEO orphan start at char: {idx_old_start}")

if idx_old_start > idx_new_end and idx_old_start > -1:
    # Find end of this orphan - it ends before the aliases section
    aliases_marker = "# Add backward compatibility aliases"
    idx_aliases = content.find(aliases_marker, idx_old_start)
    
    # Get line numbers
    line_old_start = content[:idx_old_start].count("\n")  # 0-indexed
    line_aliases = content[:idx_aliases].count("\n")  # 0-indexed
    
    print(f"Old CEO orphan lines (0-indexed): {line_old_start} to {line_aliases - 1}")
    
    # The orphan ends with:  </html>""",\n    },\n}\n
    # Just before the aliases. We want to keep "}\n\n" (end of TEMPLATES dict).
    # Find exactly where the orphan's closing }, is
    orphan_close = content.rfind('    },\n}\n', idx_old_start, idx_aliases)
    if orphan_close == -1:
        orphan_close = content.rfind('    },\n}\n\n', idx_old_start, idx_aliases)
    
    line_orphan_close = content[:orphan_close].count("\n")  # 0-indexed
    print(f"Orphan closes at line (0-indexed): {line_orphan_close}")
    
    # Remove from old_start line to line_orphan_close (keep the },\n}\n part)
    del lines[line_old_start:line_orphan_close]
    print(f"Total lines after orphan2 removal: {len(lines)}")
else:
    print("Old CEO orphan not found - may already be clean")

with open("pse_service.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Done. File written.")
