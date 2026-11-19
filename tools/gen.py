"""Generate portfolio-styled animated SVGs for the GitHub profile README."""
import base64, io, os, sys
from html import escape
from PIL import Image

SCR = os.path.dirname(os.path.abspath(__file__))
PHOTOS = "/Users/melinafathi/Desktop/Projects/Meellinaa.github.io/photos"
OUT = os.path.join(SCR, "..", "assets")
os.makedirs(OUT, exist_ok=True)

W = 1200
NAVY, MUTED, GOLD, GOLD2, BG2 = "#1a2a4a", "#6b7590", "#e8a500", "#fcd34d", "#f0f6ff"


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


FONTS = {k: b64(f"{SCR}/fonts/{k}.woff2") for k in ["sg700", "dm400", "dm500", "dm600"]}


def font_css(used):
    fam = {"sg700": ("SG", 700), "dm400": ("DM", 400), "dm500": ("DM", 500), "dm600": ("DM", 600)}
    out = []
    for k in used:
        f, w = fam[k]
        out.append(f"@font-face{{font-family:'{f}';font-weight:{w};src:url(data:font/woff2;base64,{FONTS[k]}) format('woff2');}}")
    return "".join(out)


def photo(name, width=1200, q=55):
    im = Image.open(f"{PHOTOS}/{name}").convert("RGB")
    h = int(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True)
    return base64.b64encode(buf.getvalue()).decode(), h


BASE_CSS = f"""
.sg{{font-family:'SG',sans-serif;font-weight:700}}
.dm{{font-family:'DM',sans-serif}}
.up{{text-transform:uppercase}}
@keyframes slideUp{{from{{transform:translateY(110%)}}to{{transform:translateY(0)}}}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
@keyframes grow{{from{{transform:scaleX(0)}}to{{transform:scaleX(1)}}}}
@keyframes shimmer{{from{{background-position:0%}}to{{background-position:200%}}}}
.fade{{opacity:0;animation:fadeUp .9s cubic-bezier(.16,1,.3,1) forwards}}
.grow{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:grow 1.2s cubic-bezier(.16,1,.3,1) forwards}}
"""


def svg(h, body, fonts=("sg700", "dm400", "dm500", "dm600"), extra_css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">'
            f'<style>{font_css(fonts)}{BASE_CSS}{extra_css}</style>{body}</svg>')


def bg_photo(name, h, overlay="rgba(255,255,255,.78)", radius=18, y_off=None):
    data, ph = photo(name)
    y = -(ph - h) // 2 if y_off is None else y_off
    return (f'<defs><clipPath id="r"><rect width="{W}" height="{h}" rx="{radius}"/></clipPath></defs>'
            f'<g clip-path="url(#r)"><image href="data:image/jpeg;base64,{data}" x="0" y="{y}" width="{W}" height="{ph}" preserveAspectRatio="xMidYMid slice"/>'
            f'<rect width="{W}" height="{h}" fill="{overlay}"/></g>')


def gold_grad():
    return (f'<defs><linearGradient id="gold" x1="0" x2="1"><stop offset="0" stop-color="{GOLD}"/>'
            f'<stop offset=".5" stop-color="{GOLD2}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient></defs>')


def sec_head(num, title, y, x=56):
    # "02  Skills ──────" like the portfolio
    tw = len(title) * 27 + 10
    return (f'<text x="{x}" y="{y}" class="sg up" font-size="13" letter-spacing="2.3" fill="{GOLD}">{num}</text>'
            f'<text x="{x+52}" y="{y+12}" class="sg" font-size="46" letter-spacing="-1.4" fill="{NAVY}">{escape(title)}</text>'
            f'<rect x="{x+52+tw+30}" y="{y-4}" width="{W-x-(x+52+tw+30)}" height="1" fill="rgba(0,0,0,.08)"/>'
            f'<rect class="grow" x="{x+52+tw+30}" y="{y-4}" width="{W-x-(x+52+tw+30)}" height="1.5" fill="url(#gold)" style="animation-delay:.3s"/>')


def save(name, content):
    p = f"{OUT}/{name}"
    open(p, "w").write(content)
    print(name, os.path.getsize(p) // 1024, "KB")


# ── HERO ────────────────────────────────────────────────────────────────
def hero():
    h = 560
    nav = (f'<text x="56" y="62" class="sg" font-size="16" letter-spacing="1.3" fill="{NAVY}">MF</text>'
           + "".join(f'<text x="{x}" y="62" class="dm up" font-weight="500" font-size="12" letter-spacing="1.7" fill="{MUTED}">{t}</text>'
                     for x, t in [(380, "About"), (480, "Work"), (568, "Skills"), (660, "Experience"), (800, "Contact")])
           + f'<rect x="1000" y="40" width="144" height="36" rx="18" fill="none" stroke="rgba(232,165,0,.5)" stroke-width="1.5"/>'
           f'<text x="1072" y="63" text-anchor="middle" class="dm up" font-weight="600" font-size="12" letter-spacing="1.5" fill="{GOLD}">Portfolio ↗</text>')
    tag = (f'<g class="fade" style="animation-delay:.1s"><rect x="56" y="172" width="36" height="1.2" fill="{GOLD}"/>'
           f'<text x="108" y="177" class="dm up" font-size="12" letter-spacing="2.6" fill="{MUTED}">CS Student · Entrepreneur · Western University</text></g>')
    name = ""
    for i, (word, base) in enumerate([("Melina", 290), ("Fathidashtaki", 392)]):
        name += (f'<defs><clipPath id="ln{i}"><rect x="0" y="{base-96}" width="{W}" height="122"/></clipPath></defs>'
                 f'<g clip-path="url(#ln{i})"><text x="50" y="{base}" class="sg" font-size="124" letter-spacing="-5" fill="{NAVY}" '
                 f'style="transform:translateY(110%);animation:slideUp .9s cubic-bezier(.16,1,.3,1) {0.15+i*0.1}s forwards">{word}</text></g>')
    sub = (f'<text x="56" y="448" class="dm fade" font-size="17" letter-spacing=".6" fill="{MUTED}" style="animation-delay:.6s">'
           f'Building at the intersection of code &amp; business.</text>')
    btns = (f'<g class="fade" style="animation-delay:.8s"><rect x="56" y="482" width="196" height="50" rx="25" fill="url(#gold)"/>'
            f'<text x="154" y="512" text-anchor="middle" class="dm up" font-weight="600" font-size="12.5" letter-spacing="1.6" fill="#fff">Selected Work →</text>'
            f'<text x="282" y="512" class="dm up" font-weight="500" font-size="12.5" letter-spacing="1.6" fill="{NAVY}">Portfolio ↗</text></g>'
            f'<g class="fade" style="animation-delay:1s"><rect x="1100" y="470" width="1" height="54" fill="rgba(26,42,74,.25)"/>'
            f'<text x="1112" y="510" class="dm up" font-size="11" letter-spacing="1.8" fill="{MUTED}">Scroll</text></g>')
    body = (gold_grad() + bg_photo("shell.jpg", h,
            overlay="url(#ov)", radius=18)
            .replace("<defs>", f'<defs><linearGradient id="ov" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="rgba(255,255,255,.72)"/>'
                     f'<stop offset=".45" stop-color="rgba(240,248,255,.45)"/><stop offset="1" stop-color="rgba(255,255,255,.72)"/></linearGradient>', 1)
            + nav + tag + name + sub + btns)
    save("hero.svg", svg(h, body))


# ── MARQUEE ─────────────────────────────────────────────────────────────
def marquee():
    items = ["Python", "Java", "C++", "SQL", "PyTorch", "Computer Vision", "ML Engineer", "Data Pipelines",
             "TD Scholar", "Co-Founder", "Event Organizer", "OCR", "MongoDB", "JavaFX", "Git"]
    x, parts = 0, []
    for rep in range(3):
        for it in items:
            parts.append(f'<text x="{x}" y="29" class="dm up" font-size="12" letter-spacing="2" fill="{MUTED}">{it}</text>')
            x += len(it) * 10.6 + 22
            parts.append(f'<text x="{x}" y="29" class="dm" font-size="12" fill="{GOLD}">·</text>')
            x += 30
        if rep == 0:
            span = x
    css = f"@keyframes tick{{from{{transform:translateX(0)}}to{{transform:translateX(-{span:.0f}px)}}}}.mq{{animation:tick 30s linear infinite}}"
    body = (f'<defs><clipPath id="c"><rect width="{W}" height="46" rx="10"/></clipPath></defs>'
            f'<g clip-path="url(#c)"><rect width="{W}" height="46" fill="{BG2}"/>'
            f'<rect width="{W}" height="1" fill="rgba(0,0,0,.08)"/><rect y="45" width="{W}" height="1" fill="rgba(0,0,0,.08)"/>'
            f'<g class="mq">{"".join(parts)}</g></g>')
    save("marquee.svg", svg(46, body, fonts=("dm400",), extra_css=css))


# ── ABOUT ───────────────────────────────────────────────────────────────
def about():
    h = 520
    lead = ["Building real products since year one.", "Not just learning — shipping."]
    para = ["I'm a Computer Science student at Western University who builds things",
            "that matter — from AI pipelines that classify skin tones to data systems",
            "driving real revenue. Selected as a TD Scholar (one of four university-wide),",
            "admitted to the Gifted Academic Program (18 of 5,000), and co-founded a",
            "company in my first year that grew 30% month-over-month."]
    body = gold_grad() + bg_photo("surfers.jpg", h, overlay="rgba(240,248,255,.80)") + sec_head("00", "About", 92)
    for i, l in enumerate(lead):
        body += f'<text x="56" y="{180+i*42}" class="sg fade" font-size="32" letter-spacing="-.8" fill="{NAVY}" style="animation-delay:{.2+i*.1}s">{escape(l)}</text>'
    for i, l in enumerate(para):
        body += f'<text x="56" y="{290+i*28}" class="dm fade" font-size="16.5" fill="{MUTED}" style="animation-delay:{.4+i*.05}s">{escape(l)}</text>'
    stats = [("250+", "Events organized"), ("500+", "Community members"), ("30%", "MoM revenue growth"), ("4th", "TD Scholar — university")]
    for i, (n, label) in enumerate(stats):
        x, y = 760 + (i % 2) * 210, 170 + (i // 2) * 150
        body += (f'<g class="fade" style="animation-delay:{.5+i*.12}s"><rect x="{x}" y="{y}" width="190" height="128" rx="10" fill="rgba(255,255,255,.75)" stroke="rgba(0,0,0,.06)"/>'
                 f'<text x="{x+22}" y="{y+66}" class="sg" font-size="44" letter-spacing="-1.5" fill="{GOLD}">{escape(n)}</text>'
                 f'<text x="{x+22}" y="{y+98}" class="dm up" font-size="10.5" letter-spacing="1.4" fill="{MUTED}">{escape(label)}</text></g>')
    save("about.svg", svg(h, body))


# ── WORK ────────────────────────────────────────────────────────────────
def work_head():
    h = 130
    body = gold_grad() + bg_photo("rays.jpg", h, overlay="rgba(255,255,255,.80)", y_off=-160) + sec_head("01", "Selected Work", 72)
    save("work.svg", svg(h, body, fonts=("sg700",)))


PROJECTS = [
    ("stemslice", "StemSlice", ["AI DJ engine that splits tracks into stems (vocals, drums, bass, melody)",
                                "and blends them into seamless, beatmatched transitions."], ["Python", "Demucs", "Librosa", "FastAPI"]),
    ("omniprep", "OmniPrep AI", ["Voice-driven mock interviews with live audio and vision telemetry and",
                                 "an automated STAR-method debrief. Built at Ignition Hacks."], ["Python", "ElevenLabs", "Computer Vision"]),
    ("grindtracker", "The Grind Tracker", ["Visual dashboard for job applications: statuses, deadlines, timelines",
                                           "and the tailored résumé for every role."], ["TypeScript", "React", "Tailwind"]),
    ("beauty", "AI Beauty Consultant", ["Matches foundation shades from a selfie and recommends skincare from",
                                        "Sephora product data, with a skincare chatbot."], ["Python", "OpenCV", "MediaPipe", "Streamlit"]),
    ("llmtester", "LLM Robustness Tester", ["Rewrites a prompt five ways and scores how consistent an LLM's",
                                            "answers are, with a similarity heatmap."], ["Python", "FastAPI", "NLP"]),
    ("spendpal", "SpendPal", ["OCR receipt scanner that sorts grocery items into categories and",
                              "tracks spending against a budget."], ["Python", "OCR", "MongoDB"]),
]


def work_rows():
    for i, (slug, title, desc, tags) in enumerate(PROJECTS, 1):
        h = 168
        body = (f'<rect width="{W}" height="{h}" rx="12" fill="#ffffff" stroke="rgba(0,0,0,.07)"/>'
                f'<text x="56" y="56" class="dm" font-size="12" letter-spacing="1.5" fill="{MUTED}">{i:02d}</text>'
                f'<text x="120" y="58" class="sg" font-size="27" letter-spacing="-.6" fill="{NAVY}">{escape(title)}</text>')
        for j, l in enumerate(desc):
            body += f'<text x="120" y="{90+j*23}" class="dm" font-size="15.5" fill="{MUTED}">{escape(l)}</text>'
        x = 120
        for t in tags:
            w = len(t) * 8.4 + 28
            body += (f'<rect x="{x}" y="{h-34}" width="{w:.0f}" height="22" rx="11" fill="rgba(232,165,0,.08)" stroke="rgba(232,165,0,.45)"/>'
                     f'<text x="{x+w/2:.0f}" y="{h-19}" text-anchor="middle" class="dm up" font-weight="600" font-size="10" letter-spacing="1.2" fill="{GOLD}">{escape(t)}</text>')
            x += w + 10
        body += f'<text x="1144" y="64" text-anchor="end" class="sg" font-size="22" fill="{GOLD}">↗</text>'
        save(f"p-{slug}.svg", svg(h, body, fonts=("sg700", "dm400", "dm600")))


# ── SKILLS ──────────────────────────────────────────────────────────────
def skills():
    cols = [("Languages", [("Python", 90), ("Java", 85), ("C++", 75), ("SQL", 80), ("HTML / CSS", 78), ("C", 65)]),
            ("ML & Data", [("PyTorch", 75), ("Computer Vision", 72), ("Pandas / NumPy", 85), ("Data Pipelines", 82), ("OCR", 70)]),
            ("Tools", [("Git / GitHub", 90), ("FastAPI", 75), ("React / TypeScript", 70), ("JavaFX / Maven", 80), ("MongoDB", 68), ("Unix / Linux", 75)])]
    h = 560
    body = gold_grad() + bg_photo("sharks.jpg", h, overlay="rgba(240,248,255,.82)") + sec_head("02", "Skills", 92)
    cw = (W - 112) / 3
    body += f'<rect x="56" y="140" width="{W-112}" height="380" rx="10" fill="rgba(255,255,255,.88)" stroke="rgba(0,0,0,.06)"/>'
    for c, (head, items) in enumerate(cols):
        x0 = 56 + c * cw + 36
        bw = cw - 72
        if c:
            body += f'<rect x="{56+c*cw:.0f}" y="140" width="1" height="380" fill="rgba(0,0,0,.07)"/>'
        body += f'<text x="{x0:.0f}" y="188" class="dm up" font-weight="600" font-size="11" letter-spacing="2" fill="{GOLD}">{escape(head)}</text>'
        for r, (name, pct) in enumerate(items):
            y = 236 + r * 47
            fw = bw * pct / 100
            d = .3 + c * .15 + r * .08
            body += (f'<text x="{x0:.0f}" y="{y}" class="dm" font-weight="500" font-size="14" fill="{NAVY}">{escape(name)}</text>'
                     f'<text x="{x0+bw:.0f}" y="{y}" text-anchor="end" class="dm" font-size="11" fill="{MUTED}">{pct}%</text>'
                     f'<rect x="{x0:.0f}" y="{y+11}" width="{bw:.0f}" height="2" rx="1" fill="rgba(26,42,74,.08)"/>'
                     f'<g class="grow" style="animation-delay:{d:.2f}s"><rect x="{x0:.0f}" y="{y+11}" width="{fw:.0f}" height="2" rx="1" fill="url(#gold)"/>'
                     f'<circle cx="{x0+fw:.0f}" cy="{y+12}" r="4" fill="{GOLD}"/></g>')
    save("skills.svg", svg(h, body))


# ── EXPERIENCE ──────────────────────────────────────────────────────────
def experience():
    jobs = [("Oct 2025 — Now", "Student Ambassador & Event Organizer", "Morrissette Institute for Entrepreneurship · Western University",
             ["Organized 250+ events attracting 500+ student founders & industry leaders",
              "Managed speaker recruitment, logistics, promotion & follow-up end-to-end"]),
            ("Sep 2025 — Now", "Co-Founder · Business Operations & Finance", "Gold Star Catering · Toronto, ON",
             ["Built Python & SQL data pipelines to analyze sales and expense data",
              "Identified pricing opportunities driving 30% month-over-month revenue growth"]),
            ("Nov 2024 — Now", "Instructor Assistant, Data Analytics", "Kumon Learning Centre · London, ON",
             ["Taught & mentored 100+ students weekly across math and reading",
              "Managed student records, achievement tracking & parent communication"])]
    h = 150 + len(jobs) * 150 + 50
    body = gold_grad() + bg_photo("palms.jpg", h, overlay="rgba(255,255,255,.84)") + sec_head("03", "Experience", 92)
    for i, (when, role, org, bullets) in enumerate(jobs):
        y = 160 + i * 150
        body += (f'<g class="fade" style="animation-delay:{.2+i*.15}s">'
                 f'<rect x="56" y="{y-10}" width="{W-112}" height="1" fill="rgba(0,0,0,.08)"/>'
                 f'<text x="56" y="{y+30}" class="dm up" font-size="11.5" letter-spacing="1.6" fill="{GOLD}">{escape(when)}</text>'
                 f'<text x="300" y="{y+32}" class="sg" font-size="23" letter-spacing="-.4" fill="{NAVY}">{escape(role)}</text>'
                 f'<text x="300" y="{y+58}" class="dm" font-size="14" fill="{MUTED}">{escape(org)}</text>')
        for j, b in enumerate(bullets):
            body += (f'<rect x="300" y="{y+80+j*26}" width="10" height="1.5" fill="{GOLD}"/>'
                     f'<text x="322" y="{y+86+j*26}" class="dm" font-size="14.5" fill="{NAVY}" fill-opacity=".82">{escape(b)}</text>')
        body += "</g>"
    save("experience.svg", svg(h, body))


# ── CONTACT ─────────────────────────────────────────────────────────────
def contact():
    h = 360
    body = gold_grad() + bg_photo("arch.jpg", h, overlay="rgba(240,248,255,.82)") + sec_head("04", "Contact", 92)
    body += (f'<text x="56" y="200" class="sg fade" font-size="64" letter-spacing="-2.4" fill="{NAVY}" style="animation-delay:.2s">Let\'s build something.</text>'
             f'<text x="58" y="244" class="dm fade" font-size="17" fill="{MUTED}" style="animation-delay:.35s">Open to internships, collaborations &amp; interesting problems.</text>')
    for i, (k, v) in enumerate([("Email", "melina3825@gmail.com ↗"), ("LinkedIn", "melina-f-53372b20a ↗"), ("GitHub", "@Meellinaa ↗")]):
        x = 56 + i * 370
        body += (f'<g class="fade" style="animation-delay:{.5+i*.1}s"><rect x="{x}" y="{h-36}" width="340" height="1" fill="rgba(0,0,0,.1)"/>'
                 f'<text x="{x}" y="{h-72}" class="dm up" font-size="11" letter-spacing="2" fill="{GOLD}">{k}</text>'
                 f'<text x="{x}" y="{h-48}" class="dm" font-weight="500" font-size="17" fill="{NAVY}">{escape(v)}</text></g>')
    save("contact.svg", svg(h, body))


for f in [hero, marquee, about, work_head, work_rows, skills, experience, contact]:
    f()
