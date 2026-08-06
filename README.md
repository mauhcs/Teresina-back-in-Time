# Foro de Teresina — Week-of-Year Order

Personal, unofficial re-ordering of the *Foro de Teresina* podcast feed.
Episodes are grouped by ISO calendar week (regardless of year) and sorted
oldest-year-first within each week, so listening through the feed in order
means: this week's episodes across every past year, then next week's, and
so on — cycling through the whole archive once a year.

Only one week's batch is unlocked at a time: a new batch is added to the
feed every 7 days (tracked in `state.json`, starting from the date the
feed was first generated), so the feed grows on its own instead of
dumping all 535 episodes at once.

No audio is re-hosted. `feed.xml` only points at the original MP3 URLs
already hosted by the publisher (Megaphone/Spreaker); this repo just
contains a re-ordered index (an RSS/XML file) plus the script that built it.

## Files

- `episodes.json` — metadata (title, original pubDate, ISO week, duration,
  enclosure URL) for all 535 episodes, pulled from the official feed
  (`https://feeds.megaphone.fm/NPP2619427256`).
- `state.json` — the fixed start date/week the unlock schedule began on.
  Created automatically on first run; don't edit unless you want to reset
  or shift the schedule.
- `generate_feed.py` — builds `feed.xml` from `episodes.json` + `state.json`,
  including only the weeks unlocked so far.
- `feed.xml` — the generated podcast feed. Subscribe to this in your
  podcast app.
- `.github/workflows/update-feed.yml` — runs daily on GitHub's own
  schedule, re-generates the feed, and pushes it if a new week unlocked.
  No secrets/tokens needed — it uses the repo's built-in `GITHUB_TOKEN`.
  Just needs Actions enabled (default) and Settings → Actions → General →
  Workflow permissions set to "Read and write permissions".

## Regenerating manually

The publisher adds new episodes over time. To pick those up:

```
curl -s "https://feeds.megaphone.fm/NPP2619427256" -o feed_source.xml
# re-extract episodes.json from feed_source.xml (see project history),
# then:
python3 generate_feed.py
```

The Actions workflow above handles the weekly unlock automatically once
pushed — you shouldn't need to run this by hand unless new episodes need
picking up from the source feed.

## Hosting on GitHub Pages

```
git remote add origin git@github.com:<you>/foro-week-order.git
git branch -M main
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: Deploy from branch → main →
/ (root) → Save**. After a minute your feed is live at:

```
https://<you>.github.io/foro-week-order/feed.xml
```

## Subscribing on iOS

- **Apple Podcasts**: Library tab → "..." (top right) → *Follow a Show by
  URL* → paste the Pages URL above.
- **Overcast / Pocket Casts**: use their "Add by URL" option (usually
  found in the search/add screen).

Then, in that show's settings, set episode order to **Oldest to Newest**
(or "play oldest first") — the feed's synthetic publish dates encode the
week-of-year order ascending, so oldest-first playback follows that order.
