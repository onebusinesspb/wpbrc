# Free, open-source scouts — approved in the CMS (no pull requests)

These run the **development** and **events** scouts on GitHub's free servers, on a
schedule, using only open-source Python — **no LLM, no API key, no cost.** New
finds are added to the site's data as **pending (hidden)**, and a Board member
**approves them in the CMS with one toggle**. No pull requests, no code.

## How it works
1. On schedule, the scout finds new items from the WPB sources you configure.
2. It appends each as **`approved: false`** to the data file and commits to `main`.
   Pending items are **hidden on the public site** (the map, calendar, media, and
   blog all skip anything marked not-approved).
3. A Board member opens **`/admin`**, finds the pending item (its **"Show on site
   (approved)"** toggle is OFF), reviews/fixes it, flips the toggle **ON**, and saves.
4. Netlify rebuilds — the item goes live in about a minute.

So the machine drafts; a human approves in the friendly CMS; nothing appears until
someone says so.

## What's included
- `.github/workflows/weekly-scouts.yml` — schedule (Mon = development, Thu = events) + auto-commit.
- `tools/scout_development.py` — appends pending **projects** to `assets/projects.json` (best-effort free geocoding via OpenStreetMap Nominatim; flags "COORDINATES NEEDED" when unsure).
- `tools/scout_events.py` — appends pending **events** to `assets/events.json` (next 60 days, keyword-matched).
- `tools/scout_config.json` — **you edit this**: the WPB source URLs + keywords.

## One-time setup
1. Site must be on **GitHub** (already needed for the CMS) — the Action commits there.
2. Edit `tools/scout_config.json` with real WPB sources:
   - Events: the City calendar's **iCal (.ics)** link and/or an RSS feed.
   - Development: the **Planning Board / DAC agendas** page (pre-filled) and any RSS.
3. Commit. The workflow runs on schedule; you can also run it any time from the repo's
   **Actions** tab → *Weekly scouts* → *Run workflow*.

## Approving (the whole job)
- Open `/admin` → **Calendar / Events** or **Development Tracker**.
- Pending items have **"Show on site (approved)" = OFF**. Review the details; for a
  development item, confirm the address and fix the **Latitude/Longitude** (right-click
  the building in Google Maps to copy them).
- Flip the toggle **ON**, click **Publish**. Done — it's live after the rebuild.
- To reject a find, just delete it in the CMS (or leave it OFF).

## Cost
- GitHub Actions free tier covers weekly runs. No LLM → **no API cost. $0.**

## Notes
- The scouts never invent project facts; the development scout's notes link to the
  source for a human to verify, and coordinates are marked approximate/needed.
- The weekly **blog + newsletter writer** (which benefits from strong prose) stays on
  your free desktop Claude task — see WPBRC-Agents-Hosting-Options.docx.
