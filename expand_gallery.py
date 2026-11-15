#!/usr/bin/env python3
"""Expand the gallery in site_template.html from 12 to 28 items (ALL uploaded photos).
Writes gallery_map.json consumed by build_site.py (single source of truth).
Note: 23.jpeg is byte-identical to 22.jpeg (md5) -> included once as GAL26."""
import json, os, re

TPL = os.path.expanduser("~/site_template.html")
MAP = os.path.expanduser("~/gallery_map.json")

# (source file, category, caption, alt) — gallery order for the "All" view
ORDER = [
    ("4.jpeg",  "festivals", "Hands Up — Open-Air Concert",            "MC Boychild raising his hands to a massive outdoor crowd"),
    ("8.jpeg",  "clubs",     "On the Decks with the DJ",               "MC Boychild performing alongside the DJ at the decks"),
    ("28.jpeg", "weddings",  "Hyping the Couple — Wedding Reception",  "MC Boychild on the mic beside the bride and groom during a wedding dance"),
    ("2.jpeg",  "festivals", "Live on Stage — Campus Takeover",        "MC Boychild performing on stage in front of a packed campus crowd"),
    ("5.jpeg",  "culture",   "Choma Na Plate — African Print Stage",   "MC Boychild in an orange African-print shirt hosting on stage"),
    ("20.jpeg", "weddings",  "Groom's Dance — Full House Reception",   "Groom in a white tuxedo dancing as MC Boychild hypes the reception"),
    ("9.jpeg",  "festivals", "Red Mic Energy — Massive Crowd",         "MC Boychild with a red microphone facing a huge open-air crowd"),
    ("11.jpeg", "clubs",     "DJ Booth Vibes — Blue Mic",              "MC Boychild smiling with a blue mic next to the DJ booth"),
    ("17.jpeg", "culture",   "Kitenge Dance — Cultural Celebration",   "MC Boychild dancing with women in blue and orange kitenge dresses"),
    ("1.jpeg",  "festivals", "Stage Hype — Campus Tour",               "MC Boychild hyping the crowd from the stage with fellow performers"),
    ("25.jpeg", "weddings",  "Grand Entrance — White Tux Moment",      "Groom making a grand entrance in a white tuxedo at the wedding"),
    ("12.jpeg", "festivals", "Main Stage — Big Screen Set",            "MC Boychild on the main stage in front of a big LED screen"),
    ("13.jpeg", "clubs",     "Hype Control — With the DJ",             "MC Boychild pointing the mic at the crowd beside the DJ"),
    ("24.jpeg", "weddings",  "Garden Wedding — Couple's Dance",        "MC Boychild hosting a couple's dance at a garden wedding"),
    ("6.jpeg",  "culture",   "On the Mic — Choma Na Plate",            "MC Boychild in an African-print shirt speaking on stage with a mic"),
    ("14.jpeg", "festivals", "Crowd Work — Up Close",                  "MC Boychild leaning into the crowd with a red microphone"),
    ("19.jpeg", "festivals", "Night Set — After Dark",                 "MC Boychild performing at night in a checkered jacket"),
    ("29.jpeg", "weddings",  "Wedding Bash — Packed House",            "MC Boychild hyping a packed wedding hall during the groom's entrance"),
    ("15.jpeg", "festivals", "Thousands Deep — Open-Air Crowd",        "A sea of fans at an open-air festival from the stage"),
    ("26.jpeg", "culture",   "Runway Host — Fashion Gala",             "MC Boychild hosting an indoor fashion runway gala"),
    ("7.jpeg",  "festivals", "Sea of Fans — Festival Grounds",         "Aerial view of a massive festival crowd among white tents"),
    ("21.jpeg", "weddings",  "Swahili Wedding Night — Grand Arrival",  "Bride's grand arrival at a Swahili wedding night celebration"),
    ("10.jpeg", "culture",   "Full Fit — Choma Na Plate Stage",        "MC Boychild in full African-print outfit holding the stage"),
    ("16.jpeg", "festivals", "LED Wall — Festival Mainset",            "MC Boychild on a festival stage beside a large LED wall"),
    ("18.jpeg", "culture",   "Dancing With the Aunties — Tradition",   "MC Boychild dancing with elders in traditional attire"),
    ("22.jpeg", "culture",   "Cultural Beats — Kitenge Session",       "MC Boychild on the mic during a kitenge dance session"),
    ("3.jpeg",  "festivals", "Open-Air Stage — Afternoon Set",         "Wide view of the open-air festival stage in the afternoon sun"),
    ("27.jpeg", "weddings",  "Groom Squad — Red Sash Entrance",        "Groomsmen in black suits with red sashes making a dance entrance"),
]

CATS = ["festivals", "clubs", "weddings", "culture"]
FILTERS = [
    ("all", "All"),
    ("festivals", "Campus &amp; Festivals"),
    ("clubs", "Clubs &amp; DJ"),
    ("weddings", "Weddings"),
    ("culture", "Culture &amp; Galas"),
]

SVG = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5M11 8v6M8 11h6"/></svg>'
DCLS = ["", " d1", " d2"]

def item_block(i, src, cat, cap, alt):
    d = DCLS[(i - 1) % 3]
    return (
        f'        <button class="gal-item reveal{d}" data-cat="{cat}" aria-label="View photo: {cap}">\n'
        f'          <figure>\n'
        f'            <img src="@@GAL{i}@@" alt="{alt}" loading="lazy" decoding="async">\n'
        f'            <figcaption><span>{cap}</span><span class="gal-zoom" aria-hidden="true">{SVG}</span></figcaption>\n'
        f'          </figure>\n'
        f'        </button>'
    )

filters_html = (
    '      <div class="gal-filters reveal" role="group" aria-label="Filter gallery">\n'
    + "\n".join(
        f'        <button class="gal-filter{" active" if key == "all" else ""}" data-filter="{key}">{label}</button>'
        for key, label in FILTERS
    )
    + "\n      </div>"
)

grid_html = '<div class="gal-grid" id="galGrid">\n' + "\n\n".join(
    item_block(i, *item) for i, item in enumerate(ORDER, 1)
) + '\n      </div>'

photos_js = (
    "  var PHOTOS = [\n"
    + ",\n".join(f'    {{ cap:"{cap}", cat:"{cat}" }}' for _, cat, cap, _ in ORDER)
    + "\n  ];"
)

html = open(TPL, encoding="utf-8").read()
orig = html

# 1. filter row (exact current block)
html = html.replace(
    '''      <div class="gal-filters reveal" role="group" aria-label="Filter gallery">
        <button class="gal-filter active" data-filter="all">All</button>
        <button class="gal-filter" data-filter="festivals">Campus &amp; Festivals</button>
        <button class="gal-filter" data-filter="clubs">Clubs &amp; DJ</button>
        <button class="gal-filter" data-filter="culture">Cultural &amp; Weddings</button>
      </div>''',
    filters_html, 1)

# 2. grid content: replace between <div class="gal-grid" id="galGrid"> and its closing </div>
html, n = re.subn(
    r'<div class="gal-grid" id="galGrid">.*?\n      </div>',
    lambda m: grid_html, html, count=1, flags=re.S)

# 3. PHOTOS array
html, n2 = re.subn(r'  var PHOTOS = \[.*?\n  \];', lambda m: photos_js, html, count=1, flags=re.S)

assert n == 1, f"grid replace count={n}"
assert n2 == 1, f"PHOTOS replace count={n2}"
assert "gal-filters" in html and filters_html in html, "filter row replace failed"

open(TPL, "w", encoding="utf-8").write(html)
json.dump({"order": [{"src": s, "cat": c, "cap": cp, "alt": a} for s, c, cp, a in ORDER]}, open(MAP, "w"), indent=1)

counts = {c: sum(1 for _, cc, _, _ in ORDER if cc == c) for c in CATS}
print(f"template updated: {len(ORDER)} items | per-cat counts: {counts} | total={sum(counts.values())}")
print(f"bytes: {len(orig)} -> {len(html)}")
