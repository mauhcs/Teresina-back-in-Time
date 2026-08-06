#!/usr/bin/env python3
"""
Builds a synthetic RSS feed for "Foro de Teresina" that reorders the
original episodes into week-of-year order: for each ISO calendar week,
all historical episodes published in that week (across every year),
oldest year first. Enclosures point at the original hosted MP3 files;
nothing is re-hosted or copied.
"""
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

EPISODES_JSON = "episodes.json"
OUTPUT_XML = "feed.xml"

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
    "Audio is streamed from the original publisher's hosting; nothing is re-hosted here."
)


def load_episodes():
    with open(EPISODES_JSON) as f:
        return json.load(f)


def build_play_order(episodes, start_week):
    weeks_present = sorted(set(e["iso_week"] for e in episodes))
    n = len(weeks_present)
    idx = weeks_present.index(start_week) if start_week in weeks_present else 0
    week_sequence = weeks_present[idx:] + weeks_present[:idx]

    by_week = {}
    for e in episodes:
        by_week.setdefault(e["iso_week"], []).append(e)
    for w in by_week:
        by_week[w].sort(key=lambda e: e["pubDate"])

    ordered = []
    for w in week_sequence:
        ordered.extend(by_week[w])
    return ordered


def build_rss(ordered):
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

    anchor = datetime(2024, 1, 1, tzinfo=timezone.utc)
    for i, ep in enumerate(ordered):
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = ep["title"]
        synthetic_date = anchor + timedelta(hours=i)
        ET.SubElement(item, "pubDate").text = format_datetime(synthetic_date)
        orig_date = ep["pubDate"][:10]
        ET.SubElement(item, "description").text = (
            f"Week {ep['iso_week']:02d} pick. Originally aired {orig_date}."
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
    now_week = datetime.now().isocalendar()[1]
    ordered = build_play_order(episodes, now_week)
    rss = build_rss(ordered)

    ET.indent(rss, space="  ")
    xml_bytes = ET.tostring(rss, encoding="utf-8", xml_declaration=True)
    with open(OUTPUT_XML, "wb") as f:
        f.write(xml_bytes)

    print(f"Start week: {now_week}")
    print(f"Total episodes in feed: {len(ordered)}")
    print(f"Wrote {OUTPUT_XML}")


if __name__ == "__main__":
    main()
