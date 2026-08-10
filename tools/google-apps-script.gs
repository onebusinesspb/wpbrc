/**
 * WPBRC Development Tracker — auto-publish Google Sheet → projects.json
 * ---------------------------------------------------------------------
 * OPTIONAL / ADVANCED. This makes the map update automatically whenever the
 * Board edits the Google Sheet — no manual export, no developer needed.
 *
 * It commits an updated assets/projects.json to your site's GitHub repo;
 * Netlify / Cloudflare Pages then auto-deploys within ~1 minute.
 *
 * SETUP (one time)
 *   1. Open your tracker Google Sheet → Extensions → Apps Script.
 *   2. Paste this file. In Project Settings → Script properties, add:
 *        GITHUB_TOKEN  = a fine-grained GitHub token with "Contents: write" on the repo
 *        GITHUB_REPO   = e.g. wpbrc/website
 *        GITHUB_BRANCH = main
 *        FILE_PATH     = assets/projects.json
 *   3. Run publishProjects() once to authorize.
 *   4. Triggers → Add Trigger → publishProjects → On edit  (and/or a daily timer).
 *
 * SHEET COLUMNS (row 1 headers, exactly):
 *   id | name | location | neighborhoods | district | status | notes | lat | lng
 */

function publishProjects() {
  const props = PropertiesService.getScriptProperties();
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  const rows  = sheet.getDataRange().getValues();
  const head  = rows.shift().map(h => String(h).trim().toLowerCase());

  const COORDS = {
    "downtown":[26.7128,-80.0536],"grandview heights":[26.7045,-80.0585],
    "flamingo park":[26.6995,-80.0612],"el cid":[26.6955,-80.0558],
    "sunshine park":[26.6905,-80.0602],"soso":[26.6802,-80.0571],
    "northwood":[26.7402,-80.0581],"old northwood":[26.7430,-80.0598],
    "northwood shores":[26.7370,-80.0490],"north end":[26.7560,-80.0480],
    "waterfront":[26.6900,-80.0508],"south end":[26.6722,-80.0522],"citywide":[26.7150,-80.0550]
  };
  const col = name => head.indexOf(name);

  const projects = rows.filter(r => String(r[col("name")]).trim()).map(r => {
    const get = n => String(r[col(n)] || "").trim();
    const neighbs = get("neighborhoods").split(/[;,]/).map(s => s.trim()).filter(Boolean);
    let lat = parseFloat(get("lat")), lng = parseFloat(get("lng"));
    if (isNaN(lat) || isNaN(lng)) {
      const c = neighbs.map(n => COORDS[n.toLowerCase()]).find(Boolean) || [26.7150,-80.0550];
      lat = c[0]; lng = c[1];
    }
    return {
      id: get("id") || get("name").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,""),
      name: get("name"), location: get("location"),
      neighborhoods: neighbs.length ? neighbs : ["Citywide"],
      district: get("district"), status: get("status") || "Proposed",
      notes: get("notes"), lat: +lat.toFixed(5), lng: +lng.toFixed(5)
    };
  });

  const payload = {
    _meta: { title: "WPB Development Projects Master List",
             version: "auto-synced from Google Sheet " + new Date().toISOString().slice(0,10),
             disclaimer: "Working draft maintained by WPBRC. Verify district, board status, and hearing dates against current City of West Palm Beach agendas before relying on them. Map coordinates are approximate.",
             statusOrder: ["Proposed","In Review","Planning","Approved","Under Construction","Completed"] },
    projects: projects
  };
  commitToGitHub(props, JSON.stringify(payload, null, 2));
}

function commitToGitHub(props, content) {
  const token  = props.getProperty("GITHUB_TOKEN");
  const repo   = props.getProperty("GITHUB_REPO");
  const branch = props.getProperty("GITHUB_BRANCH") || "main";
  const path   = props.getProperty("FILE_PATH") || "assets/projects.json";
  const api    = "https://api.github.com/repos/" + repo + "/contents/" + path;
  const hdr    = { Authorization: "Bearer " + token, Accept: "application/vnd.github+json" };

  // get current file sha (needed to update)
  let sha = null;
  const getRes = UrlFetchApp.fetch(api + "?ref=" + branch, { headers: hdr, muteHttpExceptions: true });
  if (getRes.getResponseCode() === 200) sha = JSON.parse(getRes.getContentText()).sha;

  const body = {
    message: "Update development tracker from Google Sheet",
    content: Utilities.base64Encode(content, Utilities.Charset.UTF_8),
    branch: branch
  };
  if (sha) body.sha = sha;

  const res = UrlFetchApp.fetch(api, {
    method: "put", headers: hdr, contentType: "application/json",
    payload: JSON.stringify(body), muteHttpExceptions: true
  });
  if (res.getResponseCode() >= 300) throw new Error("GitHub commit failed: " + res.getContentText());
  Logger.log("Published " + JSON.parse(content).projects.length + " projects.");
}
