import os
with open("core/templates/core/product/list.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

# The Flash Sale block (including KET THUC HOTDEAL) starts at line 349 (index 348) and ends at line 429 (index 428)
# The Categories block starts at line 431 (index 430) and ends at line 460 (index 459)

# A robust search:
flash_start, flash_end, cat_start, cat_end = -1, -1, -1, -1

for i, line in enumerate(lines):
    if '<h3 class="title" style="margin: 0; color: #D10024; font-size: 26px; font-weight: 700;">⚡ FLASH SALE</h3>' in line:
        flash_start = i - 6  # Back to <div class="section">
    if '<!-- KẾT THÚC HOTDEAL -->' in line:
        flash_end = i
    if '<!-- SITE: DANH MỤC SẢN PHẨM (Mới thêm) -->' in line:
        cat_start = i
    if '<!-- KẾT THÚC DANH MỤC SẢN PHẨM -->' in line:
        cat_end = i

print("Found coords:", flash_start, flash_end, cat_start, cat_end)

if flash_start != -1 and flash_end != -1 and cat_start != -1 and cat_end != -1:
    flash_block = lines[flash_start:flash_end+1]
    cat_block = lines[cat_start:cat_end+1]
    
    # Swap:
    # 0 to flash_start-1
    # cat_block
    # newline separating them
    # flash_block
    # cat_end+1 to end
    
    new_lines = lines[:flash_start] + cat_block + ["\n"] + flash_block + ["\n"] + lines[cat_end+1:]
    
    with open("core/templates/core/product/list.html", "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Swapped successfully!")
else:
    print("Missing coordinates!")

