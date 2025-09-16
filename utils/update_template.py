import sqlite3
from pathlib import Path
from typing import List
import urllib.parse
from datetime import datetime
import sys

# Usage: python3 utils/update_template.py    # uses default of 4 events
#        python3 utils/update_template.py 5  # uses 5 events

# Note: If you drop DB/re-ingest CSV this script will no longer
#       be able to accurately pull the latest added events because the IDs will be reset.
#       Instead it will pull the events with the most recent dates.
#       You will need to manually edit the output jinja2 file if you care enough.

# db path
db_path = Path(__file__).parent.parent / "database.db"

# path to template output
output_file = Path(__file__).parent.parent / "templates/updates/updates.jinja2"

def get_recent_event_names(num_events: int = 4) -> List[str]:
    """Return the most recent event names from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM event
        ORDER BY id DESC
        LIMIT ?
    """, (num_events,))
    events = [row[0] for row in cursor.fetchall()]
    conn.close()
    return events

def update_event_links(num_events: int = 4) -> None:
    """Fetch last `num_events` and overwrites the Jinja2 template file."""
    recent_events = get_recent_event_names(num_events)

    today = datetime.today()
    day = today.day

    # so we don't have to import another library just for this
    # https://stackoverflow.com/questions/739241/date-ordinal-output?noredirect=1&lq=1

    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    formatted_date = today.strftime(f"%B {day}{suffix}, %Y")

    # build jinja file
    jinja_content = '<div class="updateContainer">\n    <p>Last updated: ' + formatted_date + ' | ' + '\n'
    links = []
    for i, event in enumerate(recent_events):
        event_url = urllib.parse.quote_plus(event)
        # add comma except for last one
        comma = "," if i < len(recent_events) - 1 else ""
        # \t for indentation
        links.append(f'\t\t<a href="/?c1=any&c2=any&p1=&p2=&event={event_url}&rank=any">{event}</a>{comma}')
    jinja_content += '\n'.join(links)
    jinja_content += '\n    </p>\n</div>'

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(jinja_content)

    print(f"Updated {output_file} with {len(recent_events)} events.")

# apparently this is best practices
# alex: yes, it allows you to import this file without running a buncha
# python code accidentally
if __name__ == "__main__":
    # default
    num_events = 4

    # check if user passed a value
    if len(sys.argv) > 1:
        try:
            num_events = int(sys.argv[1])
        except ValueError:
            print("Error: number of events must be an integer")
            sys.exit(1)

    # validation
    max_events = 8
    if num_events > max_events:
        print(f"Error: number of events cannot exceed {max_events}")
        sys.exit(1)
    if num_events < 1:
        print("Error: number of events must be at least 1")
        sys.exit(1)

    update_event_links(num_events)
