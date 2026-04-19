import re

HTML_FILE = "core/templates/core/product/list.html"
CSS_FILE = "static/css/style.css"

with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

extractions = [
    ("fs-header", 'style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #D10024; padding-bottom: 10px; margin-bottom: 30px;"'),
    ("fs-wrapper", 'style="display: flex; align-items: center; flex-wrap: wrap; gap: 20px;"'),
    ("fs-title", 'style="margin: 0; color: #D10024; font-size: 26px; font-weight: 700;"'),
    ("fs-timer", 'style="margin: 0; padding: 0; display: flex; gap: 10px; list-style: none; align-items: center;"'),
    ("fs-timer-val", 'style="font-size: 14px; margin-bottom: 0;"'),
    ("fs-timer-unit", 'style="font-size: 10px;"'),
    ("fs-link", 'style="font-weight:600; color:#d10024; font-size: 14px;"'),
    
    ("pg-hd-header", 'style="margin-bottom: 20px;"'),
    ("pg-hd-title", 'style="color: #D10024; font-size: 28px;"'),
    ("pg-hd-timer", 'style="margin-bottom: 30px; display: flex; gap: 15px; justify-content: center; padding: 0; list-style: none;"'),
    
    ("cat-img", 'style="height: 250px; object-fit: cover;"'),
    
    ("hd-empty-box", 'style="max-width: 420px; margin: 0 auto;"'),
    ("hd-empty-body", 'style="padding: 30px; text-align: center;"'),
    ("hd-empty-desc", 'style="margin-top: 10px; color: #666;"'),
    ("hd-empty-btn", 'style="margin-top: 15px; display: inline-block;"'),
    
    ("sugg-title", 'style="color: #D10024; font-size: 24px;"'),
    ("sugg-more", 'style="margin-top: 20px;"'),
    
    ("inline-form", 'style="display:inline;"'),
    ("btn-bare", 'style="border:none; background:none;"'),
    ("mr-2px", 'style="margin-right: 2px;"')
]

new_css_rules = []

for cls, style_str in extractions:
    # Build CSS
    rules = style_str.replace('style="', '').rstrip('"')
    new_css_rules.append(f".{cls} {{\n    {rules.replace('; ', ';\n    ')}\n}}")
    
    # Process HTML to inject class
    # Find all instances of this exact style string. We don't use simple replace, we want to merge it into class=""
    while style_str in html:
        # Find the tag that contains this style
        # E.g. <div class="section-title" style="...">
        idx = html.find(style_str)
        # Find start of tag `<`
        tag_start = html.rfind('<', 0, idx)
        tag_end = html.find('>', idx)
        
        full_tag = html[tag_start:tag_end+1]
        
        # Check if class="" exists in full_tag
        if 'class="' in full_tag:
            # Inject cls into class=" existing "
            new_tag = re.sub(r'class="([^"]*)"', r'class="\1 ' + cls + '"', full_tag)
            # Remove style string from new_tag
            new_tag = new_tag.replace(style_str, '').replace('  ', ' ')
        else:
            # Add class="cls" and remove style
            new_tag = full_tag.replace(style_str, f'class="{cls}"').replace('  ', ' ')
            
        html = html[:tag_start] + new_tag + html[tag_end+1:]

# Write updated HTML
with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(html)

# Append CSS
with open(CSS_FILE, "a", encoding="utf-8") as f:
    f.write("\n\n/* CUSTOM INJECTED CSS FOR HOME UI */\n")
    f.write("\n\n".join(new_css_rules))

print("Successfully decoupled CSS into style.css!")
