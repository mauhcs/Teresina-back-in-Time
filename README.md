# Foro de Teresina — Week-of-Year Order

Personal, unofficial re-ordering of the *Foro de Teresina* podcast feed.
`feed.xml` always contains just the **current ISO calendar week's**
episodes — every historical episode originally published in that same
week across all years (2018–2026), oldest year first — and is swapped
out for the next week's batch automatically.

No audio is re-hosted. Every item's enclosure points at the original MP3
URL already hosted by the publisher (Megaphone/Spreaker); this repo only
holds re-ordered index files (RSS/XML) plus the scripts that build them.

## Files

- `episodes.json` — metadata (title, original pubDate, ISO week, duration,
  enclosure URL) for all 535 episodes, pulled from the official feed
  (`https://feeds.megaphone.fm/NPP2619427256`).
- `build_weeks.py` — builds one self-contained feed file per ISO week
  (`weeks/week-01.xml` … `weeks/week-52.xml`) from `episodes.json`. Only
  needs to be re-run when new episodes are added to the source feed.
- `weeks/week-NN.xml` — 52 pre-built feed files, one per calendar week.
- `sync_week.py` — copies whichever `weeks/week-NN.xml` matches the
  *current real-world* ISO week over `feed.xml`. This is what actually
  rotates the live feed.
- `feed.xml` — the live feed. **Subscribe to this one** in your podcast
  app. Always holds only the current week's episodes.
- `.github/workflows/update-feed.yml` — runs `sync_week.py` daily on
  GitHub's own schedule and pushes `feed.xml` if the week changed. No
  secrets/tokens needed — it uses the repo's built-in `GITHUB_TOKEN`.
  Requires Settings → Actions → General → Workflow permissions →
  "Read and write permissions".

## Regenerating

If the source podcast publishes new episodes and you want them picked up:

```
curl -s "https://feeds.megaphone.fm/NPP2619427256" -o feed_source.xml
# re-extract episodes.json from feed_source.xml (see project history),
python3 build_weeks.py   # rebuilds all 52 weekly files
python3 sync_week.py     # refreshes feed.xml for the current week
```

Day-to-day rotation is handled automatically by the Actions workflow —
you only need `build_weeks.py` when the underlying episode list changes.
