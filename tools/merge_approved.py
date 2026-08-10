#!/usr/bin/env python3
"""
WPBRC — merge an APPROVED candidate/draft file into the live site data.

The weekly agents write drafts into this tools/ folder. After you approve some
or all items, run this to fold them into the live JSON the site reads.

USAGE
  python3 merge_approved.py <candidate-file.json>

It auto-detects the type by the file's contents:
  • development projects  -> ../assets/projects.json   (map updates live)
  • calendar events       -> ../assets/events.json      (Calendar updates live)
  • blog post(s)          -> ../assets/blog.json        (then run build_blog.py)

Items are matched by "id": an existing id is updated, a new id is appended.
A timestamped backup of the target file is written next to it before changes.
"""
import json, sys, os, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")

TARGETS = {
    "projects": (os.path.join(ASSETS, "projects.json"), "projects"),
    "events":   (os.path.join(ASSETS, "events.json"),   "events"),
    "blog":     (os.path.join(ASSETS, "blog.json"),     "posts"),
}

def detect(items):
    """Guess the data type from the first item's keys."""
    it = items[0]
    if "lat" in it and "lng" in it: return "projects"
    if "body" in it or "slug" in it: return "blog"
    if "displayDate" in it or "tag" in it: return "events"
    raise SystemExit("Could not detect type (expected project, event, or blog fields).")

def main(path):
    raw = json.load(open(path, encoding="utf-8"))
    # accept either a bare list or {"...":[...]} ; a single object becomes a 1-item list
    if isinstance(raw, dict) and not any(isinstance(v, list) for v in raw.values()):
        items = [raw]
    elif isinstance(raw, dict):
        items = next(v for v in raw.values() if isinstance(v, list))
    else:
        items = raw
    if not items:
        raise SystemExit("No items found in " + path)

    kind = detect(items)
    target, key = TARGETS[kind]
    data = json.load(open(target, encoding="utf-8"))
    existing = data.get(key, [])
    by_id = {x.get("id"): i for i, x in enumerate(existing)}

    added, updated = 0, 0
    for it in items:
        iid = it.get("id")
        if iid in by_id:
            existing[by_id[iid]] = it; updated += 1
        else:
            existing.append(it); by_id[iid] = len(existing) - 1; added += 1

    # backup then write
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(target, target + "." + stamp + ".bak")
    data[key] = existing
    json.dump(data, open(target, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    print(f"[{kind}] merged into {os.path.relpath(target)} — {added} added, {updated} updated, {len(existing)} total.")
    print(f"Backup: {os.path.basename(target)}.{stamp}.bak")
    if kind == "blog":
        print("Next: run  python3 build_blog.py  to (re)generate blog.html + post pages.")
    else:
        print("The map/Calendar read this file live — just redeploy (or it updates on next load).")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1])
