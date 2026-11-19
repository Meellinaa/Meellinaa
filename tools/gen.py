"""Generate the animated SVG images used in the GitHub profile README.

Run:  python3 tools/gen.py      (writes everything into ../img)
Edit the PROJECTS / SKILLS / JOBS lists below to change the content.
"""
import base64, io, os, textwrap
from html import escape
from PIL import Image

SCR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SCR, "..", "img")
os.makedirs(OUT, exist_ok=True)

W = 1200
NAVY, MUTED = "#1a2a4a", "#5d6680"
ACC = "#a8875a"            # warm latte: readable accent for small text
CREAM_A, CREAM_B = "#ecdcbc", "#faf3e3"   # cream gradient for fills
PAPER = "#fbf7f0"          # cream panel background
LINE = "rgba(168,135,90,.28)"


# ── helpers ──────────────────────────────────────────────────────────────
def b64file(path):
    return base64.b64encode(open(path, "rb").read()).decode()


FONTS = {k: b64file(f"{SCR}/fonts/{k}.woff2") for k in ["sg700", "dm400", "dm500", "dm600"]}
FONT_CSS = "".join(
    f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{FONTS[k]}) format('woff2');}}"
    for k, fam, w in [("sg700", "SG", 700), ("dm400", "DM", 400), ("dm500", "DM", 500), ("dm600", "DM", 600)])

CSS = f"""{FONT_CSS}
.sg{{font-family:'SG',sans-serif;font-weight:700}}
.dm{{font-family:'DM',sans-serif}}
.up{{text-transform:uppercase}}
@keyframes slideUp{{from{{transform:translateY(115%)}}to{{transform:none}}}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
.fade{{opacity:0;animation:fadeUp 1s cubic-bezier(.16,1,.3,1) forwards}}
.grow{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow 1.4s cubic-bezier(.16,1,.3,1) forwards}}
"""

_photo_cache = {}


def photo(name, width):
    key = (name, width)
    if key not in _photo_cache:
        im = Image.open(os.path.join(SCR, "photos", name)).convert("RGB")
        h = int(im.height * width / im.width)
        im = im.resize((width, h), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=60, optimize=True)
        _photo_cache[key] = (base64.b64encode(buf.getvalue()).decode(), h)
    return _photo_cache[key]


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<style>{CSS}</style>'
            f'<defs><linearGradient id="cream" x1="0" x2="1"><stop offset="0" stop-color="{CREAM_A}"/>'
            f'<stop offset=".5" stop-color="{CREAM_B}"/><stop offset="1" stop-color="{CREAM_A}"/></linearGradient></defs>'
            f'{body}</svg>')


def panel(w, h, photo_name=None, overlay=None, img_w=None, x=0, y=0, radius=22, cid="p"):
    """Rounded panel: cream paper, optionally a photo under a tinted overlay."""
    out = f'<defs><clipPath id="{cid}"><rect width="{w}" height="{h}" rx="{radius}"/></clipPath></defs><g clip-path="url(#{cid})">'
    out += f'<rect width="{w}" height="{h}" fill="{PAPER}"/>'
    if photo_name:
        data, ph = photo(photo_name, img_w or w)
        out += f'<image href="data:image/jpeg;base64,{data}" x="{x}" y="{y}" width="{img_w or w}" height="{ph}"/>'
        out += f'<rect width="{w}" height="{h}" fill="{overlay}"/>'
    return out + "</g>"


def section_title(num, title, y, x=64, size=54, right=W - 64):
    tw = len(title) * size * 0.56
    rule_x = x + 58 + tw + 32
    return (f'<text x="{x}" y="{y}" class="sg" font-size="20" letter-spacing="2" fill="{ACC}">{num}</text>'
            f'<text x="{x+58}" y="{y+14}" class="sg" font-size="{size}" letter-spacing="-1.6" fill="{NAVY}">{escape(title)}</text>'
            f'<rect x="{rule_x:.0f}" y="{y-6}" width="{right-rule_x:.0f}" height="1.5" fill="{LINE}"/>'
            f'<rect class="grow" x="{rule_x:.0f}" y="{y-6}" width="{right-rule_x:.0f}" height="2" fill="{ACC}" style="animation-delay:.3s"/>')


def pill(x, y, text, size=17, weight=500, fill="rgba(255,255,255,.75)", color=NAVY, pad=20, h=None, upper=False, ls=0):
    h = h or size * 2.1
    w = len(text) * size * (0.62 if upper else 0.54) + pad * 2 + len(text) * ls
    cls = "dm up" if upper else "dm"
    return (f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{h/2:.0f}" fill="{fill}" stroke="{LINE}" stroke-width="1.5"/>'
            f'<text x="{x+w/2:.0f}" y="{y+h/2+size*0.36:.0f}" text-anchor="middle" class="{cls}" font-weight="{weight}" '
            f'font-size="{size}" letter-spacing="{ls}" fill="{color}">{escape(text)}</text>'), w


def save(name, content):
    path = os.path.join(OUT, name)
    open(path, "w").write(content)
    print(f"{name:22} {os.path.getsize(path)//1024:4} KB")


# ── content ─────────────────────────────────────────────────────────────
PROJECTS = [
    ("stemslice", "StemSlice", "AI DJ engine that splits songs into vocals, drums, bass and melody, then blends them into seamless, beatmatched transitions.", ["Python", "Demucs", "Librosa", "FastAPI"]),
    ("omniprep", "OmniPrep AI", "Voice-driven mock interviews with live audio and vision feedback and an automatic STAR-method debrief. Built at Ignition Hacks.", ["Python", "ElevenLabs", "Vision"]),
    ("grindtracker", "The Grind Tracker", "A visual job-hunt dashboard: application stages, deadlines, timelines and the tailored résumé for every role.", ["TypeScript", "React", "Tailwind"]),
    ("beauty", "AI Beauty Consultant", "Finds your foundation shade from a selfie and recommends skincare from real Sephora product data.", ["Python", "OpenCV", "MediaPipe"]),
    ("llmtester", "LLM Robustness Tester", "Rewrites a prompt five ways and scores how consistent an LLM's answers are, with a similarity heatmap.", ["Python", "FastAPI", "NLP"]),
    ("spendpal", "SpendPal", "Scans grocery receipts with OCR, sorts every item into a category and tracks spending against a budget.", ["Python", "OCR", "MongoDB"]),
]
# (photo, vertical offset of the photo inside the card's top strip), in PROJECTS order
CARD_PHOTOS = [("conch.jpg", -95), ("sparkle-water.jpg", -330), ("golden-wave.jpg", -330),
               ("pearl-shell.jpg", -260), ("arches.jpg", -115), ("roses-fountain.jpg", -215)]

SKILLS = [
    ("Languages", ["Python", "Java", "C++", "SQL", "TypeScript", "C", "R"]),
    ("ML & Data", ["PyTorch", "OpenCV", "MediaPipe", "pandas", "NumPy", "OCR"]),
    ("Tools", ["Git", "FastAPI", "React", "Qt", "JavaFX", "MongoDB", "Linux"]),
    ("Business", ["Financial modeling", "Project management", "Event operations"]),
]

JOBS = [
    ("Oct 2025 — Now", "Student Ambassador & Event Organizer", "Morrissette Institute for Entrepreneurship · Western University",
     ["Organized 250+ events for 500+ student founders and industry leaders",
      "Ran speaker recruitment, logistics and promotion end-to-end"]),
    ("Sep 2025 — Now", "Co-Founder · Operations & Finance", "Gold Star Catering · Toronto, ON",
     ["Built Python & SQL pipelines to analyze sales and expense data",
      "Found pricing wins that drove 30% month-over-month revenue growth"]),
    ("Nov 2024 — Now", "Instructor Assistant, Data Analytics", "Kumon Learning Centre · London, ON",
     ["Mentor 100+ students weekly across math and reading",
      "Track student records and achievement data"]),
]


# ── sections ────────────────────────────────────────────────────────────
def hero():
    h = 620
    ov = (f'<defs><linearGradient id="hov" x1="0" x2="1"><stop offset="0" stop-color="rgba(251,247,240,.93)"/>'
          f'<stop offset=".5" stop-color="rgba(251,247,240,.66)"/><stop offset="1" stop-color="rgba(251,247,240,.12)"/></linearGradient></defs>')
    body = ov + panel(W, h, "white-shell.jpg", "url(#hov)", img_w=1200, x=0, y=-80, cid="hero")
    body += (f'<text x="64" y="84" class="sg" font-size="22" letter-spacing="2" fill="{NAVY}">MF</text>')
    p, pw = pill(0, 0, "Open to internships", size=15, weight=600, upper=True, ls=1.5, fill="rgba(255,255,255,.7)", color=ACC)
    body += f'<g transform="translate({W-64-pw:.0f},56)">{p}</g>'
    body += (f'<g class="fade" style="animation-delay:.1s"><rect x="64" y="178" width="44" height="2" fill="{ACC}"/>'
             f'<text x="124" y="186" class="dm up" font-weight="600" font-size="17" letter-spacing="3.5" fill="{ACC}">Computer Science · Western University</text></g>')
    for i, (word, base) in enumerate([("Melina", 312), ("Fathidashtaki", 430)]):
        body += (f'<defs><clipPath id="ln{i}"><rect x="0" y="{base-110}" width="{W}" height="140"/></clipPath></defs>'
                 f'<g clip-path="url(#ln{i})"><text x="58" y="{base}" class="sg" font-size="136" letter-spacing="-6" fill="{NAVY}" '
                 f'style="transform:translateY(115%);animation:slideUp 1s cubic-bezier(.16,1,.3,1) {0.2+i*0.12}s forwards">{word}</text></g>')
    body += (f'<text x="64" y="496" class="dm fade" font-size="27" fill="{MUTED}" style="animation-delay:.6s">'
             f'Building at the intersection of code &amp; business.</text>')
    x = 64
    chips = ""
    for t in ["TD Scholar", "Co-founder, Gold Star Catering", "AI · Data · Full-stack"]:
        p, pw = pill(x, 532, t, size=18, weight=500)
        chips += p
        x += pw + 12
    body += f'<g class="fade" style="animation-delay:.85s">{chips}</g>'
    save("hero.svg", svg(W, h, body))


def marquee():
    items = ["Python", "Java", "C++", "SQL", "PyTorch", "Computer Vision", "Machine Learning", "Data Pipelines",
             "TD Scholar", "Co-Founder", "Event Organizer", "OCR", "MongoDB", "React", "Git"]
    x, parts, span = 0, [], 0
    for rep in range(3):
        for it in items:
            parts.append(f'<text x="{x:.0f}" y="38" class="dm up" font-weight="500" font-size="17" letter-spacing="3" fill="{NAVY}" fill-opacity=".72">{it}</text>')
            x += len(it) * 13.2 + 26
            parts.append(f'<text x="{x:.0f}" y="38" class="sg" font-size="30" fill="{ACC}">·</text>')
            x += 44
        if rep == 0:
            span = x
    css = f"<style>@keyframes tick{{to{{transform:translateX(-{span:.0f}px)}}}}.mq{{animation:tick 40s linear infinite}}</style>"
    body = (css + f'<defs><clipPath id="m"><rect width="{W}" height="60" rx="30"/></clipPath></defs>'
            f'<g clip-path="url(#m)"><rect width="{W}" height="60" fill="url(#cream)"/><g class="mq">{"".join(parts)}</g></g>')
    save("marquee.svg", svg(W, 60, body))


def about():
    h = 660
    body = panel(W, h, "sparkle-water.jpg", "rgba(251,247,240,.72)", y=-470, cid="ab")
    body += section_title("00", "About", 96)
    for i, l in enumerate(["Building real products since year one.", "Not just learning — shipping."]):
        body += f'<text x="64" y="{200+i*52}" class="sg fade" font-size="42" letter-spacing="-1.2" fill="{NAVY}" style="animation-delay:{.2+i*.1}s">{escape(l)}</text>'
    para = ("I'm a Computer Science student at Western University who builds things that matter — "
            "from AI pipelines that classify skin tones to data systems driving real revenue. "
            "I believe the best engineers also understand business.")
    for i, l in enumerate(textwrap.wrap(para, 78)):
        body += f'<text x="64" y="{318+i*36}" class="dm fade" font-size="23" fill="{NAVY}" fill-opacity=".78" style="animation-delay:{.4+i*.05}s">{escape(l)}</text>'
    stats = [("250+", "Events organized"), ("500+", "Community members"), ("30%", "MoM revenue growth"), ("1 of 4", "TD Scholars at Western")]
    cw = (W - 128 - 3 * 20) / 4
    for i, (n, label) in enumerate(stats):
        x = 64 + i * (cw + 20)
        body += (f'<g class="fade" style="animation-delay:{.6+i*.1}s"><rect x="{x:.0f}" y="470" width="{cw:.0f}" height="140" rx="16" fill="rgba(255,255,255,.82)" stroke="{LINE}" stroke-width="1.5"/>'
                 f'<text x="{x+28:.0f}" y="548" class="sg" font-size="54" letter-spacing="-2" fill="{ACC}">{escape(n)}</text>'
                 f'<text x="{x+28:.0f}" y="585" class="dm up" font-weight="600" font-size="14" letter-spacing="1.6" fill="{MUTED}">{escape(label)}</text></g>')
    save("about.svg", svg(W, h, body))


def work_title():
    h = 130
    body = panel(W, h, cid="wt") + section_title("01", "Selected Work", 74)
    save("work.svg", svg(W, h, body))


def cards():
    # Each image is half the page width (600 of 1200). The card itself is 584 wide and sits
    # against the outer edge, so two side by side leave an even 32-unit gutter in the middle.
    full, gutter, ch, band = 600, 16, 470, 170
    cw = full - gutter
    for i, ((slug, title, desc, tags), (ph, yo)) in enumerate(zip(PROJECTS, CARD_PHOTOS), 1):
        ox = 0 if i % 2 else gutter
        data, phh = photo(ph, cw)
        body = (f'<defs><clipPath id="c"><rect width="{cw}" height="{ch}" rx="22"/></clipPath>'
                f'<linearGradient id="bo" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgba(26,42,74,.05)"/>'
                f'<stop offset="1" stop-color="rgba(26,42,74,.45)"/></linearGradient></defs>'
                f'<g clip-path="url(#c)"><rect width="{cw}" height="{ch}" fill="{PAPER}"/>'
                f'<image href="data:image/jpeg;base64,{data}" x="0" y="{yo}" width="{cw}" height="{phh}"/>'
                f'<rect width="{cw}" height="{band}" fill="url(#bo)"/>'
                f'<rect y="{band}" width="{cw}" height="{ch-band}" fill="{PAPER}"/></g>'
                f'<rect x=".75" y=".75" width="{cw-1.5}" height="{ch-1.5}" rx="22" fill="none" stroke="{LINE}" stroke-width="1.5"/>'
                f'<text x="34" y="{band-26}" class="sg" font-size="52" letter-spacing="-1" fill="#ffffff">{i:02d}</text>'
                f'<circle cx="{cw-50}" cy="50" r="24" fill="rgba(255,255,255,.85)"/>'
                f'<text x="{cw-50}" y="58" text-anchor="middle" class="sg" font-size="22" fill="{NAVY}">↗</text>'
                f'<text x="34" y="{band+62}" class="sg" font-size="36" letter-spacing="-1" fill="{NAVY}">{escape(title)}</text>')
        for j, l in enumerate(textwrap.wrap(desc, 47)[:3]):
            body += f'<text x="34" y="{band+106+j*31}" class="dm" font-size="21" fill="{MUTED}">{escape(l)}</text>'
        x = 34
        for t in tags:
            p, pw = pill(x, ch - 64, t, size=14, weight=600, upper=True, ls=1.2, fill="rgba(236,220,188,.35)", color=ACC, pad=16, h=34)
            body += p
            x += pw + 10
        save(f"p-{slug}.svg", svg(full, ch, f'<g transform="translate({ox},0)">{body}</g>'))


def skills():
    h = 150 + len(SKILLS) * 82 + 30
    body = panel(W, h, "palms.jpg", "rgba(251,247,240,.84)", y=-520, cid="sk") + section_title("02", "Skills", 96)
    for r, (label, items) in enumerate(SKILLS):
        y = 160 + r * 82
        d = .2 + r * .12
        body += (f'<g class="fade" style="animation-delay:{d:.2f}s">'
                 f'<text x="64" y="{y+33}" class="dm up" font-weight="600" font-size="16" letter-spacing="2.4" fill="{ACC}">{escape(label)}</text>')
        x = 290
        for it in items:
            p, pw = pill(x, y, it, size=20, weight=500, fill="#ffffff", h=50, pad=22)
            body += p
            x += pw + 12
        body += "</g>"
        if r < len(SKILLS) - 1:
            body += f'<rect x="64" y="{y+66}" width="{W-128}" height="1" fill="{LINE}"/>'
    save("skills.svg", svg(W, h, body))


def experience():
    step = 190
    h = 160 + len(JOBS) * step + 10
    body = panel(W, h, "golden-wave.jpg", "rgba(251,247,240,.88)", y=-250, cid="ex") + section_title("03", "Experience", 96)
    for i, (when, role, org, bullets) in enumerate(JOBS):
        y = 170 + i * step
        body += (f'<g class="fade" style="animation-delay:{.2+i*.15}s">'
                 f'<rect x="64" y="{y-14}" width="{W-128}" height="1.5" fill="{LINE}"/>'
                 f'<text x="64" y="{y+36}" class="dm up" font-weight="600" font-size="16" letter-spacing="2" fill="{ACC}">{escape(when)}</text>'
                 f'<text x="330" y="{y+38}" class="sg" font-size="32" letter-spacing="-.8" fill="{NAVY}">{escape(role)}</text>'
                 f'<text x="330" y="{y+72}" class="dm" font-size="20" fill="{MUTED}">{escape(org)}</text>')
        for j, b in enumerate(bullets):
            body += (f'<circle cx="338" cy="{y+107+j*32}" r="4" fill="{ACC}"/>'
                     f'<text x="356" y="{y+114+j*32}" class="dm" font-size="20.5" fill="{NAVY}" fill-opacity=".85">{escape(b)}</text>')
        body += "</g>"
    save("experience.svg", svg(W, h, body))


def contact():
    h = 480
    body = panel(W, h, "golden-wave.jpg", "rgba(251,247,240,.55)", y=-640, cid="ct") + section_title("04", "Contact", 96)
    body += (f'<text x="60" y="230" class="sg fade" font-size="80" letter-spacing="-3" fill="{NAVY}" style="animation-delay:.2s">Let\'s build something.</text>'
             f'<text x="64" y="282" class="dm fade" font-size="25" fill="{NAVY}" fill-opacity=".8" style="animation-delay:.35s">Open to internships, collaborations &amp; interesting problems.</text>')
    for i, (k, v) in enumerate([("Email", "melina3825@gmail.com"), ("LinkedIn", "melina-f-53372b20a"), ("GitHub", "@Meellinaa")]):
        x = 64 + i * 370
        body += (f'<g class="fade" style="animation-delay:{.5+i*.1}s"><rect x="{x}" y="{h-48}" width="330" height="1.5" fill="{NAVY}" fill-opacity=".25"/>'
                 f'<text x="{x}" y="{h-104}" class="dm up" font-weight="600" font-size="15" letter-spacing="2.4" fill="{NAVY}" fill-opacity=".7">{k}</text>'
                 f'<text x="{x}" y="{h-68}" class="dm" font-weight="500" font-size="23" fill="{NAVY}">{escape(v)} ↗</text></g>')
    save("contact.svg", svg(W, h, body))


if __name__ == "__main__":
    for old in os.listdir(OUT):
        if old.endswith(".svg"):
            os.remove(os.path.join(OUT, old))
    for f in [hero, marquee, about, work_title, cards, skills, experience, contact]:
        f()
