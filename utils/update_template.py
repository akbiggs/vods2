import sqlite3
from pathlib import Path
from typing import List
import urllib.parse
from datetime import datetime
import sys

# Usage: python3 utils/update_template.py [numberOfEvents]
# numberOfEvents is optional, defaults to 4, max is 8

# db path
db_path = Path(__file__).parent.parent / "database.db"

# path to template output
output_file = Path(__file__).parent.parent / "templates/updates.jinja2"

def getRecentEventNames(numberOfEvents: int = 5) -> List[str]:
    """Return the most recent event names from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name
        FROM event
        ORDER BY id DESC
        LIMIT ?
    """, (numberOfEvents,))
    events = [row[0] for row in cursor.fetchall()]
    conn.close()
    return events

def update_event_links(numberOfEvents: int = 4) -> None:
    """Fetch last `numberOfEvents` and overwrites the Jinja2 template file."""
    recentEvents = getRecentEventNames(numberOfEvents)

    today = datetime.today()
    formattedDate = today.strftime("%B %d, %Y")

    # build jinja file
    jinjaContent = '<div class="updateContainer">\n    <p>Last updated: ' + formattedDate + ' | '
    links = []
    for event in recentEvents:
        eventURL = urllib.parse.quote_plus(event)
        links.append(f'<a href="/search?c1=any&c2=any&p1=&p2=&event={eventURL}&rank=any">{{{{ "{event}" }}}}</a>')
    jinjaContent += ', '.join(links)
    jinjaContent += '\n    </p>\n</div>'

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(jinjaContent)

    print(f"Updated {output_file} with {len(recentEvents)} events.")

# apparently this is best practices
if __name__ == "__main__":
    # default
    numberOfEvents = 4

    # check if user passed a value
    if len(sys.argv) > 1:
        try:
            numberOfEvents = int(sys.argv[1])
        except ValueError:
            print("Error: number of events must be an integer")
            sys.exit(1)

    # validation
    max_events = 8
    if numberOfEvents > max_events:
        print(f"Error: number of events cannot exceed {max_events}")
        sys.exit(1)
    if numberOfEvents < 1:
        print("Error: number of events must be at least 1")
        sys.exit(1)

    update_event_links(numberOfEvents)
