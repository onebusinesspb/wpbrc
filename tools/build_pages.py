#!/usr/bin/env python3
"""
WPBRC — build the Issues, Resources, and Media pages from their JSON data,
reusing the site's current header/footer/styles (run AFTER build_site2.py).

USAGE:  python3 build_pages.py      (run from the tools/ folder)
"""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..")
BASE = "https://wpbrc.org"

# Reuse header/footer/head from board.html (clean schema: NGO + WebSite + Breadcrumb)
tpl = open(os.path.join(SITE, "board.html"), encoding="utf-8").read()
head_tpl = tpl[:tpl.index("</head>") + len("</head>")]
header_html = re.search(r"<header.*?</header>", tpl, re.S).group(0)
footer_html = re.search(r"<footer.*?</footer>", tpl, re.S).group(0)
# modal + script tail (everything from the donate modal to </html>)
tail = tpl[tpl.index('<div id="donate-modal"'):] if '<div id="donate-modal"' in tpl else '\n<script src="assets/site.js"></script>\n</body>\n</html>'
header_html = header_html.replace(' class="active"', '')

def nav(active):
    return header_html.replace('<a href="'+active+'">', '<a href="'+active+'" class="active">', 1)

def make_head(title, desc, slug, bodycls, crumbname=None):
    h = head_tpl
    h = re.sub(r"<title>.*?</title>", "<title>" + html.escape(title) + "</title>", h, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1)+html.escape(desc)+m.group(2), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1)+html.escape(title)+m.group(2), h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1)+html.escape(desc)+m.group(2), h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1)+BASE+"/"+slug+m.group(2), h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1)+BASE+"/"+slug+m.group(2), h)
    h = re.sub(r'(<body class="page-)[^"]*(")', lambda m: m.group(1)+bodycls+m.group(2), h) if 'class="page-' in h else h
    cn = crumbname or title.split("|")[0].strip()
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":cn,"item":BASE+"/"+slug}]}
    crumb_ld = '<script type="application/ld+json">'+json.dumps(crumb)+'</script>'
    h = re.sub(r'<script type="application/ld\+json">\{"@context":[^<]*?"BreadcrumbList".*?</script>',
               lambda m: crumb_ld, h, flags=re.S)
    return h + '\n<body class="page-' + bodycls + '">\n<a class="skip-link" href="#main">Skip to content</a>'

def hero_sm(eyebrow, h1, sub):
    return ('<section class="hero hero-sm"><div class="container">'
            '<p class="tagline">Stronger Neighborhoods. Stronger Community.</p>'
            '<p class="eyebrow" style="color:var(--gold)">'+eyebrow+'</p><h1>'+h1+'</h1>'
            '<p>'+sub+'</p></div></section>')

def write(name, content):
    open(os.path.join(SITE, name), "w", encoding="utf-8").write(content)
    print("wrote", name)

# replace the body-class in the extracted head template per page (head_tpl is from board.html -> page-board)
def head_for(title, desc, slug, cls, crumbname=None):
    h = make_head(title, desc, slug, cls, crumbname)
    return h

# ---------------- ISSUES ----------------
data = json.load(open(os.path.join(SITE, "assets", "issues.json"), encoding="utf-8"))
issues = data["issues"]
note = data["_meta"].get("statusNote", "")

def lst(items):
    return "<ul>" + "".join("<li>"+html.escape(x)+"</li>" for x in items) + "</ul>"

def studies_lst(items):
    out = ""
    for x in items:
        if x.get("url"):
            out += '<li><a href="'+html.escape(x["url"])+'" rel="noopener" target="_blank">'+html.escape(x["label"])+'</a></li>'
        else:
            out += "<li>"+html.escape(x["label"])+"</li>"
    return "<ul>"+out+"</ul>"

def petitions_html(items):
    if not items: return ""
    btns = ""
    for p in items:
        url = p["url"]
        cls = "btn btn-primary" if "protectthepalm" in url else "btn btn-secondary"
        disabled = ' aria-disabled="true" title="Add the Save WPB petition link"' if url.startswith("REPLACE") else ''
        href = url if not url.startswith("REPLACE") else "#"
        btns += '<a href="'+html.escape(href)+'" class="'+cls+'"'+disabled+' rel="noopener" target="_blank">'+html.escape(p["label"])+'</a> '
    return '<div class="petitions"><p class="eyebrow gold mb-0">Take action</p>'+btns+'</div>'

cards = ""
toc = ""
for it in issues:
    toc += '<a class="chip" href="#'+it["id"]+'">'+html.escape(it["title"])+'</a>'
    cards += ('<section class="issue-block" id="'+it["id"]+'">'
        '<div class="issue-head"><span class="tag '+("alert" if it.get("tag")=="Active" else "")+'">'+html.escape(it.get("tag","Watching"))+'</span>'
        '<h2 class="mb-0">'+html.escape(it["title"])+'</h2></div>'
        '<p class="lead">'+html.escape(it.get("summary",""))+'</p>'
        + petitions_html(it.get("petitions"))
        + '<div class="grid grid-2 issue-fields">'
        '<div class="card"><h3>Why it matters</h3><p>'+html.escape(it.get("why",""))+'</p></div>'
        '<div class="card"><h3>Coalition position</h3><p>'+html.escape(it.get("position",""))+'</p></div>'
        '<div class="card"><h3>Key dates</h3>'+lst(it.get("keyDates",[]))+'</div>'
        '<div class="card"><h3>Upcoming meetings</h3>'+lst(it.get("meetings",[]))+'</div>'
        '<div class="card"><h3>Relevant studies</h3>'+studies_lst(it.get("studies",[]))+'</div>'
        '<div class="card"><h3>Plan of action</h3>'+lst(it.get("plan",[]))+'</div>'
        '</div></section>')

p = head_for("Current Issues | West Palm Beach Residents Coalition",
             "The citywide issues the West Palm Beach Residents Coalition is tracking — Downtown Master Plan, traffic and mobility, infrastructure, public safety, waterfront, and the development pipeline — with why each matters, key dates, studies, meetings, our position, and plan of action.",
             "issues.html", "issues")
p += nav("issues.html") + '<main id="main">'
p += hero_sm("Current Issues", "The issues shaping West Palm Beach.",
             "Six citywide issues we track closely — with why each matters, key dates, relevant studies, upcoming meetings, the Coalition’s position, and our plan of action.")
p += '<section class="section"><div class="container">'
p += '<p class="note" style="margin-top:0">'+html.escape(note)+'</p>'
p += '<div class="chips">'+toc+'</div>'
p += cards
p += '<p class="reviewed">Last reviewed: June 2026. Verify dates and studies against official City of West Palm Beach agendas.</p>'
p += '</div></section></main>'
p += footer_html + tail
write("issues.html", p)

# ---------------- RESOURCES ----------------
def block(eyebrow, title, body):
    return ('<section class="section"><div class="container" style="max-width:880px">'
            '<p class="eyebrow">'+eyebrow+'</p><h2>'+title+'</h2>'+body+'</div></section>')

CITY = "https://www.wpb.org"
res_body = ""
res_body += block("Start here", "How West Palm Beach city government works",
    '<p class="lead">West Palm Beach is governed by a Mayor and a five-member City Commission, each elected from a district. Land-use and development decisions move through advisory boards and the Commission in public meetings. This page is a plain-language guide for residents — a work in progress.</p>'
    '<p class="note">Content in progress — the Coalition’s civics deck is being adapted into this page. Official links are provided below in the meantime.</p>')

res_body += block("Districts", "Commission district map",
    '<p>West Palm Beach has five commission districts, each represented by one commissioner. Find your district and commissioner on the city’s official map.</p>'
    '<div class="placeholder-map"><p>Commission district map — to be embedded.<br><a class="btn btn-secondary" href="'+CITY+'/government/city-commission" target="_blank" rel="noopener">Find your district &amp; commissioner &rsaquo;</a></p></div>')

res_body += block("Contacts", "Commissioner contact information",
    '<p>Contact information for the Mayor and each district commissioner. (We’ll publish a clean table here; verify against the city site.)</p>'
    '<table class="dir"><thead><tr><th>Office</th><th>District</th><th>Contact</th></tr></thead><tbody>'
    '<tr><td>Mayor</td><td>Citywide</td><td><a href="'+CITY+'/government/mayor" target="_blank" rel="noopener">wpb.org</a></td></tr>'
    '<tr><td>Commissioner</td><td>District 1</td><td>To be added</td></tr>'
    '<tr><td>Commissioner</td><td>District 2</td><td>To be added</td></tr>'
    '<tr><td>Commissioner</td><td>District 3</td><td>To be added</td></tr>'
    '<tr><td>Commissioner</td><td>District 4</td><td>To be added</td></tr>'
    '<tr><td>Commissioner</td><td>District 5</td><td>To be added</td></tr>'
    '</tbody></table>')

res_body += block("Transparency", "Public records request guide",
    '<p>Florida’s public-records law (Chapter 119) gives residents broad rights to inspect and copy government records. In general:</p>'
    '<ol><li>Identify the record you want as specifically as possible (dates, department, topic).</li>'
    '<li>Submit a request to the City Clerk or the relevant department — in writing is best for tracking.</li>'
    '<li>You do not have to say why you want the records.</li>'
    '<li>The city may charge reasonable copying/labor fees for extensive requests.</li>'
    '<li>Records should be produced within a reasonable time.</li></ol>'
    '<p><a class="btn btn-secondary" href="'+CITY+'/government/city-clerk" target="_blank" rel="noopener">City Clerk / records &rsaquo;</a></p>')

res_body += block("Process", "How development is approved",
    '<p>Most major projects follow a public path before they’re built:</p>'
    '<ol><li><strong>Application &amp; staff review</strong> — the developer files plans; city planning staff review them against the code and Comprehensive Plan.</li>'
    '<li><strong>Advisory boards</strong> — depending on location and type, the project may go to the Planning Board and/or the Downtown Action Committee (DAC) for recommendation.</li>'
    '<li><strong>City Commission</strong> — the elected Commission holds public hearings and makes the final decision on rezonings, variances, and major approvals.</li>'
    '<li><strong>Public comment</strong> — residents may speak at these public meetings; agendas are posted in advance.</li></ol>')

res_body += block("Boards", "Understanding the DAC (Downtown Action Committee)",
    '<p>The Downtown Action Committee reviews projects within the downtown district and makes recommendations on design and development consistent with the Downtown Master Plan. It is an advisory body — final decisions rest with the City Commission. Agendas and dates are posted on the city’s Planning Division pages.</p>'
    '<p><a class="btn btn-secondary" href="'+CITY+'/Departments/Development-Services/Planning-Division/Boards-and-Committees" target="_blank" rel="noopener">Boards &amp; committees &rsaquo;</a></p>')

res_body += block("Boards", "Understanding the Planning Board",
    '<p>The Planning Board reviews rezonings, future land-use changes, and major development proposals citywide, then makes recommendations to the City Commission. Like the DAC, it is advisory; the Commission casts the binding votes.</p>')

res_body += block("Jurisdiction", "County vs. City responsibilities",
    '<p>It helps to know who decides what:</p>'
    '<ul><li><strong>City of West Palm Beach</strong> — local zoning and land use, city streets, water/sewer utilities, city parks, police and fire-rescue, code enforcement.</li>'
    '<li><strong>Palm Beach County</strong> — county roads, the Property Appraiser and Tax Collector, the Supervisor of Elections, county courts, and services in unincorporated areas.</li>'
    '<li><strong>Regional / other</strong> — the Transportation Planning Agency (TPA) for regional mobility; the School District for public schools.</li></ul>')

res_body += block("Directory", "Local organizations &amp; government",
    '<p>Quick links to the agencies, boards, and organizations residents work with most.</p>'
    '<div class="grid grid-2">'
    '<div class="card"><h3>City of West Palm Beach</h3><ul>'
    '<li><a href="https://www.wpb.org" target="_blank" rel="noopener">City of WPB (wpb.org)</a></li>'
    '<li><a href="https://www.wpb.org/government/city-commission" target="_blank" rel="noopener">City Commission &amp; districts</a></li>'
    '<li><a href="https://www.wpb.org/government/mayor" target="_blank" rel="noopener">Office of the Mayor</a></li>'
    '<li><a href="https://www.wpb.org/government/city-clerk" target="_blank" rel="noopener">City Clerk / public records</a></li>'
    '<li><a href="https://www.wpb.org/Departments/Development-Services/Planning-Division" target="_blank" rel="noopener">Planning Division</a></li>'
    '<li><a href="https://www.wpb.org/Departments/Development-Services/Planning-Division/Boards-and-Committees" target="_blank" rel="noopener">Boards &amp; committees (Planning Board, DAC)</a></li>'
    '</ul></div>'
    '<div class="card"><h3>County &amp; regional</h3><ul>'
    '<li><a href="https://discover.pbc.gov" target="_blank" rel="noopener">Palm Beach County</a></li>'
    '<li><a href="https://www.pbcpao.gov" target="_blank" rel="noopener">Property Appraiser</a></li>'
    '<li><a href="https://www.votepalmbeach.gov" target="_blank" rel="noopener">Supervisor of Elections</a></li>'
    '<li><a href="https://www.mypalmbeachclerk.com" target="_blank" rel="noopener">Clerk of the Circuit Court</a></li>'
    '<li><a href="https://www.palmbeachtpa.org" target="_blank" rel="noopener">Palm Beach Transportation Planning Agency</a></li>'
    '</ul></div>'
    '<div class="card"><h3>Neighborhood &amp; civic</h3><ul>'
    '<li><a href="https://www.wpbdna.com" target="_blank" rel="noopener">WPB Downtown Neighborhood Association</a></li>'
    '<li><a href="neighborhoods.html">WPBRC neighborhood directory</a></li>'
    '<li><a href="https://protectthepalm.com/" target="_blank" rel="noopener">Protect the Palm</a></li>'
    '</ul></div>'
    '<div class="card"><h3>Plans &amp; studies</h3><ul>'
    '<li><a href="https://www.wpb.org/Departments/Development-Services/Planning-Division/Downtown-Master-Plan" target="_blank" rel="noopener">Downtown Master Plan</a></li>'
    '<li><a href="issues.html">WPBRC current issues &amp; positions</a></li>'
    '<li><a href="development.html">WPBRC Development Tracker</a></li>'
    '</ul></div>'
    '</div>'
    '<p class="note" style="margin-top:1rem">Know a resource we should add? <a href="contact.html">Let us know</a>.</p>')

p = head_for("Resources | How Local Government Works | WPBRC",
             "A resident’s guide to how West Palm Beach city government works — commission districts, commissioner contacts, public records requests, how development is approved, the DAC, the Planning Board, and county vs. city responsibilities.",
             "resources.html", "resources")
p += nav("resources.html") + '<main id="main">'
p += hero_sm("Resources", "Know how your city works.",
             "Many residents have no idea how local government actually makes decisions. This is a plain-language guide — districts, contacts, public records, and how development gets approved.")
p += res_body
p += '<section class="section center"><div class="container" style="max-width:680px"><h2>Spot something out of date?</h2><p class="lead">Help us keep this accurate. <a href="contact.html">Tell us &rsaquo;</a></p></div></section>'
p += '</main>' + footer_html + tail
write("resources.html", p)

# ---------------- MEDIA ----------------
mdata = json.load(open(os.path.join(SITE, "assets", "media.json"), encoding="utf-8"))
items = [m for m in mdata.get("items", []) if m.get("approved") is not False]
rows = ""
for m in items:
    title = html.escape(m.get("title",""))
    if m.get("url"):
        title = '<a href="'+html.escape(m["url"])+'" target="_blank" rel="noopener">'+title+'</a>'
    rows += ('<article class="card postcard"><span class="tag">'+html.escape(m.get("outlet","Press"))+'</span>'
             '<h3 style="margin-top:.5rem">'+title+'</h3>'
             '<p class="meta note">'+html.escape(m.get("displayDate",""))+'</p>'
             '<p>'+html.escape(m.get("excerpt",""))+'</p></article>')

p = head_for("Media & Press | West Palm Beach Residents Coalition",
             "Press coverage and media mentions relevant to the West Palm Beach Residents Coalition and citywide growth, development, and planning issues.",
             "media.html", "media")
p += nav("media.html") + '<main id="main">'
p += hero_sm("Media", "In the news.",
             "Coverage and mentions relevant to the Coalition and the citywide issues we track. This page is kept current with a weekly draft-then-approve review.")
p += '<section class="section"><div class="container">'
p += '<div class="grid grid-3">'+rows+'</div>'
p += '<p class="note" style="margin-top:1.4rem">Are you a reporter? Reach our Communications Chair via the <a href="contact.html">contact form</a> (select “Media / press inquiry”).</p>'
p += '</div></section></main>'
p += footer_html + tail
write("media.html", p)

print("Built issues.html, resources.html, media.html")
