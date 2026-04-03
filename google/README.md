# Google Services

Automation and backup scripts for Google Calendar, Drive, Sheets, and Contacts.

## Subfolders

| Folder      | Purpose                                         |
|-------------|-------------------------------------------------|
| `calendar/` | Event scripts, recurring block setup, exports   |
| `drive/`    | File organization, backup, folder management    |
| `sheets/`   | Personal spreadsheet scripts (budgets, logs)    |
| `contacts/` | Contacts export and sync utilities              |

## Auth

All scripts share the same OAuth credentials from `config/credentials.json`.
Scopes are requested per-script — authorize only what each script needs.

## Quick Reference

```bash
# Export contacts to CSV
python contacts/export_contacts.py

# List Drive files larger than 100MB
python drive/find_large_files.py --min-mb 100

# Create focus time blocks on Calendar this week
python calendar/block_focus_time.py --days mon,wed,fri --hours 9-11
```
