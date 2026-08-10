#!/usr/bin/env python3
"""
build.py — regenerate the whole site. Run by Netlify on every deploy (and locally).

It runs the page generators against this repo folder, so editing the JSON data
files in assets/ (via the /admin CMS) and committing is enough to update the live
site — Netlify runs this and republishes.

Local:   python3 build.py
Netlify: set build command to  python3 build.py  and publish directory to  .
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ["SITE_OUT"] = ROOT
TOOLS = os.path.join(ROOT, "tools")

def run(script):
    print("→", script)
    subprocess.run([sys.executable, os.path.join(TOOLS, script)], check=True, cwd=TOOLS)

if __name__ == "__main__":
    run("build_site.py")   # core pages (home, about, development, board, neighborhoods, etc.)
    run("build_pages.py")  # data-driven pages (issues, resources, media) from JSON
    print("Build complete.")
