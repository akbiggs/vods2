import argparse
import csv
import re
import requests
from datetime import datetime, timezone
from pathlib import Path

# Usage: python3 playlist_to_csv.py "playlist_url"

OUTPUT_FILE = Path(__file__).resolve().parent / "output.csv"

# API KEY

def load_api_key():
    with open("youtube_api_key", "r", encoding="utf-8") as f:
        return f.read().strip()

# Playlist ID extraction

def extract_playlist_id(url: str) -> str:
    match = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("Invalid playlist URL")
    return match.group(1)

# Timestamp conversion

def convert_youtube_timestamp(ts: str) -> str:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.astimezone(timezone.utc).isoformat(sep=" ")

# Fetch playlist videos

def fetch_playlist_videos(api_key: str, playlist_id: str):
    videos = []
    page_token = None

    while True:
        url = "https://www.googleapis.com/youtube/v3/playlistItems"

        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": api_key,
        }

        if page_token:
            params["pageToken"] = page_token

        res = requests.get(url, params=params)
        data = res.json()

        for item in data.get("items", []):
            snippet = item["snippet"]

            videos.append({
                "title": snippet["title"],
                "videoId": snippet["resourceId"]["videoId"],
                "publishedAt": snippet.get("publishedAt", "")
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break
    print(f"Fetched {len(videos)} videos from playlist {playlist_id}")
    return videos

# Strip brackets / parentheses

def strip_brackets(text: str) -> str:
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    return text.strip()

# Title parser

def clean_title(title: str):
    title = title.replace(" V ", " vs ")
    title = title.replace(" v ", " vs ")
    title = title.replace(" Vs ", " vs ")
    title = title.replace(" VS ", " vs ")
    title = title.replace(" | ", " - ")

    # Remove references to RoA, taken from db.py

    title = re.sub(
        r"(\bRoA2\b|\bROA2\b|\bRoA 2\b|\bRoAII\b|\bRivals II\b|\bRIVALS 2\b|"
        r"\bRivals of Aether 2\b|\bRivals of Aether II\b|\bRivals II Bracket\b|"
        r"\bRivals 2 Bracket\b|\bRivals 2 Tournament\b)",
        "",
        title,
        flags=re.IGNORECASE
    )

    parts = title.split(" - ")
    if len(parts) < 3:
        return None

    event = parts[0].strip()
    match_part = parts[1].strip()
    round_part = parts[2].strip()

    # try standard format first
    m = re.match(
        r"(.+?)\s*\[(.+?)\]\s*vs\s*(.+?)\s*\[(.+?)\]",
        match_part,
        re.IGNORECASE
    )

    # fallback: (Character) format
    if not m:
        m = re.match(
            r"(.+?)\s*\((.+?)\)\s*vs\s*(.+?)\s*\((.+?)\)",
            match_part,
            re.IGNORECASE
        )

    # fallback: mixed format like [Player](Character)
    if not m:
        m = re.match(
            r"\[(.+?)\]\s*\((.+?)\)\s*vs\s*\[(.+?)\]\s*\((.+?)\)",
            match_part,
            re.IGNORECASE
        )

    if not m:
        return None

        if not m:
            return None

    p1, c1, p2, c2 = m.groups()

    return {
        "p1": p1.strip(),
        "p1character": c1.split(",")[0].strip(),
        "p2": p2.strip(),
        "p2character": c2.split(",")[0].strip(),
        "event": strip_brackets(event),
        "round": strip_brackets(round_part)
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()

    api_key = load_api_key()
    playlist_id = extract_playlist_id(args.url)

    videos = fetch_playlist_videos(api_key, playlist_id)

    rows = []

    for vid in videos:
        parsed = clean_title(vid["title"])
        if not parsed:
            print(f"Skipping {vid['title']}")
            continue

        timestamp = ""
        if vid.get("publishedAt"):
            timestamp = convert_youtube_timestamp(vid["publishedAt"])

        rows.append({
            "url": f"https://www.youtube.com/watch?v={vid['videoId']}",
            "p1": parsed["p1"],
            "p1character": parsed["p1character"],
            "p2": parsed["p2"],
            "p2character": parsed["p2character"],
            "event": parsed["event"],
            "round": parsed["round"],
            "timestamp": timestamp
        })
        print(f"Added {vid['title']}")

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "url",
                "p1",
                "p1character",
                "p2",
                "p2character",
                "event",
                "round",
                "timestamp"
            ]
        )
        writer.writerows(rows)

    print(f"Done → {OUTPUT_FILE} ({len(rows)} rows)")


if __name__ == "__main__":
    main()