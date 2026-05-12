---
name: vk-video-search
description: Find watchable videos for movies, TV series, and other content across multiple streaming sources — VK Video (vkvideo.ru / vk.com/video) via the official API, Russian piracy aggregators (rezka / lordfilm / kinogo / hdrezka / filmix / kinokong / gidonline / etc.) via Brave Search, Kanopy library streaming via authenticated browser, plus JustWatch / Amazon clickable verification URLs. Use when the user asks to search VK, find a movie/TV episode online, look up a VK video by ID, list videos from a VK user/community, find streaming options for a Cannes/Berlinale/festival winner, search across saved adult-content communities, or paste a batch of VK URLs to resolve.
---

# VK Video Search (multi-source streaming finder)

Anchored on VK but covers movies/TV across the wider Russian streaming ecosystem + library streaming + clickable cross-service aggregators. Run the script at `~/Documents/GitHub/Personal/Random/vk_videos.py` (Python stdlib only, venv at `~/Documents/GitHub/Personal/Random/.venv/`). Token + saved-owners state live alongside it as `.env` and `vk_known_owners.json`.

## Quick start

```bash
source ~/Documents/GitHub/Personal/Random/.venv/bin/activate
alias vkv='python ~/Documents/GitHub/Personal/Random/vk_videos.py'
vkv --help
```

## Decision tree (pick the right path)

Classify the query first, then run the matching playbook below.

```
What is the user looking for?

├── A SPECIFIC FILM / TV EPISODE / KNOWN TITLE
│   → Run the "Movie / TV streaming" playbook (Sources 1-5).
│     Always include verified watchable URLs + clickable cross-service URLs.
│     Always show Quality column. Default --min-quality 720 -Q.
│
├── SFW MAINSTREAM CONTENT (music, lectures, news, gaming clips, asmr)
│   → vkv search "<query>" --sort popularity --min-quality 720 -Q
│     VK's own index is fast and comprehensive for SFW.
│
├── NSFW / ADULT / NICHE FETISH (no specific title)
│   → Drive Yandex through MCP browser with site:vk.com/video first
│     (extract URLs from snapshot, pipe through vkv resolve).
│     Then multi_search across saved owners for "more like this."
│
└── "MORE FROM SAVED COMMUNITIES" (e.g. "more Woodman", "more Mad Men HD")
    → vkv multi_search "<topic>" --total-cap 500
      ~25ms/video; warn user before scans of >5k videos.
```

## Source matrix — how each source works

| Source | Curl-friendly? | Login needed? | Best for | Coverage notes |
|---|---|---|---|---|
| **VK API** (script) | ✅ via token | ✅ one-time setup | NSFW concentrated content (Woodman, etc.), Russian-language SFW, niche communities | API has every video but blocks adult-flagged communities from `video.search`; bypass via `discover` / `multi_search` |
| **Lordfilm.fi** | ✅ direct curl | ❌ | Mainstream films within ~2 months of theatrical, Russian-dub | One specific stable Lordfilm domain; URL pattern `https://lordfilm.fi/<id>-<slug>.html` |
| **Brave Search** (broad Russian query) | ✅ direct curl | ❌ | **Highest yield for any movie/TV** — surfaces ~30 Russian piracy aggregators in one query | Use `<Russian title> 2025 фильм смотреть онлайн`. Each result needs URL verification (200 + correct h1) since aggregators rotate domains. |
| **Yandex** (via MCP browser) | ❌ captcha-walled to curl | ❌ | Long-tail / niche content / scattered NSFW that other sources miss | Browser-driven only (cursor-ide-browser MCP). Captcha after 1-2 page loads — user clicks once if needed. |
| **Kanopy** | ❌ JS-only SPA | ✅ library card via browser | Art-house, festival films **older than ~12 months**, documentaries, director back catalogs | Empirically verified: brand-new (<12mo) festival winners almost never on Kanopy. Drive logged-in browser session for actual catalog check. |
| **Amazon Prime Video** | ❌ hard-blocks curl | ✅ login via browser for Prime status | Mainstream films, Prime/Rent/Buy verification | Drive logged-in browser for Prime/Rent/Buy. Without login, only show clickable search URL (don't fake claims). |
| **JustWatch** | ⚠️ static page works, provider data via GraphQL | ❌ for clickable URL | Clickable cross-service "where to watch" verification URL | Don't try to parse provider data from curl — Apollo GraphQL hydrates client-side. Just hand the user the per-film URL: `https://www.justwatch.com/us/movie/<slug>`. |

## Russian piracy aggregator whitelist

When parsing Brave/Yandex results, filter for these known domain families. They rotate URLs constantly so a curl-verify is mandatory before reporting.

```
rezka (rezka-ua.tv, rezka-ua.org, hdrezka.inc, hdrezka.info, hdrezka.film, hdrezka.best, ...)
lordfilm (lordfilm.fi, lordfilm.top, lordfilms.bz, lordfilm.vc, lordfilmnew.cc, lordfilmqwp.ru, lord.rip, ...)
kinogo (kinogo.media, kinogo.fm, kinogo.inc, kinogo.at, kinogo.film, kinogo.li, kinogo-go.tv, kinogo-film.com, kinogo-tv.com, kinogo-hd.io, kinogo-films.biz, kinogo-filmov.net, kinogobiz.online, ...)
filmix (filmix.my, ...)
gidonline (gidonline.eu, gidonline.me, ...)
kinokong (kinokong.day, ...)
hdkinogo (f.hd-kinogo.co, ...)
hdkinoshka, baskino (baskino.fm), kinokrad (tv.kinokrad.pro), kinohamuv (kinohamuv.online),
hello-rezka (hello-rezka.tv), uakinogo (uakinogo.io)
zorgfilm, kino-online, etc.
```

Plus Russian metadata-only sites (NOT streaming, ignore for "watch" queries):
- `kinopoisk.ru` (Russian IMDB), `film.ru`, `kino.mail.ru`, `ru.kinorium.com`

Plus Russian LEGAL streamers (require Russian payment methods — usually inaccessible to non-RU users; skip unless user confirms):
- `okko.tv`, `premier.one`, `wink.ru`, `ivi.ru`, `kion.ru`, `start.ru`, `more.tv`, `amediateka`

### Yandex result extraction pattern

Yandex result snapshots show URLs in listitem text like:

    role: listitem
      name: <Title> — Видео от <Author> | ВКонтакте vk.com video-NNNNN_NNNNNN <description...>

Match `vk\.com video(-?\d+)_(\d+)` (note: VK URL slug uses underscore separator,
Yandex display uses space). Convert to `<owner>_<video>` format and pipe through
`vkv resolve` (or build the URL list manually as `https://vk.com/video<owner>_<video>`).

## Commands

| Command | Purpose |
|---|---|
| `search "<q>"` | VK's official `video.search` — best for SFW, hides adult-flagged communities |
| `discover "<q>"` | Brave Search `site:vk.com/video` → enrich via VK API. First-contact for NSFW. |
| `multi_search "<q>"` | Paginate every saved owner's library, filter titles client-side, aggregate. Use after owners are saved. Optional `--owners "<id1>,<id2>"` for subset. |
| `owner_search <owner_id> "<q>"` | Same as `multi_search` but one specific owner. |
| `user_videos <owner_id>` | List uploads from one user/community (no keyword filter). Owner ID is negative for communities, positive for users. |
| `groups_search "<q>"` | Find VK communities by name. Returns owner IDs. |
| `get <owner_id>_<video_id>` | Look up one specific video by ID. |
| `resolve [text]` | Bulk-extract VK video IDs from any pasted text/URLs/screenshots' text → enrich → auto-add owners. Reads stdin if no argument. |
| `owners_add "<ids>"` | Add comma-separated owner IDs to `vk_known_owners.json`. Auto-fetches video totals. |
| `owners_list` | Show all saved owners + total scannable corpus size. |

Each command also accepts `--count`, `--offset`, etc. — see `vkv <cmd> --help`.

## Two content patterns on VK

This is the key insight from observing many search categories:

**Concentrated** (works well with this skill):
- Examples: Woodman Casting (~447 hits across 11 saved communities), large-brand pornstar series, Russian-language TV-show clips
- Pattern: 5-10 dedicated reposter communities each holding hundreds-thousands of videos
- Path: `discover` → `groups_search` → `owners_add` → `multi_search`

**Scattered** (limited yield):
- Examples: voyeur fetish series (Galician Gotta Go, Girls Gotta Go, PissWC), regional amateur content, niche subscription brands
- Pattern: One-off uploads on hundreds of unrelated personal user accounts (3-4 videos each, 99% unrelated content)
- VK's `video.search` blocks them; Brave doesn't index them; only Yandex catches them
- Path: User does Yandex search in their browser → pastes result text → `resolve` → maybe `multi_search` after, but yields are small (single-digit hits typical)
- **Be honest with the user** if this pattern emerges — VK isn't a good source for this category

Detect which pattern by looking at `discover` and `groups_search` results. Zero hits + very long-tail Yandex result count = scattered.

## Persistent state

- `~/Documents/GitHub/Personal/Random/.env` — `VK_ACCESS_TOKEN`
- `~/Documents/GitHub/Personal/Random/vk_known_owners.json` — accumulated owner library, includes name + total video count per owner. Survives across sessions and gets auto-extended by `discover`, `resolve`, `owners_add`.

Tell the user about this if they ask "what do you know about VK" or "what have we saved" — show them `owners_list` output.

## Setup (one-time)

If `VK_ACCESS_TOKEN` is missing, the script exits with a setup-instructions message. The working path uses **Kate Mobile's official client app_id** (`2685278`) — VK has disabled the legacy implicit flow for self-registered Standalone apps, so a self-registered app_id will return `Security Error`. Kate Mobile is a real iOS/Android VK client whose app_id is widely re-used by hobbyist scripts.

Steps for the user:

1. Sign in at https://vk.com (phone-verified account required).
2. In the same browser, paste:
   ```
   https://oauth.vk.com/authorize?client_id=2685278&scope=offline,video,wall,friends&redirect_uri=https://oauth.vk.com/blank.html&display=mobile&response_type=token&revoke=1&v=5.199
   ```
3. Click "Continue as <name>" / "Allow". Browser will redirect to `oauth.vk.com/blank.html#access_token=vk1.a.XXXXX&expires_in=0&user_id=...`.
4. Copy the value between `access_token=` and `&`. With `offline` scope, `expires_in=0` means it never expires.
5. Append to `.env`:
   ```bash
   echo "VK_ACCESS_TOKEN=vk1.a.XXXXX" >> ~/Documents/GitHub/Personal/Random/.env
   ```

## Output format

Every command that returns videos prints a markdown table with columns:

`| Date | Quality | Duration | Views | Title | Page | Player |`

- **Quality** = max available height (`360p`, `720p`, `1080p`, `4K`...) parsed from VK's `files` dict. `?` if unknown.
- **Page** = `https://vkvideo.ru/video<owner>_<id>` — clickable, plays in browser
- **Player** = embeddable iframe URL VK returns. Direct mp4s aren't in the API response — to download, scrape the player page.

**Pipe the script's output verbatim to the user. Don't reformat or summarize the table itself.** Add brief commentary above/below if useful (e.g. "owner X had 25 hits, owner Y had none").

## Quality filtering and sorting

All commands that return videos accept:

- `--min-quality HEIGHT` — drop anything below the given pixel height. E.g. `--min-quality 720` for HD only, `--min-quality 1080` for full-HD only.
- `-Q` / `--sort-by-quality` — sort results highest-quality first.

For long-form / TV content always pass `--min-quality 720 -Q` by default. The most popular result on VK is frequently 360p (someone uploaded 5+ years ago); a much smaller-view-count uploader from the past month often has the same content in HD.

## Movie / TV streaming playbook

For any film/TV request, execute these sources **in parallel** (don't wait sequentially):

1. Brave with broad Russian query → 5-15 streaming aggregator URLs (verify each)
2. Lordfilm.fi own search → confirms Lordfilm-specific availability
3. VK: КИНОБРО first, then wider VK index → Russian-dub uploads + niche reposts
4. Kanopy (only if film is >12 months old or user explicitly asks legal source)
5. JustWatch + Amazon clickable URLs (always include in "to verify" footer)

Then verify every URL via curl 200 check before including in the response.

### Source 1: Brave Search with broad Russian query (THE highest-yield path)

**This is the highest-yield path for any movie request.** Brave is curl-friendly and indexes the entire Russian piracy aggregator ecosystem (rezka, lordfilm, kinogo, hdrezka, filmix, kinokong, gidonline, lord.rip, hdkinoshka, baskino, kinokrad, and many more).

Query pattern:

```bash
curl -sL --compressed -A "Mozilla/5.0" \
  "https://search.brave.com/search?q=$(python3 -c 'import urllib.parse,sys; print(urllib.parse.quote_plus(sys.argv[1]))' '<RUSSIAN_TITLE> 2025 фильм смотреть онлайн')" \
  | grep -oE 'href="https?://[^"]+"' \
  | sed 's/href="//;s/"$//' \
  | grep -iE '(rezka|lordfilm|kinogo|hdkinogo|filmix|kinokong|gidonline|lord\.rip|hdkinoshka|baskino|kinokrad|kinohamuv)' \
  | sort -u | head -10
```

Use the **Russian translation title** (most common one). Add the year (`2025`) and the magic phrase `фильм смотреть онлайн` ("film watch online"). This unlocks 10-30 mirror URLs per popular film.

**Always verify the URLs before reporting** — many aggregators rotate domains, so `kinogo.foo` might 404 while `kinogo.bar` 200s. Pattern:

```bash
code=$(curl -sL --compressed --max-time 10 -A "Mozilla/5.0" -o /tmp/v.html -w "%{http_code}" "$url")
title=$(grep -oE '<h1[^>]*>[^<]+' /tmp/v.html | head -1)
[ "$code" = "200" ] && echo "OK: $title"
```

### Source 1b: Lordfilm.fi (specific Lordfilm domain that's currently stable)

When Brave doesn't surface enough hits, hit Lordfilm.fi's own search:

```bash
curl -s -A "Mozilla/5.0" -G \
  --data-urlencode "do=search" --data-urlencode "subaction=search" \
  --data-urlencode "story=QUERY" "https://lordfilm.fi/index.php" \
  | grep -oE 'href="https?://lordfilm\.fi/[0-9]+-[^"]+\.html"' | sort -u
```

URL pattern: `https://lordfilm.fi/<id>-<slug>.html`. No login, no captcha.

### Source 2: VK Video (КИНОБРО priority + general search)

1. **`owner_search -220018529 "<title>" --min-quality 720 -Q --max-pages 5`** — КИНОБРО (2.2M subs, ~3,649 videos), biggest mainstream movie reposter on VK. Scans only the most-recent 500 uploads for speed. Drop `--max-pages` for full scan only on explicit request.
2. **`vkv search "<title>" --sort popularity --min-quality 720 -Q`** — wider VK index.
3. **If a strong HD hit surfaces from a NEW owner, immediately probe that owner** with `owner_search <owner_id> "<title or related>" --min-quality 720` to find more seasons / related films.
4. Add productive new owners with `owners_add` and tag them in `vk_known_owners.json` as `"priority": "movies"`.

### Source 3: Kanopy.com (legal, library-card streaming)

Kanopy is a library-funded streaming service for art-house / festival / Criterion / indie films and documentaries. URL pattern when logged in includes the library slug:

```
https://www.kanopy.com/en/<library-slug>/search?query=<URL-encoded title>
```

Example logged-in URL: `https://www.kanopy.com/en/cityofsanmateo/search?query=Sentimental+Value`

**Empirical rule (verified Apr 2026): Kanopy is a BACK-CATALOG source, not a CURRENT-YEAR source.** Library acquisition deals run ~12 months behind theatrical release. So:
- ❌ Films < 12 months from theatrical: almost never on Kanopy. Don't waste cycles searching.
- ✅ Films > 12 months from theatrical (especially festival/art-house): high hit rate.
- ✅ Director's BACK CATALOG: when a recent film isn't on Kanopy, search the director's name — their older films usually are. Always recommend "if you can't find X, try director Y's earlier film Z on Kanopy."

How to drive Kanopy programmatically (when user is logged in via MCP browser):
1. Navigate to `https://www.kanopy.com/en/<library-slug>/search?query=<title>` (URL param alone won't trigger search)
2. `browser_fill` the search textbox with the title
3. `browser_press_key` Enter
4. `browser_wait_for` 3 sec
5. `browser_take_screenshot` to read results
6. Look for "**No results found for '<query>'**" message = empty hit. Otherwise, results are real.

**Without an active logged-in browser session, do NOT try to scrape Kanopy** — JS-only SPA, no useful indexing. Just hand the user a search URL template they can click.

When to use Kanopy:
- ✅ Art-house, Criterion, Sundance, Cannes, Berlinale, Locarno films older than ~12 months
- ✅ Documentaries (Kanopy is THE library docu source)
- ✅ World cinema, foreign-language back catalogs
- ✅ "If you liked X (recent), watch Y by same director" recommendations
- ❌ Films within ~12 months of theatrical release
- ❌ Mainstream blockbusters (those go to Netflix/Max)

### Source 4: JustWatch + Amazon (legal, paid/Prime)

For ANY movie/TV request, also include these clickable URLs in the response:

```
JustWatch (aggregates ALL streaming services in one page):
https://www.justwatch.com/us/movie/<lowercase-hyphenated-title>
or fallback: https://www.justwatch.com/us/search?q=<URL-encoded title>

Amazon Prime Video (rent/buy/Prime check, user verifies logged in):
https://www.amazon.com/s?k=<URL-encoded title>&i=instant-video
```

JustWatch direct slug pattern works for ~90% of films — just lowercase the English title and replace spaces with hyphens (`Sentimental Value` → `sentimental-value`). For 2025+ films that share a title with an older film, append `-2025` (`the-secret-agent-2025`). 404s mean wrong slug — fall back to the search URL.

**Do NOT try to scrape JustWatch's per-film provider data via curl** — they use Apollo GraphQL with client-side hydration; static HTML has no offer data. Drive the browser only if you really need parsed availability; otherwise just give the user the URL and let them click.

**Do NOT try to scrape Amazon directly** — they hard-block curl with anti-bot. Let the user click the search URL and see Prime status in their logged-in session.

### Source 5 (fallback): Yandex via MCP browser

When Brave's broad query returns 0 hits (very niche / festival-only / non-Russian-released), drive Yandex through the MCP browser. Yandex indexes Russian streaming sites more comprehensively than Brave. Two query shapes that work:

```
yandex.ru/search/?text=<RUSSIAN_TITLE>+2025+фильм+смотреть+онлайн     # broadest, surfaces all aggregators
yandex.ru/search/?text=<TITLE>+site%3Avk.com%2Fvideo                  # narrow, for VK-specific NSFW
```

Workflow: navigate → snapshot → extract URLs from `listitem` text → unlock → curl-verify → report. Captcha hits after 1-2 page loads — user clicks once if needed; usually page 1 is enough.

## Festival-timing rule

Empirically confirmed (Cannes 2025 in Apr 2026, Berlinale 2026 in Apr 2026):

| Time since theatrical premiere | Piracy availability | Recommendation |
|---|---|---|
| **< 1 month** | None — film is still festival-only | Tell user honestly: not available; offer JustWatch URL as future-watch reference |
| **1-3 months** (in some commercial release) | Sparse — only big-distributor titles (NEON, A24) leaking on Russian aggregators | Try Brave broad query; expect 1-2 hits if any |
| **3-6 months** | Most theatrical-released films available on Russian aggregators in HD | Brave query is the move |
| **6-12 months** | Wide piracy + occasional Kanopy on big-library systems | Add Kanopy check |
| **> 12 months** | Everything available + Kanopy + JustWatch shows providers | Full multi-source sweep |

**Practical implication**: if a user asks about a film that just premiered at a festival within the last few weeks, don't bother running the full sweep — tell them straight that the wide-piracy clock starts at theatrical release, not festival premiere. Cannes-May winners typically appear on Russian aggregators in Sept-Nov of the same year (after NEON/A24/etc. theatrical rollout). Berlinale-Feb winners appear ~July onward (after their European theatrical rollout).

### Reporting to the user

**Always present results from all working sources side-by-side**, not VK-only. Lordfilm tends to win for art-house / festival films where VK gets DMCA'd. VK wins for older content / niche communities / NSFW. Note when Lordfilm has a film that VK doesn't (or vice versa).

The `vk_known_owners.json` `priority: "movies"` tag identifies the set of owners worth scanning for ALL future movie/TV requests. Currently includes КИНОБРО + a handful of TV-series specialists.

## Rules

- Never re-discover what VK / vkvideo.ru is — go straight to the script.
- Never scrape `vkvideo.ru/search` directly — bot-walled and SFW-filtered.
- Never invest in setting up Yandex Cloud Search API — it requires a Russian-issued payment method (we tried; signup walls non-Russian cards). Use Yandex via the user's own browser instead.
- **For ANY NSFW query, default first step is to drive Yandex through the cursor-ide-browser MCP**, extract URLs from the snapshot, pipe through `resolve`. Do not run `discover` or `multi_search` first. Yandex indexes 100x more VK NSFW than Brave. If captcha hits, ask user to click "I'm not a robot" and continue. `discover` is a fallback when browser MCP is unavailable; `multi_search` is for "give me more from owners I already have" follow-ups.
- **Always show the Quality column. For long-form content (TV series, movies, full episodes) default to `--min-quality 720 -Q` and warn if only 360p is available.**
- **HARD RULE — completeness over breadth: when a TV series / movie / multi-part query yields ONE strong-quality hit (HD season pack, HD episode, complete-series pack), IMMEDIATELY probe the same owner with `owner_search <owner_id>` to see if they have the rest of the series/related seasons.** Do not present that single hit alongside inferior hits as "options" and ask the user to choose — finish the discovery first, then present the consolidated set in one message. Most TV uploaders work serially and have multiple related uploads from the same source.
- **HARD RULE — multi-part movies: a single VK video that is much shorter than the expected runtime is almost always part of a multi-part upload.** Triggers to check: (a) title contains "часть"/"part" with a number, (b) duration is < 80% of the film's known runtime, (c) title contains "ч.1", "p.1", "1/2", "1 of 2". Action: resolve the same owner's adjacent video IDs (`±1, ±2, ±3` from the found video_id) — multi-part uploads are almost always sequential IDs because they're uploaded back-to-back. Don't tell the user "partial — full version not available" until you've checked the next 2-3 IDs.
- **HARD RULE — verified vs unverified separation: never bundle unverified "click to check" URLs alongside verified watch URLs in the same column or row.** Use a clear "Verified watchable" column for sources you actually checked (VK API resolved, Lordfilm slug 200'd, Kanopy logged-in search returned the title, etc.). Put unverified URLs (Amazon search links, JustWatch search links, etc.) in a separate "To verify yourself" section, clearly labeled. The user shouldn't have to figure out which links are real and which are templates.
- Pre-existing owners list survives between calls. After `discover` or `resolve`, mention any new owners that were added.
- For `multi_search`, expect ~25ms per scanned video (1k videos ≈ 25 sec, 25k ≈ 10 min). Reserve it for "show me MORE of topic X from owners I already have." Set `--max-pages` and `--total-cap` aggressively. Warn the user about runtime before starting a full-corpus scan — they will background it if you don't.
- Never curate-out a known owner from `multi_search` because you assumed it's irrelevant. Hit-density is hard to predict from owner names; run against the FULL known list or have a systematic reason to subset.

## Common gotchas

- **VK `video.get` returns ~90-100 items per call regardless of `count` param.** The script handles this (paginates by `len(items)`), but code that uses the API directly must NOT advance offset by a fixed page size.
- **Closed/private communities return error 204** ("Access denied"). Some dedicated-topic communities (e.g. `-81792998` "Все кастинги Вудмана") need the user to send a join request on VK before the API can list their videos.
- **Adult-flagged content** requires the API token's user account to have completed VK's age-verification interstitial at least once (visit any 18+ video while logged in, click "I'm 18+"). The Kate Mobile token bypasses most filtering automatically.
- **`adult=1` parameter doesn't help** — VK applies platform-level community-flag filtering on top of it. Workaround is `discover` / `multi_search`, not API params.
