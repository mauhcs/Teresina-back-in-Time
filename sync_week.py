#!/usr/bin/env python3
"""
Overwrites feed.xml with the pre-built weeks/week-NN.xml file matching
the current real-world ISO calendar week. Run weekly (see
.github/workflows/update-feed.yml) so subscribers only ever see the
current week's batch.
"""
import shutil
from datetime import datetime, timezone

WEEKS_DIR = "weeks"
OUTPUT_XML = "feed.xml"


def main():
    week_num = datetime.now(timezone.utc).isocalendar()[1]
    src = f"{WEEKS_DIR}/week-{week_num:02d}.xml"
    shutil.copyfile(src, OUTPUT_XML)
    print(f"Current ISO week: {week_num:02d}")
    print(f"Copied {src} -> {OUTPUT_XML}")


if __name__ == "__main__":
    main()
