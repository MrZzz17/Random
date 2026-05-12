---
name: twitter-watch
version: 1.0.0
description: "On-demand X/Twitter watchlist via local twscrape fetch.py — summarize new or recent posts in chat."
metadata:
  openclaw:
    category: "research"
---

# Twitter / X watch (on-demand)

**Prerequisite:** One-time setup in `~/twitter-watch/README.md` — install `twscrape`, add a burner account to `accounts.db`, edit `accounts.yaml`.

When the user asks for Twitter/X updates, watchlist news, “what’s new on twitter”, “any posts from my watchlist”, or “latest from @handle”, run the local fetcher and **summarize** the JSON (group by `category` when present).

## Commands

**New since last check** (updates dedupe `state.db`):

```bash
python3 ~/twitter-watch/fetch.py --since-last --json
```

**One account:**

```bash
python3 ~/twitter-watch/fetch.py --since-last --handle HANDLE --json
```

**Last N tweets** (ignores dedupe state; good for a one-off peek):

```bash
python3 ~/twitter-watch/fetch.py --handle HANDLE --last N --json
```

Optional paths if the user moved files:

```bash
python3 ~/twitter-watch/fetch.py --config PATH --accounts-db PATH --state-db PATH --since-last --json
```

## Agent behavior

1. Run the appropriate command (prefer `--json` for parsing).
2. If stderr mentions missing `accounts.db` or login errors, tell the user to follow `~/twitter-watch/README.md` (do not invent tweet text).
3. Summarize: author, short text snippet, link (`url`), and time (`created_at`). If the array is empty, say there’s nothing new since the last run.

## Notes

- Uses **twscrape** (unofficial); not the X API. Respect rate limits; use a dedicated burner account.
- Fallback without twscrape: RSSHub — see `~/twitter-watch/README.md`.

## See also

- [twscrape upstream](https://github.com/vladkens/twscrape)
