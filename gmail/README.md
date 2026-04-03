# Gmail

Scripts and configs for managing your Gmail account programmatically.

## Folders

| Folder      | Purpose                                              |
|-------------|------------------------------------------------------|
| `filters/`  | Gmail filter rules (exported XML + source JSON)      |
| `scripts/`  | Python scripts for inbox automation                  |
| `templates/`| Reusable email templates                             |

## Scripts

| Script                    | What it does                                   |
|---------------------------|------------------------------------------------|
| `scripts/triage.py`       | Summarize unread inbox (sender, subject, date) |
| `scripts/label_archive.py`| Apply labels and archive matching emails       |
| `scripts/export_labels.py`| Export all labels to JSON for backup          |

## Setup

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
# Place your credentials.json (from Google Cloud Console) in config/
python scripts/triage.py
```

## Auth

Uses OAuth 2.0. On first run, a browser window opens to authorize access.
Token is saved to `config/token.json` (gitignored).
