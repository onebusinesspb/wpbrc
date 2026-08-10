# No-code editing (CMS) — setup & use

Your site now has a free, open-source admin at **/admin/** so Board members can edit
content through simple web forms — no coding. It uses **Sveltia CMS** (a maintained,
drop-in replacement for Decap/Netlify CMS) on top of your existing static site. There
is still **no database and no server to maintain**: editors save changes, and Netlify
rebuilds and republishes the site automatically.

## What editors can change from /admin/
- 🗺️ **Development Tracker** — add/update projects and statuses (the map).
- 👥 **Board of Directors** — names, roles, neighborhood, years in WPB, bios.
- 📌 **Current Issues** — the six issues and all their fields.
- 📅 **Calendar / Events** — upcoming meetings and events.
- 📰 **Media / Press** — coverage entries.
- 🏘️ **Neighborhood Directory** — the associations list.

(Page prose like the mission statement lives in the site generator and is edited by
your web help — it changes rarely. Everything that changes often is in the CMS.)

## How updates flow (automatic)
1. An editor changes something at `wpbrc.org/admin/` and clicks **Save/Publish**.
2. That saves to the site's files (a commit) on GitHub.
3. Netlify sees the change, runs `python3 build.py` (regenerates the pages from the
   updated data), and republishes — live in about a minute.

`netlify.toml` and `build.py` are already in the project to make this work.

## One-time setup
You need the site connected to **GitHub + Netlify** (drag-and-drop deploys can't run
the CMS login or the rebuild). Steps:

1. **Put the site in a GitHub repo.** Push the contents of the `WPBRC-Website` folder to
   a new repository (the folder's files should be at the repo root, so `index.html` is
   at the top level).
2. **Connect the repo to Netlify.** New site → Import from Git → pick the repo. Netlify
   reads `netlify.toml` automatically: build command `python3 build.py`, publish `.`.
3. **Add your domain** (`wpbrc.org`) in Netlify → Domain settings, set it primary; SSL
   is automatic. (Your IONOS DNS already points to Netlify.)
4. **Turn on login (pick one):**
   - **Easiest — email invites (git-gateway):** Netlify → *Identity* → Enable Identity →
     enable **Git Gateway** → *Invite users* (add each Board editor's email). This matches
     the default `backend: git-gateway` in `admin/config.yml`.
   - **Durable — GitHub logins:** in `admin/config.yml` switch to the commented `github`
     backend and set `repo: your-org/wpbrc-website`. Editors sign in with GitHub accounts.
5. **Log in** at `https://wpbrc.org/admin/` and try editing one item to confirm.

> Note: Netlify Identity still works but Netlify has signaled it's winding down for new
> features. If you're setting this up fresh and want the most future-proof option, use
> the **GitHub** backend (step 4, second bullet).

## Editing tips
- **Map coordinates:** to place a pin exactly, right-click the building in Google Maps,
  click the latitude/longitude to copy, and paste into the Latitude/Longitude fields.
- **IDs must be unique** and lowercase-with-dashes (e.g. `one-flagler`).
- **Images:** the CMS stores uploads in `assets/uploads/`. To replace a banner, overwrite
  the matching `assets/hero-*-wc.jpg` file in the repo (same filename).
- **Undo:** every change is versioned in GitHub; you can roll back any deploy in Netlify.

## If you'd rather not use GitHub/Netlify
The site still works as plain drag-and-drop on Netlify — you'd just edit the JSON files
by hand and re-run `python3 build.py` locally before dragging the folder. The CMS and
auto-rebuild specifically require the GitHub + Netlify connection above.
