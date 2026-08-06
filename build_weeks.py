#!/usr/bin/env python3
"""
Builds one self-contained RSS feed per ISO calendar week into weeks/,
each containing every historical episode published in that week (across
all years), oldest year first. Uses each episode's real original pubDate
(sorting ascending already puts oldest year first, since the episodes are
genuinely from different years) — no synthetic dates needed.

Re-run this only when episodes.json is refreshed with new episodes from
the source feed. The weekly rotation itself is handled by sync_week.py.
"""
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime

EPISODES_JSON = "episodes.json"
WEEKS_DIR = "weeks"

CHANNEL_LINK = "https://www.spreaker.com/show/foro-de-teresina"
CHANNEL_LANGUAGE = "pt"
CHANNEL_IMAGE = (
    "https://megaphone.imgix.net/podcasts/03b80a24-71dc-11ee-9304-278056d646af/"
    "image/a549074bc5d7f5ccfde8fec8e212be43.png?ixlib=rails-4.3.1&max-w=3000&max-h=3000&fit=crop&auto=format,compress"
)
CHANNEL_AUTHOR = "piauí"


def load_episodes():
    with open(EPISODES_JSON) as f:
        return json.load(f)


def build_week_rss(week_num, episodes_for_week):
    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
    })
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = f"Foro de Teresina — Week {week_num:02d} of the Year"
    ET.SubElement(channel, "link").text = CHANNEL_LINK
    ET.SubElement(channel, "language").text = CHANNEL_LANGUAGE
    ET.SubElement(channel, "description").text = (
        "Unofficial personal re-ordering of the Foro de Teresina podcast "
        f"archive: every historical episode originally published in ISO "
        f"calendar week {week_num:02d}, oldest year first. Audio is "
        "streamed from the original publisher's hosting; nothing is "
        "re-hosted here."
    )
    ET.SubElement(channel, "itunes:author").text = CHANNEL_AUTHOR
    ET.SubElement(channel, "itunes:image", {"href": CHANNEL_IMAGE})
    ET.SubElement(channel, "itunes:explicit").text = "false"
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = CHANNEL_IMAGE
    ET.SubElement(image, "title").text = channel.find("title").text
    ET.SubElement(image, "link").text = CHANNEL_LINK

    for ep in sorted(episodes_for_week, key=lambda e: e["pubDate"]):
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = ep["title"]
        dt = datetime.fromisoformat(ep["pubDate"])
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ET.SubElement(item, "pubDate").text = format_datetime(dt)
        ET.SubElement(item, "description").text = (
            f"Originally aired {ep['pubDate'][:10]}."
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
    by_week = {}
    for e in episodes:
        by_week.setdefault(e["iso_week"], []).append(e)

    os.makedirs(WEEKS_DIR, exist_ok=True)

    for week_num, eps in sorted(by_week.items()):
        rss = build_week_rss(week_num, eps)
        ET.indent(rss, space="  ")
        xml_bytes = ET.tostring(rss, encoding="utf-8", xml_declaration=True)
        path = os.path.join(WEEKS_DIR, f"week-{week_num:02d}.xml")
        with open(path, "wb") as f:
            f.write(xml_bytes)
        print(f"week {week_num:02d}: {len(eps)} episodes -> {path}")

    print(f"\nBuilt {len(by_week)} weekly feed files in {WEEKS_DIR}/")


if __name__ == "__main__":
    main()
