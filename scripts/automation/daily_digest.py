"""
Daily digest: run each morning to get a summary of unread emails,
today's calendar events, and overdue tasks.

Usage: python daily_digest.py
Schedule via cron: 0 8 * * * cd /path/to/repo && python scripts/automation/daily_digest.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent


def run(script: Path, label: str):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print("=" * 50)
    result = subprocess.run([sys.executable, str(script)], capture_output=False)
    if result.returncode != 0:
        print(f"[!] {label} failed with exit code {result.returncode}")


def main():
    print("Daily Digest — " + __import__("datetime").date.today().isoformat())
    run(ROOT / "gmail/scripts/triage.py", "Gmail — Unread Inbox")
    run(ROOT / "finance/crypto/portfolio.py", "Crypto Portfolio")


if __name__ == "__main__":
    main()
