"""
Parse Chrome's Preferences file to list installed extensions.
Saves output to chrome/extensions/extensions.json.

Usage: python list_extensions.py
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

CHROME_PREFS = Path.home() / "Library/Application Support/Google/Chrome/Default/Preferences"
OUTPUT_FILE = Path(__file__).parent.parent / "chrome/extensions/extensions.json"

WEBSTORE_BASE = "https://chrome.google.com/webstore/detail/"

# Extensions that are built-in / not in the store
SKIP_IDS = {
    "nmmhkkegccagdldgiimedpiccmgmieda",  # Chrome Web Store Payments
    "pkedcjkdefgpdelpbcmbmeomcjbeemfm",  # Chrome Cast
}


def parse_extensions(prefs_path: Path) -> list[dict]:
    with open(prefs_path) as f:
        prefs = json.load(f)

    extensions_raw = prefs.get("extensions", {}).get("settings", {})
    results = []
    for ext_id, data in extensions_raw.items():
        if ext_id in SKIP_IDS:
            continue
        state = data.get("state", 0)
        if state != 1:
            continue  # not enabled
        manifest = data.get("manifest", {})
        name = manifest.get("name", data.get("name", ext_id))
        if name.startswith("__MSG_"):
            name = ext_id  # fallback for unresolved message keys
        results.append({
            "name": name,
            "id": ext_id,
            "store_url": f"{WEBSTORE_BASE}{ext_id}",
        })

    return sorted(results, key=lambda x: x["name"].lower())


def main():
    if not CHROME_PREFS.exists():
        print(f"Chrome Preferences not found at:\n  {CHROME_PREFS}")
        sys.exit(1)

    extensions = parse_extensions(CHROME_PREFS)
    output = {
        "last_updated": str(date.today()),
        "extensions": extensions,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Found {len(extensions)} extensions → {OUTPUT_FILE}")
    for ext in extensions:
        print(f"  • {ext['name']} ({ext['id']})")


if __name__ == "__main__":
    main()
