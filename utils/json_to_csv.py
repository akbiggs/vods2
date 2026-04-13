import json
import csv
import re
import os

INPUT_FILE = os.path.join(os.path.dirname(__file__), "playlistExport.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "output.csv")

TOURNAMENT_DATE = "2026-04-06 00:00:00+00:00"


def clean_title(title: str):

    title = re.sub(
        r"(\[?\s*(RoA2|ROA2|RoA 2|RoAII|ROAII|Rivals II|RIVALS 2|RIVALS II|Rivals of Aether 2|Rivals of Aether II|Rivals 2 Tournament|Rivals II Bracket|Rivals 2 Bracket)\s*\]?)",
        "",
        title,
        flags=re.IGNORECASE
    ).strip()
    # normalize separators
    title = title.replace(" V ", " vs ")
    title = title.replace(" v ", " vs ")
    title = title.replace(" Vs ", " vs ")
    title = title.replace(" VS ", " vs ")

    # split event / round
    parts = title.split(" - ", 2)

    # fallback safety
    if len(parts) < 3:
        return None

    match_part = parts[1].strip()
    round_part = parts[2].strip()

    # extract players + characters
    # format: P1 [C1] vs P2 [C2]
    m = re.match(
        r"(.+?)\s*\[(.+?)\]\s*vs\s*(.+?)\s*\[(.+?)\]",
        match_part,
        re.IGNORECASE
    )

    if not m:
        return None

    p1, c1, p2, c2 = m.groups()

    # only keep first character if multiple
    c1 = c1.split(",")[0].strip()
    c2 = c2.split(",")[0].strip()

    event = parts[0].strip()

    return {
        "p1": p1.strip(),
        "p1character": c1,
        "p2": p2.strip(),
        "p2character": c2,
        "event": event,
        "round": round_part,
    }


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = []

    for vid in data:
        parsed = clean_title(vid["title"])
        if not parsed:
            continue

        rows.append({
            "url": vid["videoUrl"],
            "p1": parsed["p1"],
            "p1character": parsed["p1character"],
            "p2": parsed["p2"],
            "p2character": parsed["p2character"],
            "event": parsed["event"],
            "round": parsed["round"],
            "timestamp": TOURNAMENT_DATE
        })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["url", "p1", "p1character", "p2", "p2character", "event", "round", "timestamp"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done → {OUTPUT_FILE} ({len(rows)} rows)")


if __name__ == "__main__":
    main()