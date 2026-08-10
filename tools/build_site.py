# -*- coding: utf-8 -*-
"""WPBRC modern site generator (v2) — official logo + palette, dev tracker, new pages."""
import html, json, os, re, glob

OUT=os.environ.get("SITE_OUT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJ_COUNT=len([p for p in json.load(open(OUT+"/assets/projects.json"))["projects"] if p.get("approved")!=False])
BASE="https://wpbrc.org"
ORG="West Palm Beach Residents Coalition"
TAGLINE="Stronger Neighborhoods. Stronger Community."

# Freely-licensed West Palm Beach photos (Wikimedia Commons, served via stable Special:FilePath)
FP="https://commons.wikimedia.org/wiki/Special:FilePath/"
IMG_SKYLINE="assets/hero-skyline.jpg"
IMG_CITYHALL="assets/hero-waterfront.jpg"
IMG_CITYPLACE="assets/hero-rooftops.jpg"
CRED_SKYLINE='WPBRC'
CRED_CITYHALL='WPBRC'
CRED_CITYPLACE='WPBRC'

def photo_band(src,alt,caption,credit):
    return f'''
<section class="section" style="padding-top:0">
  <div class="container">
    <figure class="photo-band">
      <img src="{src}" alt="{html.escape(alt)}" loading="lazy" width="2000" height="900">
      <span class="credit">Photo: {credit}</span>
      <figcaption>{caption}</figcaption>
    </figure>
  </div>
</section>'''

ASKS_HTML = """
<section class="section">
  <div class="container">
    <div class="section-head"><p class="eyebrow gold">What we&rsquo;re asking for</p><h2>Five reasonable requests</h2>
      <p class="lead">Constructive, non-partisan requests from neighborhood residents about how the city plans and decides &mdash; centered on the Downtown Master Plan and long-term growth.</p></div>
    <div class="grid grid-4">
      <div class="card feature"><h3>1 &middot; Time for review</h3><p>Allow time for mobility and infrastructure questions to be answered before the Downtown Master Plan is finalized.</p></div>
      <div class="card feature"><h3>2 &middot; Neighborhood representation</h3><p>Support a workshop to explore creating a Residential Planning Advisory Board (RPAB).</p></div>
      <div class="card feature"><h3>3 &middot; Coordinated mobility planning</h3><p>Align long-term planning with the County Transportation Master Plan and regional mobility studies.</p></div>
      <div class="card feature"><h3>4 &middot; Real transparency</h3><p>A public development dashboard, hearing calendar, infrastructure tracking, and study updates.</p></div>
    </div>
    <div class="grid" style="grid-template-columns:1fr;margin-top:1.5rem">
      <div class="card feature"><h3>5 &middot; A formal path for ongoing input</h3><p>Neighborhoods should be engaged early &mdash; not after decisions are largely made.</p></div>
    </div>
    <div class="split" style="margin-top:2rem">
      <div class="callout"><h3 class="mt-0">What we are <em>not</em> asking for</h3><p class="mb-0">We are <strong>not</strong> anti-growth, not anti-development, not seeking veto power, and not seeking to replace existing boards.</p></div>
      <div class="callout" style="border-left-color:var(--teal)"><h3 class="mt-0">What we <em>are</em> seeking</h3><p class="mb-0">Clarity, transparency, coordination, and meaningful resident participation in the decisions that shape our city.</p></div>
    </div>
  </div>
</section>
<section class="section navy">
  <div class="container" style="max-width:860px">
    <p class="eyebrow" style="color:var(--gold)">Our long-term vision</p>
    <h2>A permanent voice. A stronger city.</h2>
    <p class="lead">We&rsquo;re working toward a permanent structure for neighborhood representation in West Palm Beach &mdash; including a <strong>Residential Planning Advisory Board</strong>, a dedicated neighborhood liaison, neighborhood-informed planning, and a permanent seat at the table.</p>
  </div>
</section>
"""

# ---- Zeffy (free nonprofit platform) embeds + Formspree contact ----
# Replace these placeholder URLs with your real Zeffy form URLs after creating each form in Zeffy.
ZEFFY={
  "membership":"https://www.zeffy.com/embed/REPLACE-WITH-MEMBERSHIP-FORM-ID",
  "donation":"https://www.zeffy.com/en-US/embed/donation-form/donate-to-shape-our-citys-future",
  "newsletter":"https://www.zeffy.com/en-US/embed/newsletter-form/sign-up-for-our-newsletter-3752",
}
ZEFFY_DONATE_LINK="https://www.zeffy.com/en-US/donation-form/donate-to-shape-our-citys-future"
FORMSPREE="https://formsubmit.co/info@wpbrc.org"  # routes contact submissions to info@wpbrc.org

def zeffy_embed(url,title,height=900):
    return f'''<div class="embed-wrap" style="--embed-h:{height}px">
      <iframe class="zeffy" title="{html.escape(title)}" src="{url}" allow="payment" allowtransparency="true" loading="lazy"></iframe>
    </div>
    <p class="note" style="margin-top:.8rem">Secure form powered by <a href="https://www.zeffy.com" rel="noopener">Zeffy</a> &mdash; 100% of your contribution reaches the Coalition (Zeffy charges no fees). If the form doesn&rsquo;t load, <a href="{url}">open it in a new tab</a>.</p>'''

# ---- Site settings + custom pages (CMS-editable navigation & pages) ----
def _load_json(rel, default):
    p=os.path.join(OUT, rel)
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return default

def _parse_frontmatter(raw):
    """Minimal front-matter parser (no external deps). Returns (dict, body)."""
    fm={}; body=raw
    if raw.startswith("---"):
        end=raw.find("\n---", 3)
        if end!=-1:
            head=raw[3:end].strip("\n"); body=raw[end+4:].lstrip("\n")
            for line in head.splitlines():
                if ":" not in line: continue
                k,v=line.split(":",1); k=k.strip(); v=v.strip()
                if v.lower() in ("true","false"): v=(v.lower()=="true")
                elif re.fullmatch(r"-?\d+", v): v=int(v)
                else: v=v.strip().strip('"').strip("'")
                fm[k]=v
    return fm, body

def _load_custom_pages():
    pages=[]
    for fp in sorted(glob.glob(os.path.join(OUT,"content","pages","*.md"))):
        fm, body=_parse_frontmatter(open(fp, encoding="utf-8").read())
        slug=str(fm.get("slug") or os.path.splitext(os.path.basename(fp))[0])
        if not slug.endswith(".html"): slug+=".html"
        fm["slug"]=slug; fm["body"]=body
        pages.append(fm)
    return pages

SETTINGS=_load_json("content/settings.json", {"nav":[],"join":{"label":"Join","url":"contact.html"}})
CUSTOM_PAGES=_load_custom_pages()
_navcore=[(n["url"], n["label"], n.get("order",999)) for n in SETTINGS.get("nav",[]) if n.get("show",True)]
_navcustom=[(p["slug"], (p.get("nav_label") or p.get("title","Page")), int(p.get("nav_order",500))) for p in CUSTOM_PAGES if p.get("in_nav")]
NAV=[(u,l) for (u,l,o) in sorted(_navcore+_navcustom, key=lambda x:x[2])]
JOIN=SETTINGS.get("join",{"label":"Join","url":"contact.html"})
HOME=_load_json("content/home.json", {})
ABOUT=_load_json("content/about.json", {})

def _apply_text(s, pairs):
    for anchor, val in pairs:
        if val: s = s.replace(anchor, val, 1)
    return s

def render_md(body):
    b=(body or "").strip()
    if b.startswith("<"): return body
    try:
        import markdown; return markdown.markdown(body, extensions=["extra"])
    except Exception:
        return "".join("<p>"+para.strip().replace("\n","<br>")+"</p>" for para in b.split("\n\n") if para.strip())

def _strip(s): return re.sub("<[^>]+>","",s).strip()

def head(title,desc,slug,extra=""):
    canon=f"{BASE}/{slug}" if slug else f"{BASE}/"
    bodycls=(slug.split(".")[0] or "home")
    org={"@context":"https://schema.org","@type":"NGO","@id":f"{BASE}/#org","name":ORG,
      "alternateName":"WPBRC","slogan":TAGLINE,"url":BASE,"logo":f"{BASE}/assets/wpbrc-logo.png",
      "description":"A citywide, non-partisan 501(c)(4) coalition giving West Palm Beach residents a coordinated voice on growth, development, infrastructure, resilience, transparency, and quality of life.",
      "areaServed":{"@type":"City","name":"West Palm Beach","address":{"@type":"PostalAddress","addressLocality":"West Palm Beach","addressRegion":"FL","addressCountry":"US"}}}
    web={"@context":"https://schema.org","@type":"WebSite","@id":f"{BASE}/#website","url":BASE,"name":ORG,"publisher":{"@id":f"{BASE}/#org"}}
    _crumb=title.split("|")[0].strip()
    crumb={"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":_crumb,"item":canon}]}
    blocks=(f'<script type="application/ld+json">{json.dumps(org)}</script>\n'
            f'<script type="application/ld+json">{json.dumps(web)}</script>\n'
            f'<script type="application/ld+json">{json.dumps(crumb)}</script>\n')
    if extra: blocks+=extra+"\n"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{ORG}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/assets/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="index,follow">
<link rel="icon" href="assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/styles.css?v=13">
{blocks}</head>
<body class="page-{bodycls}">
<a class="skip-link" href="#main">Skip to content</a>'''

def header(active):
    li=[]
    for href,label in NAV:
        cls=' class="active"' if href==active else ""
        attr=' data-donate' if href=="donate.html" else ""
        li.append(f'<li><a href="{href}"{cls}{attr}>{label}</a></li>')
    li.append(f'<li><a href="{JOIN.get("url","contact.html")}" class="btn btn-primary">{JOIN.get("label","Join")}</a></li>')
    return f'''
<header class="site-header">
  <nav class="nav" aria-label="Primary">
    <a class="brand" href="index.html">
      <img src="assets/wpbrc-logo.png" alt="West Palm Beach Residents Coalition logo">
      <span class="bt">WPBRC<span>Stronger Neighborhoods</span></span>
    </a>
    <button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false">&#9776;</button>
    <ul class="nav-links">{''.join(li)}</ul>
  </nav>
</header>'''

def hero(eyebrow,h1,p,actions="",small=False,tagline=True,bg=None):
    cls="hero hero-sm" if small else "hero"
    if bg: cls+=" has-photo"
    style=f' style="--hero-img:url(\'{bg}\')"' if bg else ''
    tag=f'<p class="tagline">{TAGLINE}</p>' if tagline else ''
    return f'''
<section class="{cls}"{style}>
  <div class="container">
    {tag}
    <p class="eyebrow" style="color:var(--gold)">{eyebrow}</p>
    <h1>{h1}</h1>
    <p>{p}</p>
    {actions}
  </div>
</section>'''

FOOT=f'''
<footer class="site-footer">
  <div class="container">
    <div class="foot-grid">
      <div>
        <div class="foot-brand"><img src="assets/wpbrc-logo.png" alt="{ORG} logo"></div>
        <p style="margin-top:1rem">A citywide, non-partisan voice for the residents and stakeholders of West Palm Beach. <em>{TAGLINE}</em></p>
        <p class="disclaimer">Organized under Section 501(c)(4) of the Internal Revenue Code. We do not endorse or oppose candidates for public office.</p>
      </div>
      <div><h4>Explore</h4><ul class="foot-list">
        <li><a href="about.html">About</a></li><li><a href="development.html">Development Tracker</a></li>
        <li><a href="neighborhoods.html">Neighborhoods</a></li><li><a href="resources.html">Resources</a></li><li><a href="board.html">Board</a></li><li><a href="blog.html">Blog</a></li></ul></div>
      <div><h4>Get involved</h4><ul class="foot-list">
        <li><a href="join.html">Join</a></li><li><a href="donate.html">Donate &amp; Sponsor</a></li>
        <li><a href="events.html">Calendar</a></li><li><a href="contact.html">Contact</a></li></ul></div>
      <div><h4>Stay informed</h4><ul class="foot-list">
        <li><a href="events.html#newsletter">Newsletter</a></li><li><a href="development.html">What&rsquo;s being built</a></li>
        <li><a href="contact.html">Raise an issue</a></li></ul></div>
    </div>
    <div class="foot-bottom"><span>&copy; 2026 {ORG}.</span><span>West Palm Beach, Florida</span></div>
  </div>
</footer>
<div id="donate-modal" class="modal" hidden aria-hidden="true" role="dialog" aria-modal="true" aria-labelledby="donate-modal-title">
  <div class="modal-backdrop" data-donate-close></div>
  <div class="modal-card" role="document">
    <button class="modal-close" type="button" aria-label="Close" data-donate-close>&times;</button>
    <p class="eyebrow gold" style="margin-bottom:.3rem">Support the Coalition</p>
    <h3 id="donate-modal-title" class="mt-0">Help Fund Independent Traffic, Mobility &amp; Infrastructure Analysis</h3>
    <div class="embed-wrap" style="--embed-h:620px">
      <iframe class="zeffy" title="WPBRC donation form" src="https://www.zeffy.com/en-US/embed/donation-form/donate-to-shape-our-citys-future" allow="payment" allowtransparency="true" loading="lazy"></iframe>
    </div>
    <p class="note" style="margin-top:.6rem">100% of your contribution reaches the Coalition (Zeffy charges no fees). Prefer a full page? <a href="donate.html">Open the donation page</a>.</p>
  </div>
</div>
<script src="assets/site.js"></script>'''

def faq(items):
    rows="\n".join(f'    <details><summary>{html.escape(q)}</summary><div class="ans">{a}</div></details>' for q,a in items)
    ld={"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":_strip(a)}} for q,a in items]}
    return f'<div class="faq">\n{rows}\n  </div>', f'<script type="application/ld+json">{json.dumps(ld)}</script>'

def speakable(selectors=("h1",".lead")):
    ld={"@context":"https://schema.org","@type":"WebPage",
        "speakable":{"@type":"SpeakableSpecification","cssSelector":list(selectors)}}
    return f'<script type="application/ld+json">{json.dumps(ld)}</script>'

def write(slug,c):
    open(os.path.join(OUT,slug),"w",encoding="utf-8").write(c); print("wrote",slug)

# ---------------- HOME ----------------
hfaq,hfaq_ld=faq([
 ("What is the West Palm Beach Residents Coalition?","The West Palm Beach Residents Coalition (WPBRC) is a citywide, non-partisan 501(c)(4) social-welfare organization that gives residents and stakeholders a coordinated voice on issues affecting the whole city &mdash; growth and development, infrastructure, resilience, transparency, public safety, mobility, and waterfront planning."),
 ("Is the Coalition affiliated with a political party or candidate?","No. The Coalition is non-partisan and does not endorse or oppose candidates for public office. It focuses on public issues, policies, and processes."),
 ("How is it different from my neighborhood association?","The Coalition complements neighborhood associations rather than replacing them, focusing on broader issues that affect multiple neighborhoods across West Palm Beach."),
 ("How can I get involved?","You can join as a member, attend public meetings and events, follow the development tracker, donate, or contact the Coalition to raise a citywide issue."),
])
s=head(f"{ORG} | Citywide Voice",
 "A citywide, non-partisan 501(c)(4) giving West Palm Beach residents a coordinated voice on growth, development, infrastructure, resilience, transparency, and quality of life.",
 "",extra=hfaq_ld)
s+=header("index.html")
s+='''
<div class="banner">New &middot; Track every major development project across the city &mdash; <a href="development.html">open the interactive map &rsaquo;</a></div>
<main id="main">'''
s+=hero("The central information hub for West Palm Beach residents","Shaping the future of West Palm Beach, together.",
 "A citywide, non-partisan coalition of residents, property owners, and neighborhood leaders &mdash; organizing the information our city needs and working across district lines on the issues that affect every part of it.",
 '<div class="actions"><a href="https://www.zeffy.com/en-US/donation-form/donate-to-shape-our-citys-future" target="_blank" rel="noopener" class="btn btn-primary btn-lg">Donate Now</a><a href="development.html" class="btn btn-ghost light btn-lg">See what&rsquo;s being built</a></div>',bg=IMG_SKYLINE)
s+=f'''
<section class="section">
  <div class="container split">
    <div>
      <p class="eyebrow">Who we are</p>
      <h2>A citywide alliance of neighborhood leaders.</h2>
      <p class="lead">The West Palm Beach Residents Coalition is a citywide alliance of neighborhood leaders working together to ensure West Palm Beach grows thoughtfully, responsibly, and with residents at the table.</p>
      <p>We believe the strongest communities are built through collaboration, transparency, and informed decision-making. By bringing neighborhoods together under one coordinated, constructive voice, we can help create practical, long-term solutions that benefit everyone who lives, works, and invests in our city.</p>
      <a href="about.html" class="btn btn-secondary">Our mission &amp; priorities</a>
    </div>
    <div class="callout">
      <h3 class="mt-0">What we are &mdash; and aren&rsquo;t</h3>
      <p>We are a <strong>non-partisan</strong> social-welfare coalition. We <strong>do not</strong> endorse political candidates, and we don&rsquo;t take on single-neighborhood disputes unless they carry citywide significance.</p>
      <p class="mb-0 note">Organized under Section 501(c)(4) of the Internal Revenue Code.</p>
    </div>
  </div>
</section>

<section class="section navy">
  <div class="container" style="max-width:880px">
    <p class="eyebrow" style="color:var(--gold)">What we&rsquo;re raising funds for</p>
    <h2>Independent analysis for smarter growth.</h2>
    <p class="lead">Our current fundraising priority is to commission independent citywide mobility and infrastructure studies that complement existing public studies while providing objective, West Palm Beach&ndash;specific analysis &mdash; helping residents, elected officials, planners, and developers make informed decisions about future growth.</p>
    <p>Your support helps fund independent research, expert analysis, community engagement, and educational resources that empower residents and provide thoughtful, data-driven input as West Palm Beach plans for the future.</p>
    <p style="margin-top:1.3rem"><a href="https://www.zeffy.com/en-US/donation-form/donate-to-shape-our-citys-future" target="_blank" rel="noopener" class="btn btn-primary btn-lg">Donate Now</a></p>
  </div>
</section>

<section class="section alt center">
  <div class="container">
    <div class="section-head" style="margin-inline:auto"><p class="eyebrow">Get involved</p><h2>How you can help</h2></div>
    <div class="grid grid-4">
      <div class="card feature hover"><div class="ico" aria-hidden="true">&#10084;</div><h3>Donate</h3><p>Every contribution&mdash;large or small&mdash;helps fund independent research and gives residents a stronger voice in shaping West Palm Beach&rsquo;s future.</p><p style="margin-top:.7rem"><a href="https://www.zeffy.com/en-US/donation-form/donate-to-shape-our-citys-future" target="_blank" rel="noopener">Donate now &rsaquo;</a></p></div>
      <div class="card feature hover"><div class="ico" aria-hidden="true">&#128506;</div><h3>Learn</h3><p>Explore our Development &amp; Neighborhood Tracker tools to stay informed about projects affecting our community.</p><p style="margin-top:.7rem"><a href="development.html">Open the tracker &rsaquo;</a></p></div>
      <div class="card feature hover"><div class="ico" aria-hidden="true">&#128226;</div><h3>Share</h3><p>Help spread the word by sharing our campaign with friends, family, neighbors, and on social media.</p><p style="margin-top:.7rem"><a href="contact.html">Get involved &rsaquo;</a></p></div>
      <div class="card feature hover"><div class="ico" aria-hidden="true">&#129309;</div><h3>Volunteer</h3><p>Become involved with your neighborhood association or help strengthen resident engagement across the city.</p><p style="margin-top:.7rem"><a href="contact.html">Volunteer &rsaquo;</a></p></div>
    </div>
  </div>
</section>


<section class="section">
  <div class="container">
    <div class="section-head"><p class="eyebrow">On the agenda</p><h2>What we&rsquo;re watching now</h2></div>
    <div class="issue"><span class="tag alert">Active</span><div><h3 class="mb-0">900 S Rosemary &mdash; proposed convention-center hotel</h3><p class="note">A second convention-center hotel proposed downtown. We&rsquo;re tracking updates and encouraging residents to participate.</p><a href="development.html#featured">More on the tracker &rsaquo;</a></div></div>
    <div class="issue"><span class="tag">Watching</span><div><h3 class="mb-0">Downtown Master Plan &amp; waterfront</h3><p class="note">Long-range decisions shaping downtown and the waterfront for decades. We follow the public process.</p></div></div>
    <div class="issue"><span class="tag">Watching</span><div><h3 class="mb-0">Growth along the Dixie &amp; Flagler corridors</h3><p class="note">A wave of towers and mixed-use projects from Northwood to SoSo &mdash; see them all on the map.</p><a href="development.html">Open the tracker &rsaquo;</a></div></div>
  </div>
</section>

<section class="section sand">
  <div class="container" style="max-width:820px"><p class="eyebrow">Common questions</p><h2>About the Coalition</h2>{hfaq}<p class="reviewed">Last reviewed: June 2026.</p></div>
</section>

<section class="section sand" id="newsletter">
  <div class="container" style="max-width:720px">
    <div class="section-head center" style="margin-inline:auto"><p class="eyebrow">Stay informed</p><h2>Newsletter signup</h2>
      <p class="lead">Get Coalition updates on development projects, public meetings, and citywide issues.</p></div>
    <div class="embed-wrap" style="--embed-h:540px">
      <iframe title="Signup form powered by Zeffy" style="position:absolute;border:0;top:0;left:0;bottom:0;right:0;width:100%;height:100%" src="https://www.zeffy.com/en-US/embed/newsletter-form/sign-up-for-our-newsletter-3752" allowTransparency="true"></iframe>
    </div>
  </div>
</section>

<section class="section center">
  <div class="container" style="max-width:720px"><h2>Add your voice.</h2>
    <p class="lead">Open to residents, property owners, businesses, neighborhood organizations, and community stakeholders who share our mission.</p>
    <div class="actions" style="justify-content:center;display:flex;gap:.8rem;flex-wrap:wrap"><a href="contact.html" class="btn btn-primary btn-lg">Become a member</a><a href="donate.html" class="btn btn-ghost btn-lg" data-donate>Support our work</a></div>
  </div>
</section>
</main>'''
s=s.replace('<section class="section sand">',
  photo_band(IMG_CITYHALL,"West Palm Beach City Hall",
    "City decisions are made in public &mdash; we help residents show up and be heard.",CRED_CITYHALL)
  +'\n<section class="section sand">',1)
s+=FOOT+"\n</body>\n</html>"
_h=HOME.get("hero",{}); _w=HOME.get("whoWeAre",{}); _fr=HOME.get("fundraising",{})
s=_apply_text(s,[
 ("The central information hub for West Palm Beach residents", _h.get("eyebrow")),
 ("Shaping the future of West Palm Beach, together.", _h.get("headline")),
 ("A citywide, non-partisan coalition of residents, property owners, and neighborhood leaders &mdash; organizing the information our city needs and working across district lines on the issues that affect every part of it.", _h.get("subtitle")),
 ('<p class="eyebrow">Who we are</p>', ('<p class="eyebrow">'+_w["eyebrow"]+'</p>') if _w.get("eyebrow") else None),
 ("A citywide alliance of neighborhood leaders.", _w.get("heading")),
 ("The West Palm Beach Residents Coalition is a citywide alliance of neighborhood leaders working together to ensure West Palm Beach grows thoughtfully, responsibly, and with residents at the table.", _w.get("paragraph1")),
 ("We believe the strongest communities are built through collaboration, transparency, and informed decision-making. By bringing neighborhoods together under one coordinated, constructive voice, we can help create practical, long-term solutions that benefit everyone who lives, works, and invests in our city.", _w.get("paragraph2")),
 ("What we&rsquo;re raising funds for", _fr.get("eyebrow")),
 ("Independent analysis for smarter growth.", _fr.get("heading")),
 ("Our current fundraising priority is to commission independent citywide mobility and infrastructure studies that complement existing public studies while providing objective, West Palm Beach&ndash;specific analysis &mdash; helping residents, elected officials, planners, and developers make informed decisions about future growth.", _fr.get("paragraph1")),
 ("Your support helps fund independent research, expert analysis, community engagement, and educational resources that empower residents and provide thoughtful, data-driven input as West Palm Beach plans for the future.", _fr.get("paragraph2")),
])
write("index.html",s)

# ---------------- ABOUT ----------------
afaq,afaq_ld=faq([
 ("What are the Coalition&rsquo;s priorities?","The Coalition focuses on citywide issues: meaningful resident representation in planning, responsible and transparent growth, infrastructure and climate resilience, mobility and public safety, and protection of the waterfront and environment."),
 ("Who governs the Coalition, and can elected officials serve on the Board?","Our Board of Directors (11 current members) governs the Coalition, organized around core focus areas. No currently serving elected public official may sit on the Board. Only individuals authorized by the Board may speak on its behalf."),
 ("Does the Coalition take positions on individual development projects?","The Coalition focuses on issues, policies, and processes rather than personalities. It does not advocate on a single neighborhood dispute unless the Board determines it carries citywide significance."),
 ("Is the Coalition non-partisan?","Yes. As a 501(c)(4) social-welfare organization, the Coalition does not endorse or oppose candidates for public office."),
])
s=head("WPB Residents Coalition | About & Priorities",
 "Our mission, priorities, principles, and governance. The WPB Residents Coalition is a non-partisan 501(c)(4) citywide voice for residents.","about.html",
 extra=afaq_ld+"\n"+speakable())
s+=header("about.html")+'<main id="main">'
s+=hero("About the Coalition","A coordinated, informed, constructive voice for our city.",
 "Built by residents and neighborhood leaders to focus on the issues that affect West Palm Beach as a whole.",small=True)
s+='''
<section class="section">
  <div class="container" style="max-width:840px">
    <p class="eyebrow">Our purpose</p>
    <h2>Why we exist</h2>
    <p class="lead">The Coalition provides a coordinated, informed, and constructive citywide voice on issues affecting West Palm Beach&rsquo;s long-term livability &mdash; growth and development, infrastructure, environmental resilience, transparency, public safety, historic character, mobility, and waterfront planning.</p>
    <p>We complement existing neighborhood associations and local advocacy groups &mdash; focusing on broader issues that affect multiple neighborhoods and residents collectively.</p>
  </div>
</section>

<section class="section alt">
  <div class="container">
    <div class="section-head"><p class="eyebrow">What we&rsquo;re working toward</p><h2>Our priorities</h2>
      <p class="lead">Practical, non-partisan priorities focused on how the city plans, decides, and communicates.</p></div>
    <div class="grid grid-3">
      <div class="card feature"><h3>A real seat in planning</h3><p>Meaningful resident representation in long-term and neighborhood planning &mdash; including the Downtown Master Plan process.</p></div>
      <div class="card feature"><h3>Responsible growth</h3><p>Thoughtful, transparent review of development, zoning, and density so growth strengthens neighborhoods.</p></div>
      <div class="card feature"><h3>Better information &amp; transparency</h3><p>Clear notice of projects and decisions, and public information that&rsquo;s easy to find and understand.</p></div>
      <div class="card feature"><h3>Infrastructure &amp; resilience</h3><p>Drainage, utilities, public works, and climate resilience that keep the city functioning and protected.</p></div>
      <div class="card feature"><h3>Mobility &amp; safety</h3><p>Traffic, parking, pedestrian safety, and public-safety concerns across the city.</p></div>
      <div class="card feature"><h3>Waterfront &amp; environment</h3><p>Protecting the waterfront, green space, and environmental resilience for the long term.</p></div>
    </div>
    <p class="note" style="margin-top:1.2rem">These public priorities are drawn from the Coalition&rsquo;s planning work; specific positions on individual projects are set by the Board.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head"><p class="eyebrow">How we&rsquo;re organized</p><h2>Governance &amp; leadership</h2>
      <p class="lead">Our Board of Directors (11 current members) governs the Coalition, with leadership organized around our core focus areas. No currently serving elected public official may sit on the Board. <a href="board.html">Meet the Board &rsaquo;</a></p></div>
    <div class="grid grid-4">
      <div class="card"><h3>Chair / President</h3><p>Leads operations and serves as primary spokesperson.</p></div>
      <div class="card"><h3>Communications</h3><p>Media relations, public messaging, and social media.</p></div>
      <div class="card"><h3>Neighborhood Relations</h3><p>Coordination with association presidents and community leaders.</p></div>
      <div class="card"><h3>Growth &amp; Development</h3><p>Zoning, land use, redevelopment, and major construction.</p></div>
      <div class="card"><h3>Infrastructure</h3><p>Utilities, drainage, resiliency, transportation, public works.</p></div>
      <div class="card"><h3>Crime &amp; Safety</h3><p>Public-safety initiatives and neighborhood safety.</p></div>
      <div class="card"><h3>Traffic &amp; Parking</h3><p>Congestion, roadways, parking, pedestrian safety, mobility.</p></div>
      <div class="card"><h3>Committees</h3><p>Government affairs, communications, membership, fundraising, waterfront/resilience, research.</p></div>
    </div>
  </div>
</section>

<section class="section sand">
  <div class="container" style="max-width:840px"><p class="eyebrow">Our principles</p><h2>Non-partisan, citywide, constructive</h2>
    <div class="callout"><p class="mb-0"><strong>We do not endorse political candidates</strong> and do not advocate on any single neighborhood dispute unless the Board determines it carries citywide significance. We focus on issues, policies, and processes &mdash; not personalities. Only individuals authorized by the Board may speak on behalf of the Coalition.</p></div>
    <p class="reviewed">Last reviewed: June 2026.</p>
  </div>
</section>
<section class="section">
  <div class="container" style="max-width:840px">
    <div class="section-head"><p class="eyebrow">Common questions</p><h2>About the Coalition</h2></div>
    {AFAQ}
  </div>
</section>
</main>'''
s=s.replace('<section class="section sand">',
  ASKS_HTML+photo_band(IMG_CITYPLACE,"Downtown West Palm Beach street scene",
    "A growing city &mdash; shaped with residents, not just for them.",CRED_CITYPLACE)
  +'\n<section class="section sand">',1)
s+=FOOT+"\n</body>\n</html>"
s=s.replace('{AFAQ}',afaq)
_ap=ABOUT.get("purpose",{})
s=_apply_text(s,[
 ("The Coalition provides a coordinated, informed, and constructive citywide voice on issues affecting West Palm Beach&rsquo;s long-term livability &mdash; growth and development, infrastructure, environmental resilience, transparency, public safety, historic character, mobility, and waterfront planning.", _ap.get("lead")),
 ("We complement existing neighborhood associations and local advocacy groups &mdash; focusing on broader issues that affect multiple neighborhoods and residents collectively.", _ap.get("paragraph")),
])
write("about.html",s)

# ---------------- DEVELOPMENT TRACKER ----------------
data=json.load(open(os.path.join(OUT,"assets","projects.json")))
projects=data["projects"]; meta=data["_meta"]
proj_js=json.dumps(projects)
dfaq,dfaq_ld=faq([
 ("What is the 900 S Rosemary project?","900 S Rosemary is a proposed second convention-center hotel in downtown West Palm Beach. Because a project of this scale affects traffic, parking, and downtown character, the Coalition tracks it as a citywide issue."),
 ("How current is this development map?","The tracker is a working draft maintained by the Coalition. Commission district, board status, and hearing dates should be verified against current City of West Palm Beach agendas before relying on them. Map locations are approximate."),
])
s=head("West Palm Beach Development Tracker | Interactive Project Map",
 "An interactive map of major West Palm Beach development projects — proposed, approved, and under construction — by status, district, and neighborhood.",
 "development.html",extra=dfaq_ld)
s+='<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">\n'
s+=header("development.html")+'<main id="main">'
s+=hero("Development Tracker","What&rsquo;s being built across West Palm Beach.",
 "An interactive map of major development projects &mdash; what&rsquo;s proposed, in review, approved, and under construction &mdash; near you and across the city.",small=True,bg=IMG_SKYLINE)
s+=f'''
<section class="section">
  <div class="container">
    <div class="callout" style="margin-bottom:1.6rem;border-left-color:var(--gold)">
      <p class="mb-0"><strong>Working draft.</strong> {html.escape(meta["disclaimer"])}</p>
    </div>
    <div class="tracker-layout">
      <aside class="filters" aria-label="Map filters">
        <h3>Filter projects</h3>
        <label for="f-status">Status</label>
        <select id="f-status"><option value="">All statuses</option></select>
        <label for="f-district">Commission district</label>
        <select id="f-district"><option value="">All districts</option></select>
        <label for="f-search">Search</label>
        <input id="f-search" type="search" placeholder="Project or neighborhood&hellip;">
        <div class="legend" aria-hidden="true">
          <span><i class="dot st-proposed"></i>Proposed</span>
          <span><i class="dot st-review"></i>In Review</span>
          <span><i class="dot st-planning"></i>Planning</span>
          <span><i class="dot st-approved"></i>Approved</span>
          <span><i class="dot st-construction"></i>Construction</span>
          <span><i class="dot st-complete"></i>Completed</span>
          <span><i class="dot st-onhold"></i>On Hold</span>
        </div>
        <p class="note" style="margin-top:1rem"><span id="count"></span> projects shown</p>
      </aside>
      <div><div id="map" role="application" aria-label="Map of West Palm Beach development projects" style="height:520px"><p class="note" style="padding:1.6rem">Loading the interactive map… if it stays blank, make sure you&rsquo;re online (the map tiles load from the web).</p></div></div>
    </div>
    <div class="proj-list" id="proj-list"></div>
  </div>
</section>

<section class="section sand">
  <div class="container" style="max-width:840px"><p class="eyebrow">Common questions</p><h2>About the tracker</h2>{dfaq}
  <p class="note">Key meetings to track: Downtown Master Plan workshops &amp; hearings, DAC review meetings, Planning Board hearings, City Commission readings, and CRA Board meetings.</p>
  <p class="reviewed">Working draft &mdash; review against City agendas. Last updated: June 2026.</p></div>
</section>
</main>'''
s+=f'''
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const PROJECTS={proj_js};
const COLORS={{"Proposed":"#9aa7b1","In Review":"#E0A43B","Planning":"#92C3D1","Approved":"#2F7C93","Under Construction":"#5F7E3C","Completed":"#163B65","On Hold":"#B0432E"}};
const map=L.map('map',{{scrollWheelZoom:false}}).setView([26.715,-80.055],13);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{maxZoom:19,attribution:'&copy; OpenStreetMap'}}).addTo(map);
let markers=[];
const VISIBLE=PROJECTS.filter(function(p){{return p.approved!==false;}});
const elStatus=document.getElementById('f-status'),elDist=document.getElementById('f-district'),
      elSearch=document.getElementById('f-search'),list=document.getElementById('proj-list'),count=document.getElementById('count');
[...new Set(VISIBLE.map(p=>p.status))].forEach(v=>{{let o=document.createElement('option');o.value=v;o.textContent=v;elStatus.appendChild(o);}});
[...new Set(VISIBLE.map(p=>p.district))].sort().forEach(v=>{{let o=document.createElement('option');o.value=v;o.textContent='District '+v;elDist.appendChild(o);}});
function render(){{
  markers.forEach(m=>map.removeLayer(m));markers=[];list.innerHTML='';
  const q=elSearch.value.trim().toLowerCase(),st=elStatus.value,di=elDist.value;
  let shown=0;
  VISIBLE.forEach(p=>{{
    if(p.lat==null||p.lng==null)return;
    const hay=(p.name+' '+p.neighborhoods.join(' ')+' '+p.location).toLowerCase();
    if(st&&p.status!==st)return; if(di&&p.district!==di)return; if(q&&!hay.includes(q))return;
    shown++;
    const col=COLORS[p.status]||'#9aa7b1';
    const m=L.circleMarker([p.lat,p.lng],{{radius:9,color:'#fff',weight:2,fillColor:col,fillOpacity:.95}}).addTo(map);
    m.bindPopup(`<h4>${{p.name}}</h4><b>${{p.status}}</b> &middot; District ${{p.district}}<br>${{p.location}} &mdash; ${{p.neighborhoods.join(', ')}}<br><span style="color:#5B6B78">${{p.notes}}</span>`);
    markers.push(m);
    const card=document.createElement('div');card.className='proj';card.style.borderLeftColor=col;
    card.innerHTML=`<h4>${{p.name}}</h4><div class="meta">${{p.location}} &middot; ${{p.neighborhoods.join(', ')}} &middot; District ${{p.district}}</div><span class="status" style="background:${{col}}">${{p.status}}</span><p class="note" style="margin:.6rem 0 0">${{p.notes}}</p>`;
    card.tabIndex=0;
    card.addEventListener('click',()=>{{map.setView([p.lat,p.lng],15);m.openPopup();window.scrollTo({{top:document.getElementById('map').offsetTop-70,behavior:'smooth'}});}});
    list.appendChild(card);
  }});
  count.textContent=shown;
}}
[elStatus,elDist].forEach(e=>e.addEventListener('change',render));
elSearch.addEventListener('input',render);
render();
setTimeout(function(){{map.invalidateSize();}},300);window.addEventListener('load',function(){{map.invalidateSize();}});
// Live data: when hosted, pull the latest projects.json (updated from the Google Sheet); fall back to embedded data for local viewing.
fetch('assets/projects.json').then(r=>r.ok?r.json():null).then(d=>{{if(d&&d.projects&&d.projects.length){{PROJECTS.length=0;d.projects.forEach(p=>PROJECTS.push(p));render();}}}}).catch(()=>{{}});
</script>'''
s+=FOOT+"\n</body>\n</html>"
write("development.html",s)

# ---------------- NEIGHBORHOODS ----------------
_nb=json.load(open(os.path.join(OUT,"assets","neighborhoods.json"),encoding="utf-8"))["neighborhoods"]
rows=[(n.get("name","").strip(), str(n.get("district","")).strip(), ("contact" if n.get("hasContact") else "")) for n in _nb if n.get("name","").strip()]
total=len(rows); wc=sum(1 for x in rows if x[2])
_tr=[]
for n,d,c in rows:
    dcell=f'<span class="pill">District {html.escape(d)}</span>' if d else '<span class="pill empty">&mdash;</span>'
    ccell='<span class="pill">Contact on file</span>' if c else '<span class="pill empty">Seeking contact</span>'
    _tr.append(f'      <tr><td>{html.escape(n)}</td><td>{dcell}</td><td>{ccell}</td></tr>')
trows="\n".join(_tr)
nfaq,nfaq_ld=faq([
 ("What is a neighborhood association?","A neighborhood association is a voluntary, resident-led group representing a specific West Palm Beach neighborhood. They remain fully independent; the Coalition connects them on citywide issues."),
 (f"How many neighborhoods are in the Coalition network?","The Coalition currently tracks {total} West Palm Beach neighborhood associations across the city&rsquo;s commission districts, and the directory keeps growing."),
 ("Can my neighborhood association join the Coalition?","Yes. Associations can join as organizational members to coordinate on citywide issues. If your association isn&rsquo;t listed, you can join or update your listing through the site."),
 ("Does joining affect my association&rsquo;s independence?","No. Associations stay fully independent and self-governing. The Coalition coordinates a shared, informed voice on issues that cross neighborhood lines."),
])
s=head("West Palm Beach Neighborhood Associations Directory | WPBRC",
 f"A growing directory of {total} West Palm Beach neighborhood associations in the Residents Coalition network.","neighborhoods.html",
 extra=nfaq_ld+"\n"+speakable())
s+=header("neighborhoods.html")+'<main id="main">'
s+=hero("Our network","West Palm Beach neighborhoods.",
 "The Coalition connects neighborhood associations across the city. If your association isn&rsquo;t listed or your contact is missing, we&rsquo;d love to hear from you.",small=True)
s+=f'''
<section class="section">
  <div class="container">
    <div class="stats" style="margin-bottom:2.2rem">
      <div><div class="num">{total}</div><div class="lbl">Associations tracked</div></div>
      <div><div class="num">{wc}</div><div class="lbl">Contacts on file</div></div>
      <div><div class="num">{total-wc}</div><div class="lbl">Seeking a contact</div></div>
      <div><div class="num">5</div><div class="lbl">Commission districts</div></div>
    </div>
    <div class="searchbar" style="margin-bottom:1rem"><label for="dir-search" class="note">Search the directory</label>
      <input id="dir-search" type="search" placeholder="Search neighborhoods&hellip;" aria-label="Search neighborhoods"></div>
    <div class="table-wrap"><table class="dir">
      <caption class="note" style="text-align:left;padding:.6rem 1rem">West Palm Beach neighborhood associations</caption>
      <thead><tr><th scope="col">Neighborhood / Association</th><th scope="col">District</th><th scope="col">Coalition contact</th></tr></thead>
      <tbody>
{trows}
      </tbody></table></div>
    <p class="note" style="margin-top:1rem">Contact details for association leaders are kept private and are not published here.
      Is your association represented? <a href="join.html">Join as an organizational member</a> or <a href="contact.html">update your listing</a>.</p>
  </div>
</section>
<section class="section sand center"><div class="container" style="max-width:680px"><h2>Bring your neighborhood in.</h2>
  <p class="lead">Associations can join as organizational members to coordinate on citywide issues while staying fully independent.</p>
  <a href="join.html" class="btn btn-primary btn-lg">Join as an organization</a></div></section>
<section class="section">
  <div class="container" style="max-width:840px">
    <div class="section-head"><p class="eyebrow">Common questions</p><h2>Neighborhood associations</h2></div>
    {{NFAQ}}
  </div>
</section>
</main>'''
s+=FOOT+"\n</body>\n</html>"
s=s.replace('{NFAQ}',nfaq)
write("neighborhoods.html",s)

# ---------------- BOARD ----------------
roles=[("Chair / President","Leads organizational operations and serves as the primary spokesperson; presides over Board and membership meetings."),
 ("Communications Chair","External communications, media relations, press outreach, public messaging, and social media."),
 ("Neighborhood Relations Chair","Maintains communication with association presidents and community leaders; coordinates outreach."),
 ("Growth &amp; Development Chair","Monitors zoning, land use, redevelopment, and major construction; evaluates project impacts."),
 ("Infrastructure Chair","Infrastructure, utilities, drainage, resiliency, transportation systems, and public works."),
 ("Crime &amp; Safety Chair","Public-safety initiatives and coordination on crime prevention and neighborhood safety."),
 ("Traffic &amp; Parking Chair","Traffic congestion, roadway planning, parking, pedestrian safety, and mobility.")]
cards="\n".join(f'<div class="card"><div class="ico" aria-hidden="true">&#128100;</div><h3>{t}</h3><p>{d}</p><p class="note" style="margin-top:.6rem">Open seat &mdash; <a href="join.html">get involved</a></p></div>' for t,d in roles)
_bd=json.load(open(os.path.join(OUT,"assets","board.json")))
_members=_bd.get("members",[])
def _mcard(m):
    yrs=str(m.get("yearsInWPB","")).strip()
    bio=m.get("bio","").strip()
    yrs_html=('<br><strong>Years in WPB:</strong> '+html.escape(yrs)) if yrs else ''
    bio_html=('<p style="margin-top:.6rem">'+html.escape(bio)+'</p>') if bio else ''
    return ('<div class="card member"><div class="ico" aria-hidden="true">&#128100;</div>'
            '<h3 class="mb-0">'+html.escape(m.get("name",""))+'</h3>'
            '<p class="role note" style="margin:.15rem 0 .6rem">'+html.escape(m.get("role",""))+'</p>'
            '<p class="mb-0"><strong>Neighborhood:</strong> '+html.escape(m.get("neighborhood",""))+yrs_html+'</p>'
            +bio_html+'</div>')
_member_cards="".join(_mcard(m) for m in _members)
members_section=('<section class="section"><div class="container">'
    '<div class="section-head"><p class="eyebrow">Our board</p><h2>Board of Directors</h2>'
    '<p class="lead">Residents who live here and serve here &mdash; each representing a West Palm Beach neighborhood association.</p></div>'
    '<div class="grid grid-3">'+_member_cards+'</div></div></section>') if _members else ''
s=head(f"Board & Leadership | {ORG}",
 "Meet the Board of Directors and officer roles of the West Palm Beach Residents Coalition. No currently serving elected official may sit on the Board.","board.html")
s+=header("board.html")+'<main id="main">'
s+=hero("Leadership","The Board &amp; officer roles.",
 "Our Board of Directors (11 current members) governs the Coalition, with leadership organized around our core focus areas. No currently serving elected public official may sit on the Board.",small=True)
s+=members_section
_roles_grid=('' if _members else f'''
<section class="section">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Officer roles</p><h2>How leadership is organized</h2>
      <p class="lead">Officer names will be published here as the founding Board is seated. No currently serving elected public official may serve on the Board.</p></div>
    <div class="grid grid-4">{cards}</div>
  </div>
</section>''')
s+=_roles_grid
s+=f'''
<section class="section sand"><div class="container" style="max-width:840px"><p class="eyebrow">Committees</p><h2>Where the work happens</h2>
  <p>The Board may establish committees including Government Affairs / Policy; Infrastructure / Transportation; Communications / Media; Membership &amp; Outreach; Fundraising / Development; Waterfront / Environmental Resilience; and Research / Public Information. Committees may include non-board members.</p>
  <p><a href="join.html" class="btn btn-primary">Serve on a committee</a></p></div></section>
</main>'''
s+=FOOT+"\n</body>\n</html>"
write("board.html",s)

# ---------------- EVENTS ----------------
_evlist=json.load(open(OUT+"/assets/events.json"))["events"]
_evitems=[{"@type":"Event","name":e["title"],"startDate":e["date"],"eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode","location":{"@type":"Place","name":e.get("location","West Palm Beach"),"address":{"@type":"PostalAddress","addressLocality":"West Palm Beach","addressRegion":"FL","addressCountry":"US"}},"description":_strip(e.get("description","")),"organizer":{"@type":"Organization","name":ORG,"url":BASE},"url":BASE+"/events.html"} for e in _evlist if e.get("date")]
EVENTS_LD=('<script type="application/ld+json">'+json.dumps({"@context":"https://schema.org","@graph":_evitems})+'</script>') if _evitems else ""
s=head(f"Calendar & Newsletter | {ORG}",
 "Upcoming West Palm Beach Residents Coalition events, public meetings to track, and the community newsletter sign-up.","events.html", extra=EVENTS_LD)
s+=header("events.html")+'<main id="main">'
s+=hero("Stay engaged","Calendar &amp; updates.",
 "Public meetings, community forums, and the hearings worth showing up for &mdash; plus a newsletter that keeps you informed.",small=True)
s+='''
<section class="section">
  <div class="container">
    <div class="section-head"><p class="eyebrow">Upcoming</p><h2>What&rsquo;s on the calendar</h2></div>
    __EVENTS_LIST__
  </div>
</section>
<section class="section sand" id="newsletter">
  <div class="container split">
    <div><p class="eyebrow">Newsletter</p><h2>Get the citywide brief.</h2>
      <p class="lead">A periodic update on development, hearings, and how to make your voice heard &mdash; no spam, no party line.</p>
      <p class="note">We keep your information private and use it only for Coalition updates.</p></div>
    <div class="form"><h3 class="mt-0">Sign up</h3>
      <form data-demo>
        <div class="field"><label for="nn">Name</label><input id="nn" name="nn" required></div>
        <div class="field"><label for="ne">Email</label><input id="ne" name="ne" type="email" required></div>
        <div class="field"><label for="nz">Neighborhood (optional)</label><input id="nz" name="nz"></div>
        <button type="submit" class="btn btn-primary btn-lg">Subscribe</button>
        <p class="form-msg note" style="display:none;margin-top:1rem;color:var(--green)">Thanks &mdash; you&rsquo;re on the list. (Demo form: connect to your email platform to collect subscribers.)</p>
      </form>
    </div>
  </div>
</section>
</main>'''
s=re.sub(r'<form data-demo>.*?</form>',
  zeffy_embed(ZEFFY["newsletter"],"WPBRC newsletter sign-up",560), s, flags=re.S)
# data-driven events: embed events.json + live-fetch override (past events auto-hide)
_evjs=json.dumps(json.load(open(OUT+"/assets/events.json"))["events"])
EVENTS_TPL='''<div class="grid grid-3" id="events-list"></div>
<script>
const EVENTS={"events":__DATA__};
(function(){
  const tagClass={"Featured":"alert","Hearing":"alert","Meeting":"","Track":"","Forum":""};
  function esc(x){return (x||"").toString();}
  function render(list){
    const el=document.getElementById('events-list'); if(!el) return; el.innerHTML='';
    const today=new Date(); today.setHours(0,0,0,0);
    list.slice().sort(function(a,b){return (a.date||'9999')<(b.date||'9999')?-1:1;}).forEach(function(ev){
      if(ev.approved===false)return;
      if(ev.date){var d=new Date(ev.date+'T00:00:00'); if(!isNaN(d)&&d<today) return;}
      const card=document.createElement('div'); card.className='card feature';
      const tg=ev.tag?('<span class="tag '+(tagClass[ev.tag]||'')+'">'+esc(ev.tag)+'</span>'):'';
      const when=ev.displayDate?('<p class="meta note">'+esc(ev.displayDate)+'</p>'):'';
      const loc=ev.location?(' <span class="note">'+esc(ev.location)+'.</span>'):'';
      const link=ev.url?(' <a href="'+esc(ev.url)+'">Details &rsaquo;</a>'):'';
      card.innerHTML=tg+'<h3 style="margin-top:.6rem">'+esc(ev.title)+'</h3>'+when+'<p>'+esc(ev.description)+loc+link+'</p>';
      el.appendChild(card);
    });
    if(!el.children.length){el.innerHTML='<p class="note">No upcoming events listed right now. Check back soon, or sign up for the newsletter below.</p>';}
  }
  render(EVENTS.events||[]);
  fetch('assets/events.json').then(function(r){return r.ok?r.json():null;}).then(function(d){if(d&&d.events)render(d.events);}).catch(function(){});
})();
</script>'''
s=s.replace("__EVENTS_LIST__", EVENTS_TPL.replace("__DATA__", _evjs))
s+=FOOT+"\n</body>\n</html>"
write("events.html",s)

# ---------------- JOIN ----------------
s=head(f"Join the {ORG} | Membership",
 "Become a member of the West Palm Beach Residents Coalition. Open to residents, property owners, businesses, and neighborhood organizations.","join.html")
s+=header("join.html")+'<main id="main">'
s+=hero("Add your voice","Join the Residents Coalition.",
 "Open to residents, property owners, businesses, neighborhood organizations, and community stakeholders who support our mission.",small=True)
s+='''
<section class="section">
  <div class="container">
    <div class="section-head center" style="margin-inline:auto"><p class="eyebrow">Membership</p><h2>Find the right fit</h2>
      <p class="note">Categories and any dues are set by the Board and reflect the categories in our bylaws. Adding your voice as a Supporting Member is free.</p></div>
    <div class="grid grid-4">
      <div class="tier"><h3>Supporting</h3><div class="price">Free</div><ul><li>Issue alerts &amp; updates</li><li>Forum invitations</li><li>Ways to take action</li></ul><a href="#join-form" class="btn btn-teal">Join free</a></div>
      <div class="tier featured"><h3>Founding</h3><div class="price">Support</div><ul><li>Everything in Supporting</li><li>Recognized as an early backer</li><li>Priority invitations</li></ul><a href="donate.html" class="btn btn-primary">Become a founder</a></div>
      <div class="tier"><h3>Organizational</h3><div class="price">For groups</div><ul><li>For neighborhood associations</li><li>Coordinate citywide</li><li>Stay independent</li></ul><a href="#join-form" class="btn btn-teal">Register org</a></div>
      <div class="tier"><h3>Advisory</h3><div class="price">By invite</div><ul><li>Subject-matter expertise</li><li>Guidance to committees</li><li>Issue-specific input</li></ul><a href="contact.html" class="btn btn-teal">Get in touch</a></div>
    </div>
  </div>
</section>
<section class="section sand" id="join-form"><div class="container" style="max-width:720px"><p class="eyebrow">Membership form</p><h2>Sign up</h2>
  <form class="form" data-demo>
    <div class="grid grid-2"><div class="field"><label for="fn">First name</label><input id="fn" required></div><div class="field"><label for="ln">Last name</label><input id="ln" required></div></div>
    <div class="field"><label for="em">Email</label><input id="em" type="email" required></div>
    <div class="grid grid-2"><div class="field"><label for="ph">Phone (optional)</label><input id="ph" type="tel"></div><div class="field"><label for="nb">Your neighborhood</label><input id="nb" placeholder="e.g. Flamingo Park"></div></div>
    <div class="field"><label for="cat">Membership category</label><select id="cat"><option>Supporting Member (free)</option><option>Founding Member</option><option>Organizational Member (neighborhood association)</option><option>Advisory Member</option></select></div>
    <div class="field"><label for="iss">Issues you care about most (optional)</label><textarea id="iss" placeholder="Growth &amp; development, infrastructure, traffic, waterfront, safety&hellip;"></textarea></div>
    <button type="submit" class="btn btn-primary btn-lg">Submit membership</button>
    <p class="form-msg note" style="display:none;margin-top:1rem;color:var(--green)">Thank you &mdash; your membership request has been recorded. (Demo form: connect to your email or membership platform.)</p>
    <p class="note" style="margin-top:1rem">By joining you affirm support for the Coalition&rsquo;s mission. We keep your information private.</p>
  </form></div></section>
</main>'''
s=re.sub(r'<form class="form" data-demo>.*?</form>',
  zeffy_embed(ZEFFY["membership"],"WPBRC membership form",1050), s, flags=re.S)
s+=FOOT+"\n</body>\n</html>"
write("join.html",s)

# ---------------- DONATE + SPONSORS ----------------
s=head(f"Donate & Sponsor | {ORG}",
 "Support the West Palm Beach Residents Coalition through donations, sponsorships, and founding gifts. Note: 501(c)(4) gifts are generally not tax-deductible.","donate.html")
s+=header("donate.html")+'<main id="main">'
s+=hero("Fuel the work","Help Fund Independent Traffic, Mobility &amp; Infrastructure Analysis.",
 "Your contribution funds independent traffic, mobility, and infrastructure analysis &mdash; plus development tracking, public forums, and resident outreach across the city.",small=True)
s+='''
<section class="section">
  <div class="container split">
    <div><p class="eyebrow">Where it goes</p><h2>What your support makes possible</h2>
      <p>The Coalition accepts voluntary contributions, sponsorships, donations, and fundraising support. Funds are held in the Coalition&rsquo;s name under Board oversight, with expenditures authorized under adopted financial-controls policies.</p>
      <div class="grid grid-2" style="margin-top:1rem">
        <div class="card"><h3>Development tracking</h3><p>Keeping the project map current and researched.</p></div>
        <div class="card"><h3>Public forums</h3><p>Venue, materials, and outreach for community meetings.</p></div>
        <div class="card"><h3>Independent research</h3><p>Studies and technical evaluations on major projects.</p></div>
        <div class="card"><h3>Resident outreach</h3><p>Mailers, signage, and communications.</p></div>
      </div>
    </div>
    <div class="form"><h3 class="mt-0">Make a contribution</h3>
      <form data-demo>
        <div class="field"><label>Choose an amount</label><div class="grid grid-3" style="gap:.6rem"><button type="button" class="btn btn-ghost">$25</button><button type="button" class="btn btn-ghost">$50</button><button type="button" class="btn btn-ghost">$100</button></div></div>
        <div class="field"><label for="amt">Other amount</label><input id="amt" type="number" min="1" placeholder="$"></div>
        <div class="field"><label for="dn">Name</label><input id="dn" required></div>
        <div class="field"><label for="de">Email</label><input id="de" type="email" required></div>
        <button type="submit" class="btn btn-primary btn-lg">Continue to payment</button>
        <p class="form-msg note" style="display:none;margin-top:1rem;color:var(--green)">Thank you for your support! (Demo form: connect PayPal, Stripe, or a donation platform.)</p>
      </form>
    </div>
  </div>
</section>
<section class="section alt center"><div class="container"><p class="eyebrow">Partners</p><h2>Our sponsors &amp; founding donors</h2>
  <p class="lead" style="max-width:60ch;margin-inline:auto">Local businesses and residents who invest in a stronger, better-informed community.</p>
  <div class="sponsors" style="margin-top:1.6rem">
    <div class="sponsor">Your logo here</div><div class="sponsor">Become a sponsor</div><div class="sponsor">Founding donor</div><div class="sponsor">Founding donor</div>
  </div>
  <p style="margin-top:1.6rem"><a href="contact.html" class="btn btn-secondary">Become a sponsor</a></p></div></section>
<section class="section sand"><div class="container" style="max-width:840px"><div class="callout"><h3 class="mt-0">A note on tax status</h3>
  <p class="mb-0">Organized under Section 501(c)(4) of the Internal Revenue Code. Contributions to 501(c)(4) social-welfare organizations are <strong>generally not tax-deductible as charitable contributions</strong>. Please consult your tax advisor. This is general information, not tax advice.</p></div></div></section>
</main>'''
s=re.sub(r'<form data-demo>.*?</form>',
  zeffy_embed(ZEFFY["donation"],"WPBRC donation form",760), s, flags=re.S)
s+=FOOT+"\n</body>\n</html>"
write("donate.html",s)

# ---------------- CONTACT ----------------
s=head(f"Contact {ORG}",
 "Get in touch with the West Palm Beach Residents Coalition to raise a citywide issue, update your neighborhood listing, volunteer, or ask how to get involved.","contact.html")
s+=header("contact.html")+'<main id="main">'
s+=hero("Get in touch","We&rsquo;d love to hear from you.",
 "Have an issue affecting multiple neighborhoods? Want to update your association&rsquo;s listing, volunteer, or ask a question? Reach out.",small=True)
s+='''
<section class="section"><div class="container split">
  <div class="form"><h3 class="mt-0">Send a message</h3>
    <form data-demo>
      <div class="grid grid-2"><div class="field"><label for="cn">Name</label><input id="cn" required></div><div class="field"><label for="ce">Email</label><input id="ce" type="email" required></div></div>
      <div class="field"><label for="ct">Topic</label><select id="ct"><option>General question</option><option>Raise a citywide issue</option><option>A development project</option><option>Membership</option><option>Update / add a neighborhood listing</option><option>Volunteer</option><option>Media / press inquiry</option><option>Sponsorship / donation</option></select></div>
      <div class="field"><label for="cm">Message</label><textarea id="cm" required></textarea></div>
      <button type="submit" class="btn btn-primary btn-lg">Send message</button>
      <p class="form-msg note" style="display:none;margin-top:1rem;color:var(--green)">Thank you &mdash; your message has been recorded. (Demo form: connect to your inbox or a form service.)</p>
    </form></div>
  <div><h3>Other ways to connect</h3>
    <p>Add your contact email, phone, and mailing address here once channels are set up. Messages from the form already reach <em>info@wpbrc.org</em>.</p>
    <div class="card" style="margin-bottom:1.2rem"><h3 class="mt-0">Press &amp; media</h3><p class="mb-0">Only individuals authorized by the Board may speak for the Coalition. Select <strong>&ldquo;Media / press inquiry&rdquo;</strong> and we&rsquo;ll route it to our Communications Chair.</p></div>
    <div class="card"><h3 class="mt-0">Neighborhood leaders</h3><p class="mb-0">Association president or community leader? Use the form to coordinate with our Neighborhood Relations Chair.</p></div>
    <div class="card" style="margin-top:1.2rem"><h3 class="mt-0">Newsletter</h3><p>Get Coalition updates on development, meetings, and citywide issues.</p><a href="https://www.zeffy.com/en-US/newsletter-form/sign-up-for-our-newsletter-3752" target="_blank" rel="noopener" class="btn btn-primary">Newsletter signup</a></div>
  </div>
</div></section>
</main>'''
contact_form=('<form action="'+FORMSPREE+'" method="POST">'
  '<input type="hidden" name="_subject" value="New message from the WPBRC website">'
  '<input type="hidden" name="_template" value="table">'
  '<input type="hidden" name="_captcha" value="false">'
  '<div class="grid grid-2"><div class="field"><label for="cn">Name</label><input id="cn" name="name" required></div>'
  '<div class="field"><label for="ce">Email</label><input id="ce" name="email" type="email" required></div></div>'
  '<div class="field"><label for="ct">Topic</label><select id="ct" name="topic"><option>General question</option><option>Raise a citywide issue</option><option>A development project</option><option>Membership</option><option>Update / add a neighborhood listing</option><option>Volunteer</option><option>Media / press inquiry</option><option>Sponsorship / donation</option></select></div>'
  '<div class="field"><label for="cm">Message</label><textarea id="cm" name="message" required></textarea></div>'
  '<button type="submit" class="btn btn-primary btn-lg">Send message</button>'
  '<p class="note" style="margin-top:1rem">Messages are emailed to the Coalition at info@wpbrc.org. (First-time note: FormSubmit sends a one-time confirmation link to that inbox to activate the form.)</p>'
  '</form>')
s=re.sub(r'<form data-demo>.*?</form>', lambda m: contact_form, s, flags=re.S)
s+=FOOT+"\n</body>\n</html>"
write("contact.html",s)





# ---------------- BLOG (index + individual post pages) ----------------
def render_body(body):
    b=(body or "").strip()
    if b.startswith("<"): return body
    try:
        import markdown; return markdown.markdown(body)
    except Exception:
        return "".join("<p>"+para.strip().replace("\n","<br>")+"</p>" for para in b.split("\n\n") if para.strip())

_bd=json.load(open(OUT+"/assets/blog.json"))
_posts=[p for p in _bd["posts"] if p.get("approved")!=False]
# index
s=head("Blog | "+ORG,"News and non-partisan analysis from the West Palm Beach Residents Coalition on development, public meetings, and citywide issues.","blog.html")
s+=header("blog.html")+'<main id="main">'
s+=hero("Blog","News &amp; analysis.","Updates on development projects, public meetings, and the issues shaping West Palm Beach &mdash; in plain language, with sources.",small=True)
_cards=""
for p in _posts:
    _cards+=('<a class="card hover postcard" href="'+p["slug"]+'">'
        '<span class="tag">'+html.escape(p.get("tag","Update"))+'</span>'
        '<h3 style="margin-top:.6rem">'+html.escape(p["title"])+'</h3>'
        '<p class="meta note">'+html.escape(p.get("displayDate",""))+' &middot; '+html.escape(p.get("author","WPBRC"))+'</p>'
        '<p>'+html.escape(p.get("excerpt",""))+'</p>'
        '<span class="readmore">Read more &rsaquo;</span></a>')
s+='<section class="section"><div class="container"><div class="grid grid-3">'+_cards+'</div></div></section>'
s+=('<section class="section sand" id="newsletter"><div class="container" style="max-width:720px">'
    '<div class="section-head center" style="margin-inline:auto"><p class="eyebrow">Stay informed</p><h2>Subscribe to our newsletter</h2>'
    '<p class="lead">Get new posts, development updates, and meeting alerts by email.</p></div>'
    '<div class="embed-wrap" style="--embed-h:540px"><iframe title="Signup form powered by Zeffy" style="position:absolute;border:0;top:0;left:0;bottom:0;right:0;width:100%;height:100%" src="'+ZEFFY["newsletter"]+'" allowTransparency="true"></iframe></div>'
    '</div></section>')
s+=FOOT+"\n</body>\n</html>"
write("blog.html",s)
# individual post pages
for p in _posts:
    a=head(p["title"]+" | "+ORG, p.get("excerpt","")[:180], p["slug"])
    a+=header("blog.html")+'<main id="main">'
    a+=('<section class="hero hero-sm"><div class="container">'
        '<p class="eyebrow" style="color:var(--gold)">Blog</p>'
        '<h1>'+html.escape(p["title"])+'</h1>'
        '<p>'+html.escape(p.get("displayDate",""))+' &middot; '+html.escape(p.get("author","WPBRC"))+'</p>'
        '</div></section>')
    a+=('<section class="section"><div class="container article">'
        '<p><a href="blog.html" class="note">&laquo; All posts</a></p>'
        + render_body(p["body"]) +
        '<p class="reviewed">Posted '+html.escape(p.get("displayDate",""))+' by '+html.escape(p.get("author","WPBRC"))+'.</p>'
        '<p style="margin-top:1.5rem"><a href="join.html" class="btn btn-primary">Join the Coalition</a> '
        '<a href="events.html#newsletter" class="btn btn-ghost">Get the newsletter</a></p>'
        '</div></section>')
    a+=FOOT+"\n</body>\n</html>"
    write(p["slug"],a)


# ---------------- CUSTOM PAGES (CMS: content/pages/*.md) ----------------
for pg in CUSTOM_PAGES:
    _slug=pg["slug"]; _title=str(pg.get("title","Page"))
    _desc=str(pg.get("meta_description") or pg.get("subtitle") or _title)
    cp=head(f"{_title} | {ORG}", _desc, _slug)
    cp+=header(_slug)+'<main id="main">'
    cp+=hero(str(pg.get("eyebrow","Coalition")), _title, str(pg.get("subtitle","")), small=True)
    cp+='<section class="section"><div class="container" style="max-width:880px">'+render_md(pg.get("body",""))+'</div></section>'
    cp+='</main>'+FOOT+"\n</body>\n</html>"
    write(_slug, cp)

# ---------------- TECHNICAL SEO ----------------
order=[("","1.0"),("issues.html","0.9"),("development.html","0.9"),("resources.html","0.8"),("about.html","0.8"),("neighborhoods.html","0.8"),("blog.html","0.7"),
       ("join.html","0.8"),("events.html","0.7"),("media.html","0.6"),("board.html","0.6"),("donate.html","0.7"),("contact.html","0.6")]
order+=[(p["slug"],"0.6") for p in _posts]
order+=[(pg["slug"],"0.6") for pg in CUSTOM_PAGES]
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for p,pr in order:
    loc=f"{BASE}/{p}" if p else f"{BASE}/"
    sm.append(f"  <url><loc>{loc}</loc><changefreq>monthly</changefreq><priority>{pr}</priority></url>")
sm.append("</urlset>")
open(os.path.join(OUT,"sitemap.xml"),"w").write("\n".join(sm))
open(os.path.join(OUT,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")
llms_lines=[
 "# "+ORG+" (WPBRC)",
 "> "+TAGLINE+" A citywide, non-partisan 501(c)(4) giving West Palm Beach residents a coordinated voice on",
 "> growth/development, infrastructure, resilience, transparency, public safety, mobility, and waterfront planning.",
 "",
 "## Pages",
 "- [Home]("+BASE+"/): Mission, focus areas, get involved.",
 "- [About]("+BASE+"/about.html): Purpose, priorities, governance.",
 "- [Current Issues]("+BASE+"/issues.html): Six citywide issues with why-it-matters, key dates, studies, meetings, Coalition position, and plan of action.",
 "- [Resources]("+BASE+"/resources.html): How local government works \u2014 commission districts, commissioner contacts, public records, how development is approved, the DAC, the Planning Board, county vs city.",
 "- [Media]("+BASE+"/media.html): Press coverage and mentions relevant to the Coalition.",
 "- [Development Tracker]("+BASE+"/development.html): Interactive map of WPB development projects by status/district.",
 "- [Neighborhoods]("+BASE+"/neighborhoods.html): Directory of WPB neighborhood associations.",
 "- [Board]("+BASE+"/board.html): Board and officer roles.",
 "- [Events]("+BASE+"/events.html): Events, meetings to track, newsletter.",
 "- [Join]("+BASE+"/join.html): Membership categories and sign-up (Zeffy).",
 "- [Donate and Sponsor]("+BASE+"/donate.html): Support the Coalition via Zeffy.",
 "- [Contact]("+BASE+"/contact.html): Reach the Coalition (emails info@wpbrc.org).",
 "",
]
open(os.path.join(OUT,"llms.txt"),"w").write("\n".join(llms_lines))
# validate nav links point to real files
import glob as _g
_exist=set(os.path.basename(x) for x in _g.glob(os.path.join(OUT,"*.html")))
for _u,_l in NAV:
    if _u and _u not in _exist:
        print("WARNING: nav item '"+_l+"' -> "+_u+" has no page file.")
print("ALL_DONE")
