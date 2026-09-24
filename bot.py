#!/usr/bin/env python3
"""Typeface of the Day: posts one typeface + fun fact to a Slack channel.

Usage:
  python3 bot.py                    # post today's typeface (only during the 9am hour)
  python3 bot.py --force            # post now regardless of the time
  python3 bot.py --dry-run --force  # print the Slack payload instead of posting
  python3 bot.py --date 2026-12-25 --dry-run --force
  python3 bot.py --validate         # sanity-check typefaces.json
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TIMEZONE = os.environ.get("BOT_TIMEZONE", "America/Toronto")
POST_HOUR = int(os.environ.get("BOT_POST_HOUR", "9"))
DATA_FILE = Path(__file__).with_name("typefaces.json")
FIELDS = ("name", "designer", "year", "classification", "fact")


def load_typefaces():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def typeface_for(day, typefaces):
    # Index by position in a leap year so every calendar date (incl. Feb 29)
    # always maps to the same typeface, year after year.
    index = date(2024, day.month, day.day).timetuple().tm_yday - 1
    return typefaces[index]


def build_payload(day, tf):
    label = f"{day:%B} {day.day}"
    search = "https://www.google.com/search?q=" + urllib.parse.quote_plus(f"{tf['name']} typeface")
    return {
        "text": f"Typeface of the Day: {tf['name']}. {tf['fact']}",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": f"🔤 Typeface of the Day: {label}"}},
            {"type": "section", "text": {"type": "mrkdwn", "text": f"*{tf['name']}*"}},
            {
                "type": "context",
                "elements": [{
                    "type": "mrkdwn",
                    "text": f"✏️ {tf['designer']}  ·  📅 {tf['year']}  ·  🏷️ {tf['classification']}",
                }],
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": f"💡 *Fun fact:* {tf['fact']}"}},
            {
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {"type": "plain_text", "text": "See it in action"},
                    "url": search,
                }],
            },
        ],
    }


def post(payload, webhook):
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            status = resp.status
    except urllib.error.HTTPError as e:
        body, status = e.read().decode(), e.code
    if status != 200 or body != "ok":
        raise RuntimeError(f"Slack rejected the post ({status}: {body}). Check that SLACK_WEBHOOK_URL is the full, current webhook URL.")


def validate(typefaces):
    problems = []
    if len(typefaces) != 366:
        problems.append(f"expected 366 entries, found {len(typefaces)}")
    seen = set()
    for i, tf in enumerate(typefaces):
        for field in FIELDS:
            if not str(tf.get(field, "")).strip():
                problems.append(f"entry {i} ({tf.get('name')}) is missing '{field}'")
        if tf.get("name") in seen:
            problems.append(f"duplicate typeface: {tf['name']}")
        seen.add(tf.get("name"))
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--force", action="store_true", help="post regardless of the current hour")
    parser.add_argument("--dry-run", action="store_true", help="print the payload instead of posting")
    parser.add_argument("--date", help="use this date (YYYY-MM-DD) instead of today")
    parser.add_argument("--validate", action="store_true", help="check typefaces.json and exit")
    args = parser.parse_args()

    typefaces = load_typefaces()

    if args.validate:
        problems = validate(typefaces)
        for p in problems:
            print("✗", p)
        print("✓ typefaces.json looks good" if not problems else f"{len(problems)} problem(s)")
        return 1 if problems else 0

    now = datetime.now(ZoneInfo(TIMEZONE))
    if not args.force and now.hour != POST_HOUR:
        # The workflow runs at two UTC times to cover daylight saving;
        # only the run that lands in the 9am local hour posts.
        print(f"It's {now:%H:%M} in {TIMEZONE}, not the {POST_HOUR}:00 hour. Skipping.")
        return 0

    day = date.fromisoformat(args.date) if args.date else now.date()
    payload = build_payload(day, typeface_for(day, typefaces))

    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook:
        print("SLACK_WEBHOOK_URL is not set. Add it under the repo's Settings → Secrets and variables → Actions.", file=sys.stderr)
        return 1
    post(payload, webhook)
    print(f"Posted {payload['blocks'][1]['text']['text']} for {day}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
