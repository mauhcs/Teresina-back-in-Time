#!/usr/bin/env python3
"""
Builds a synthetic RSS feed for "Foro de Teresina" that reorders the
original episodes into week-of-year order: for each ISO calendar week,
all historical episodes published in that week (across every year),
oldest year first. Enclosures point at the original hosted MP3 files;
nothing is re-hosted or copied.

Only reveals one week-of-year batch at a time: a new batch unlocks every
7 days, starting from the first run's date (persisted in state.json), so
the feed grows on its own rather than dumping all 535 episodes at once.
Intended to be re-run on a schedule (see .github/workflows/update-feed.yml).
"""
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

EPISODES_JSON = "episodes.json"
OUTPUT_XML = "feed.xml"
STATE_JSON = "state.json"

CHANNEL_TITLE = "Foro de Teresina — Week-of-Year Order"
CHANNEL_LINK = "https://www.spreaker.com/show/foro-de-teresina"
CHANNEL_LANGUAGE = "pt"
CHANNEL_IMAGE = (
    "https://megaphone.imgix.net/podcasts/03b80a24-71dc-11ee-9304-278056d646af/"
    "image/a549074bc5d7f5ccfde8fec8e212be43.png?ixlib=rails-4.3.1&max-w=3000&max-h=3000&fit=crop&auto=format,compress"
)
CHANNEL_AUTHOR = "piauí"
CHANNEL_DESCRIPTION = (
    "Unofficial personal re-ordering of the Foro de Teresina podcast archive: "
    "episodes grouped by calendar week-of-year, oldest year first within each "
    "week, so you can listen to \"this week in past years\" episodes together. "
    "One week's worth unlocks every 7 days. Audio is streamed from the "
    "original publisher's hosting; nothing is re-hosted here."
)


def load_episodes():
    with open(EPISODES_JSON) as f:
        return json.load(f)


def load_or_init_state(start_week_default):
    try:
        with open(STATE_JSON) as f:
            return json.load(f)
    except FileNotFoundError:
        state = {
            "start_date": datetime.now(timezone.utc).date().isoformat(),
            "start_week": start_week_default,
        }
        with open(STATE_JSON, "w") as f:
            json.dump(state, f, indent=2)
        return state


def full_week_sequence(episodes, start_week):
    weeks_present = sorted(set(e["iso_week"] for e in episodes))
    idx = weeks_present.index(start_week) if start_week in weeks_present else 0
    return weeks_present[idx:] + weeks_present[:idx]


def build_play_order(episodes, week_sequence, weeks_unlocked):
    by_week = {}
    for e in episodes:
        by_week.setdefault(e["iso_week"], []).append(e)
    for w in by_week:
        by_week[w].sort(key=lambda e: e["pubDate"])

    included_weeks = week_sequence[:weeks_unlocked]
    batches = [by_week[w] for w in included_weeks]
    return batches  # list of lists, one per unlocked week batch


def build_rss(batches, start_date):
    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
    })
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = CHANNEL_TITLE
    ET.SubElement(channel, "link").text = CHANNEL_LINK
    ET.SubElement(channel, "language").text = CHANNEL_LANGUAGE
    ET.SubElement(channel, "description").text = CHANNEL_DESCRIPTION
    ET.SubElement(channel, "itunes:author").text = CHANNEL_AUTHOR
    ET.SubElement(channel, "itunes:image", {"href": CHANNEL_IMAGE})
    ET.SubElement(channel, "itunes:explicit").text = "false"
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = CHANNEL_IMAGE
    ET.SubElement(image, "title").text = CHANNEL_TITLE
    ET.SubElement(image, "link").text = CHANNEL_LINK

    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=8)

    for batch_idx, batch in enumerate(batches):
        unlock_dt = start_dt + timedelta(days=7 * batch_idx)
        for pos, ep in enumerate(batch):
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = ep["title"]
            item_dt = unlock_dt + timedelta(minutes=5 * pos)
            ET.SubElement(item, "pubDate").text = format_datetime(item_dt)
            orig_date = ep["pubDate"][:10]
            ET.SubElement(item, "description").text = (
                f"Week {ep['iso_week']:02d} pick. Originally aired {orig_date}. "
                f"Unlocked {unlock_dt.date().isoformat()}."
            )
            guid = ET.SubElement(item, "guid", {"isPermaLink": "false"})
            guid.text = ep["guid"]
            ET.SubElement(item, "enclosure", {
                "url": ep["url"],
                "type": "audio/mpeg",
                "length": "0",
            })
            h = ep["duration_sec"] // 3600
            m = (ep["duration_sec"] % 3600) // 60
            s = ep["duration_sec"] % 60
            ET.SubElement(item, "itunes:duration").text = f"{h:02d}:{m:02d}:{s:02d}"
            ET.SubElement(item, "itunes:explicit").text = "false"

    return rss


def main():
    episodes = load_episodes()
    now_week = datetime.now(timezone.utc).isocalendar()[1]
    state = load_or_init_state(now_week)

    start_date = datetime.fromisoformat(state["start_date"]).date()
    start_week = state["start_week"]

    weeks_elapsed = (datetime.now(timezone.utc).date() - start_date).days // 7 + 1

    week_sequence = full_week_sequence(episodes, start_week)
    total_weeks = len(week_sequence)
    weeks_unlocked = min(weeks_elapsed, total_weeks)

    batches = build_play_order(episodes, week_sequence, weeks_unlocked)
    rss = build_rss(batches, start_date)

    ET.indent(rss, space="  ")
    xml_bytes = ET.tostring(rss, encoding="utf-8", xml_declaration=True)
    with open(OUTPUT_XML, "wb") as f:
        f.write(xml_bytes)

    total_eps = sum(len(b) for b in batches)
    print(f"Start date: {start_date}, start week: {start_week}")
    print(f"Weeks unlocked: {weeks_unlocked} / {total_weeks}")
    print(f"Episodes in feed: {total_eps}")
    print(f"Wrote {OUTPUT_XML}")


if __name__ == "__main__":
    main()
