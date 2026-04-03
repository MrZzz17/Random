# Browser

Chrome configuration backup and management.

## Structure

```
browser/
├── chrome/
│   ├── bookmarks/      # Exported bookmark files and scripts
│   ├── extensions/     # Extension list and configs
│   └── profiles/       # Profile-specific settings (gitignored by default)
└── scripts/            # Automation scripts
```

## Bookmarks

Chrome bookmarks can be exported manually:
1. Chrome → Bookmarks → Bookmark Manager → ⋮ → Export bookmarks
2. Save the HTML file to `chrome/bookmarks/bookmarks_YYYY-MM-DD.html`

Or use the script to parse and organize them:
```bash
python scripts/export_bookmarks.py
```

## Extensions

Track your installed extensions so you can restore them on a new machine.

```bash
# Generate extensions list from Chrome's preferences
python scripts/list_extensions.py
```

Output: `chrome/extensions/extensions.json` — a list of all installed extension IDs and names.

To reinstall on a new machine, open each Chrome Web Store URL from the list.

## Profiles

Chrome profiles live at:
```
~/Library/Application Support/Google/Chrome/Default/   # macOS
%LOCALAPPDATA%\Google\Chrome\User Data\Default\        # Windows
~/.config/google-chrome/Default/                       # Linux
```

Profile data is gitignored (too large, contains sensitive data).
Only configs and preference snapshots are tracked here.
