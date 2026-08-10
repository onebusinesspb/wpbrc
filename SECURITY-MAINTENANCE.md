# Security & maintenance — how the site stays safe (and low-effort)

Your website is a **static site** (plain files on Netlify — no server, no database,
no WordPress/PHP). That removes the biggest sources of website vulnerabilities: there's
no admin server to hack, no database to breach, no plugins to exploit. What remains is a
small, well-understood surface — and it's monitored automatically, for **free, with no
AI/API cost**.

## What's watching the site

**1. Dependabot (built into GitHub, free).**
Watches the few software packages the site uses (`requirements.txt`) and the GitHub
Action versions, and **opens a Pull Request whenever a security fix or update is
available**. You review and click **Merge** to apply — Netlify redeploys automatically.
GitHub also emails security alerts for known vulnerabilities.

**2. Weekly "Site health & security" check (free GitHub Action).**
Every Monday (and any time you run it from the Actions tab) it verifies:
- the site is **up** (HTTP 200) and the **SSL certificate** isn't expiring soon;
- the **integrations** work — Zeffy donation & newsletter forms, the contact form
  endpoint, the map/CMS CDN libraries, and the OpenStreetMap tiles;
- **no broken links** — internal pages and external links (city.gov, petitions, etc.);
- whether a **library update** is available (pinned version vs. latest).

If anything is wrong it **opens a GitHub Issue** titled "Site health & security — action
needed" with the details, and (if you add email settings) emails the report. GitHub also
emails the repo owner automatically when a scheduled run fails.

**3. Security headers (Netlify).**
`netlify.toml` sets hardening headers on every page: HSTS (force HTTPS), a Content
Security Policy (limits what can load/run), `X-Content-Type-Options`, `X-Frame-Options`,
`Referrer-Policy`, and `Permissions-Policy`. The `/admin` editor gets a relaxed policy so
it's never blocked.

## What to do when you get an alert

| Alert | What it means | What to do |
|-------|----------------|------------|
| Dependabot PR | A package has an update/fix | Open the PR, glance at it, **Merge**. Done. |
| "update available" in the health report | A library (e.g. Leaflet) has a newer version | Bump the version in the code (or ask web help); low urgency. |
| Broken integration (Zeffy/CDN/OSM) | A form or the map may be failing | Check the service's status; re-copy the Zeffy embed link if it changed. |
| Broken link | A page or external site moved | Fix the link in the CMS (internal) or Resources/Issues (external). |
| SSL expiring | Certificate renewal issue | Netlify auto-renews; if it persists, check Netlify → Domain settings. |
| Site down | Hosting/DNS problem | Check Netlify status and your IONOS DNS. |

## One-time setup (with the rest of the GitHub/Netlify connection)
1. Push the site to GitHub and connect Netlify (same as the CMS setup).
2. Dependabot and the health Action start working automatically (files are in `.github/`).
3. **Optional email:** to also email the health report, add these repository secrets
   (Settings → Secrets → Actions): `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`,
   `MAIL_PASSWORD`, `MAIL_TO` (e.g. info@wpbrc.org). Without them, you still get the
   GitHub Issue + GitHub's built-in failure emails.
4. Turn on GitHub's free **Dependabot alerts** and **secret scanning** in
   Settings → Code security (public repos get these free).

## The honest bottom line
Because there's no server or database, routine "patch everything" work is minimal. The
realistic maintenance is: **merge the occasional Dependabot PR, and act on the rare health
alert.** Most weeks there will be nothing to do — and you'll be *told* if there is.

*Detection is automated and free. Applying a fix is a human click. A deeper "AI explains
the vulnerability" layer is possible but would use a paid LLM — not needed for this site.*
