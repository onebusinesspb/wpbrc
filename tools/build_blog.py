#!/usr/bin/env python3
"""
WPBRC — (re)build the Blog from assets/blog.json.

Generates blog.html (index) and one page per post (post-<id>.html), reusing the
site's current header/footer/styles so the blog always matches the rest of the site.

USAGE:  python3 build_blog.py      (run from the tools/ folder)
Then redeploy (or it's already in your site folder).
"""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..")
BASE = "https://wpbrc.org"

# Reuse header/footer/head from an existing page so the blog stays in sync.
tpl = open(os.path.join(SITE, "neighborhoods.html"), encoding="utf-8").read()
head_tpl = tpl[:tpl.index("</head>") + len("</head>")]
header_html = re.search(r"<header.*?</header>", tpl, re.S).group(0)
footer_html = re.search(r"<footer.*?</footer>", tpl, re.S).group(0)
tail = tpl[tpl.index('<div id="donate-modal"'):] if '<div id="donate-modal"' in tpl else '\n<script src="assets/site.js"></script>\n</body>\n</html>'
# nav: clear any active item, then we set Blog active per page
header_html = header_html.replace(' class="active"', '')

def make_head(title, desc, slug, bodycls, crumbname=None, extra_ld=""):
    h = head_tpl
    h = re.sub(r"<title>.*?</title>", "<title>" + html.escape(title) + "</title>", h, flags=re.S)
    h = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1)+html.escape(desc)+m.group(2), h)
    h = re.sub(r'(<meta property="og:title" content=")[^"]*(")', lambda m: m.group(1)+html.escape(title)+m.group(2), h)
    h = re.sub(r'(<meta property="og:description" content=")[^"]*(")', lambda m: m.group(1)+html.escape(desc)+m.group(2), h)
    h = re.sub(r'(<link rel="canonical" href=")[^"]*(")', lambda m: m.group(1)+BASE+"/"+slug+m.group(2), h)
    h = re.sub(r'(<meta property="og:url" content=")[^"]*(")', lambda m: m.group(1)+BASE+"/"+slug+m.group(2), h)
    # rebuild the BreadcrumbList for THIS page (template carries the source page's crumb)
    # the template page carries its own FAQPage/Speakable schema — remove it for blog pages
    h = re.sub(r'<script type="application/ld\+json">\{"@context":[^<]*?"FAQPage".*?</script>\s*', '', h, flags=re.S)
    h = re.sub(r'<script type="application/ld\+json">\{"@context":[^<]*?"SpeakableSpecification".*?</script>\s*', '', h, flags=re.S)
    cn = crumbname or title.split("|")[0].strip()
    crumb = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":cn,"item":BASE+"/"+slug}]}
    _crumb_ld = '<script type="application/ld+json">'+json.dumps(crumb)+'</script>'
    h = re.sub(r'<script type="application/ld\+json">\{"@context":[^<]*?"BreadcrumbList".*?</script>',
               lambda m: _crumb_ld, h, flags=re.S)
    if extra_ld:
        h = h.replace("</head>", extra_ld + "\n</head>")
    return h + '\n<body class="page-' + bodycls + '">\n<a class="skip-link" href="#main">Skip to content</a>'

def nav(active_blog=True):
    return header_html.replace('<a href="blog.html">Blog</a>', '<a href="blog.html" class="active">Blog</a>') if active_blog else header_html

def write(name, content):
    open(os.path.join(SITE, name), "w", encoding="utf-8").write(content)
    print("wrote", name)

data = json.load(open(os.path.join(SITE, "assets", "blog.json"), encoding="utf-8"))
posts = data["posts"]

# ---- index ----
cards = ""
for p in posts:
    cards += ('<a class="card hover postcard" href="' + p["slug"] + '">'
        '<span class="tag">' + html.escape(p.get("tag", "Update")) + '</span>'
        '<h3 style="margin-top:.6rem">' + html.escape(p["title"]) + '</h3>'
        '<p class="meta note">' + html.escape(p.get("displayDate", "")) + ' &middot; ' + html.escape(p.get("author", "WPBRC")) + '</p>'
        '<p>' + html.escape(p.get("excerpt", "")) + '</p>'
        '<span class="readmore">Read more &rsaquo;</span></a>')
idx = make_head("Blog | West Palm Beach Residents Coalition",
                "News and non-partisan analysis on development, public meetings, and citywide issues.",
                "blog.html", "blog")
idx += nav() + '<main id="main">'
idx += ('<section class="hero hero-sm"><div class="container">'
        '<p class="tagline">Stronger Neighborhoods. Stronger Community.</p>'
        '<p class="eyebrow" style="color:var(--gold)">Blog</p><h1>News &amp; analysis.</h1>'
        '<p>Updates on development projects, public meetings, and the issues shaping West Palm Beach.</p></div></section>')
idx += '<section class="section"><div class="container"><div class="grid grid-3">' + cards + '</div></div></section>'
idx += footer_html + "\n" + tail
write("blog.html", idx)

# ---- post pages ----
for p in posts:
    _bp = {"@context":"https://schema.org","@type":"BlogPosting",
           "headline": p["title"], "datePublished": p.get("date",""), "dateModified": p.get("date",""),
           "author": {"@type":"Organization","name": p.get("author","WPBRC")},
           "publisher": {"@type":"Organization","name":"West Palm Beach Residents Coalition",
                         "logo":{"@type":"ImageObject","url": BASE+"/assets/wpbrc-logo.png"}},
           "mainEntityOfPage": BASE+"/"+p["slug"], "description": p.get("excerpt","")}
    _bp_ld = '<script type="application/ld+json">'+json.dumps(_bp)+'</script>'
    page = make_head(p["title"], p.get("excerpt", "")[:180], p["slug"], "post-" + p["id"], crumbname=p["title"], extra_ld=_bp_ld)
    page += nav() + '<main id="main">'
    page += ('<section class="hero hero-sm"><div class="container">'
             '<p class="eyebrow" style="color:var(--gold)">Blog</p><h1>' + html.escape(p["title"]) + '</h1>'
             '<p>' + html.escape(p.get("displayDate", "")) + ' &middot; ' + html.escape(p.get("author", "WPBRC")) + '</p></div></section>')
    page += ('<section class="section"><div class="container article">'
             '<p><a href="blog.html" class="note">&laquo; All posts</a></p>' + p["body"] +
             '<p class="reviewed">Posted ' + html.escape(p.get("displayDate", "")) + ' by ' + html.escape(p.get("author", "WPBRC")) + '.</p>'
             '<p style="margin-top:1.5rem"><a href="join.html" class="btn btn-primary">Join the Coalition</a> '
             '<a href="events.html#newsletter" class="btn btn-ghost">Get the newsletter</a></p></div></section>')
    page += footer_html + "\n" + tail
    write(p["slug"], page)

print("Blog rebuilt:", len(posts), "posts +", 1, "index.")
