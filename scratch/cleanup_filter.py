fp = r'd:/TMDT/core/templates/core/product/list.html'
with open(fp, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The redundant block starts with <style> and has /* ===== TIKI-STYLE FILTER ===== */
# It starts around line 1334 (0-indexed 1333)
# We want to keep everything up to the previous </script> (line 1332)
# And keep the final countdown script at the end.

# Find the start of the redundant block
redundant_start = None
for i, line in enumerate(lines):
    if '/* ===== TIKI-STYLE FILTER ===== */' in line:
        redundant_start = i - 1 # include the <style> line
        break

# Find the start of the countdown script near the end
countdown_start = None
for i in range(len(lines)-1, 0, -1):
    if '<script>' in lines[i] and 'document.addEventListener("DOMContentLoaded"' in lines[i+1]:
        countdown_start = i
        break

print(f"Redundant block start: {redundant_start}, Countdown start: {countdown_start}")

if redundant_start and countdown_start:
    new_content = lines[:redundant_start] + lines[countdown_start:]
    with open(fp, 'w', encoding='utf-8') as f:
        f.writelines(new_content)
    print(f"Cleanup done! Kept {len(new_content)} lines.")
else:
    print("Could not find markers for cleanup.")
