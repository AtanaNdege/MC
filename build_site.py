#!/usr/bin/env python3
"""Build mc-boychild.html with the client's real photos embedded as data URIs."""
import base64, io, json, os, re, urllib.request
from PIL import Image, ImageOps
from fontTools import subset

UPLOADS = os.path.expanduser("~/uploads")
TEMPLATE = os.path.expanduser("~/site_template.html")
OUT = os.path.expanduser("~/mc-boychild.html")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

# token -> source file; gallery order/captions come from expand_gallery.py via gallery_map.json
GAL_MAP = json.load(open(os.path.expanduser("~/gallery_map.json")))["order"]
PORTRAIT_SOURCE = "5.jpeg"  # orange African-print shirt, mic in hand (Choma Na Plate stage)

def jpeg_data_uri(path, quality=72, max_w=1024):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

# ---------- 1. Gallery data URIs (28 items, ALL uploaded photos) ----------
gals = {}
for i, item in enumerate(GAL_MAP, 1):
    gals[f"@@GAL{i}@@"] = jpeg_data_uri(os.path.join(UPLOADS, item["src"]), quality=70, max_w=880)
print("gallery data URIs:", len(gals), "items,", sum(len(v) for v in gals.values()) // 1024, "KB")

# ---------- 2. Portrait: 4:5 crop around the main subject ----------
im = ImageOps.exif_transpose(Image.open(os.path.join(UPLOADS, PORTRAIT_SOURCE))).convert("RGB")
W, H = im.size                     # 1066 x 1600 (portrait orientation)
cw = min(W, 900)                   # slight zoom-in on the subject
ch = round(cw * 5 / 4)
cx = 490                           # subject centered on x
face_y = 700                       # face line -> sit ~30% from crop top
left = max(0, min(cx - cw // 2, W - cw))
top = max(0, min(face_y - round(ch * 0.30), H - ch))
portrait = im.crop((left, top, left + cw, top + ch)).resize((560, 700), Image.LANCZOS)
buf = io.BytesIO()
portrait.save(buf, "JPEG", quality=80, optimize=True, progressive=True)
portrait_uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
portrait.save(os.path.expanduser("~/gallery/portrait.jpg"), "JPEG", quality=82, optimize=True)
print("portrait:", portrait.size, len(portrait_uri) // 1024, "KB")

# ---------- 3. Fonts ----------
FAMILIES = [
    ("FONT_ANTON", "family=Anton:wght@400"),
    ("FONT_WS400", "family=Work+Sans:wght@400"),
    ("FONT_WS500", "family=Work+Sans:wght@500"),
    ("FONT_WS600", "family=Work+Sans:wght@600"),
    ("FONT_WS700", "family=Work+Sans:wght@700"),
]

def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read()

fonts = {}
for key, fam in FAMILIES:
    css = fetch(f"https://fonts.googleapis.com/css2?{fam}&display=swap").decode()
    blocks = re.findall(r"/\* (\w[\w-]*) \*/\s*@font-face\s*{([^}]+)}", css)
    url = None
    for name, body in blocks:
        if name == "latin":
            m = re.search(r"url\((https://[^)]+\.woff2)\)", body)
            if m: url = m.group(1)
    if not url:
        m = re.search(r"url\((https://[^)]+\.woff2)\)", css)
        url = m.group(1)
    raw = fetch(url)
    opts = subset.Options()
    opts.hinting = True
    opts.desubroutinize = True
    opts.drop_tables += ["GSUB", "GPOS", "GDEF"]
    f = subset.load_font(io.BytesIO(raw), opts)
    ss = subset.Subsetter(options=opts)
    ss.populate(unicodes=list(range(0x20, 0x7F)) + [0xA0, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2026, 0x2192])
    ss.subset(f)
    buf = io.BytesIO()
    f.flavor = "woff2"
    f.save(buf)
    data = buf.getvalue()
    fonts[f"@@{key}@@"] = base64.b64encode(data).decode()  # template has the data: prefix
    print(key, len(data) // 1024, "KB")

# ---------- 4. Assemble ----------
html = open(TEMPLATE, encoding="utf-8").read()
for mapping in (gals, fonts, {"@@PORTRAIT@@": portrait_uri}):
    for k, v in mapping.items():
        html = html.replace(k, v)
leftover = re.findall(r"@@[A-Z0-9_]+@@", html)
if leftover:
    raise SystemExit(f"UNREPLACED TOKENS: {set(leftover)}")
open(OUT, "w", encoding="utf-8").write(html)
print(f"\nWrote {OUT}: {os.path.getsize(OUT)//1024} KB")
