import sqlite3
import click
from datetime import datetime
from flask import current_app, g

from models import Vod

CHAR_NAME_TO_ID = {
    "clairen": 1,
    "ranno": 2,
    "zetterburn": 3,
    "forsburn": 4,
    "orcane": 5,
    "fleet": 6,
    "kragg": 7,
    "wrastor": 8,
    "loxodont": 9,
    "maypul": 10,
    "etalus": 11,
    "olympia": 12
}

# STATUS VALUES

NOT_REVIEWED_STATUS = 1
REJECTED_STATUS = 2
APPROVED_STATUS = 3

# GAME VALUES

RIVALS_OF_AETHER_TWO = 1

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
           'database.db',
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

def get_character_id(name):
    name = name.lower()

    # Common nicknames and misspellings.
    if name == 'clarien': name = 'clairen'
    if name == 'eta': name = 'etalus'
    if name == 'zetter': name = 'zetterburn'
    if name == 'zettersburn': name = 'zetterburn'
    if name == 'fors': name = 'forsburn'
    if name == 'oly': name = 'olympia'

    return CHAR_NAME_TO_ID.get(name)

def ensure_event(event):
    db = get_db()
    entry = db.cursor().execute("SELECT id, name FROM event WHERE name = ?;", (event,)).fetchone()
    if not entry:
        db.cursor().execute("INSERT INTO event (name) VALUES (?);", (event,))
        entry = db.cursor().execute("SELECT id, name FROM event WHERE name = ?;", (event,)).fetchone()
    
    return entry[0] if entry else None

def ensure_player(player):
    db = get_db()
    entry = db.cursor().execute("SELECT id, tag FROM player WHERE tag = ?;", (player,)).fetchone()
    if not entry:
        db.cursor().execute("INSERT INTO player (tag) VALUES (?);", (player,))
        entry = db.cursor().execute("SELECT id, tag FROM player WHERE tag = ?;", (player,)).fetchone()
    
    return entry[0] if entry else None

def create_submission(url, p1_char, p2_char, p1_tag, p2_tag, event, round, date):
    db = get_db()
    db.cursor().execute("""
    INSERT INTO submission (game_id, url, status, p1, c1, p2, c2, event, round, date)
    VALUES                 (?,       ?,   ?,      ?,  ?,  ?,  ?,  ?,     ?,     ?);
    """,
    (RIVALS_OF_AETHER_TWO, url, NOT_REVIEWED_STATUS, p1_tag, p1_char, p2_tag, p2_char, event, round, date,))
    db.commit()

def vod_exists(url):
    db = get_db()
    existing_vod = db.cursor().execute("SELECT id from vod WHERE url = ? LIMIT 1;", (url,)).fetchone()
    return True if existing_vod else False

def latest_vods(amount=100):
    db = get_db()
    vods = db.cursor().execute("""
    SELECT vod.id, vod.url, p1.tag, p2.tag, c1.name, c1.icon_url, c2.name, c2.icon_url, e.name, vod.round, vod.vod_date
    FROM vod
        INNER JOIN event e ON e.id = vod.event_id
        INNER JOIN player p1 ON p1.id = vod.p1_id
        INNER JOIN player p2 ON p2.id = vod.p2_id
        INNER JOIN game_character c1 ON c1.id = vod.c1_id
        INNER JOIN game_character c2 ON c2.id = vod.c2_id
    ORDER BY vod_date DESC
    LIMIT ?
    """, (amount,)).fetchall()
    
    result = []
    for id, url, p1_tag, p2_tag, c1_name, c1_icon_url, c2_name, c2_icon_url, event, round, vod_date in vods:
        result.append(Vod(
            url=url,
            round=round,
            p1_tag=p1_tag,
            p2_tag=p2_tag,
            c1_icon_url=c1_icon_url,
            c2_icon_url=c2_icon_url,
            vod_date=vod_date,
            event_name=event
        ))
    return result

def search_vods(p1, p2, c1, c2, event, rank, amount=200):
    db = get_db()

    p1_match = '%' + p1 + '%'
    p2_match = '%' + p2 + '%'
    c1_match = '%' + c1 + '%'
    c2_match = '%' + c2 + '%'
    event_match = '%' + event + '%'

    lunarank_query = ''
    if rank and rank.lower() in ['one_lunarank', 'two_lunarank']:
        lunarank_players = []
        with open('data/lunarank.txt') as f:
            for line in f.readlines():
                lunarank_players.append(line.strip().lower())
        if rank == 'one_lunarank':
            p1_query = ' OR '.join([f"p1.tag LIKE '%{p}%'" for p in lunarank_players])
            p2_query = ' OR '.join([f"p2.tag LIKE '%{p}%'" for p in lunarank_players])
            lunarank_query = f'AND (({p1_query}) OR ({p2_query}))'
        elif rank == 'two_lunarank':
            p1_query = ' OR '.join([f"p1.tag LIKE '%{p}%'" for p in lunarank_players])
            p2_query = ' OR '.join([f"p2.tag LIKE '%{p}%'" for p in lunarank_players])
            lunarank_query = f'AND ({p1_query}) AND ({p2_query})'

    print(lunarank_query)
    vods = None
    if c1 != c2:
        vods = db.cursor().execute("""
        SELECT vod.id, vod.url, p1.tag, p2.tag, c1.name, c1.icon_url, c2.name, c2.icon_url, e.name, vod.round, vod.vod_date
        FROM vod
            INNER JOIN event e ON e.id = vod.event_id
            INNER JOIN player p1 ON p1.id = vod.p1_id
            INNER JOIN player p2 ON p2.id = vod.p2_id
            INNER JOIN game_character c1 ON c1.id = vod.c1_id
            INNER JOIN game_character c2 ON c2.id = vod.c2_id
        WHERE
            (p1.tag LIKE ? OR p2.tag LIKE ?)
            AND (p1.tag LIKE ? OR p2.tag LIKE ?)
            AND (c1.name LIKE ? OR c2.name LIKE ?)
            AND (c1.name LIKE ? OR c2.name LIKE ?)
            AND (e.name LIKE ?) """ + lunarank_query + """
        ORDER BY vod_date DESC
        LIMIT ?;
        """, (p1_match, p1_match, p2_match, p2_match, c1_match, c1_match, c2_match, c2_match, event_match, amount,)).fetchall()
    else:
        vods = db.cursor().execute("""
        SELECT vod.id, vod.url, p1.tag, p2.tag, c1.name, c1.icon_url, c2.name, c2.icon_url, e.name, vod.round, vod.vod_date
        FROM vod
            INNER JOIN event e ON e.id = vod.event_id
            INNER JOIN player p1 ON p1.id = vod.p1_id
            INNER JOIN player p2 ON p2.id = vod.p2_id
            INNER JOIN game_character c1 ON c1.id = vod.c1_id
            INNER JOIN game_character c2 ON c2.id = vod.c2_id
        WHERE
            (p1.tag LIKE ? OR p2.tag LIKE ?)
            AND (p1.tag LIKE ? OR p2.tag LIKE ?)
            AND (c1.name LIKE ? AND c2.name LIKE ?)
            AND (e.name LIKE ?) """ + lunarank_query + """
        ORDER BY vod_date DESC
        LIMIT ?;
        """, (p1_match, p1_match, p2_match, p2_match, c1_match, c1_match, event_match, amount,)).fetchall()

    result = []
    for id, url, p1_tag, p2_tag, c1_name, c1_icon_url, c2_name, c2_icon_url, event, round, vod_date in vods:
        # Make the character order match the search query if it doesn't already.
        if c2_name.lower() == c1:
            result.append(Vod(
                url=url,
                round=round,
                p1_tag=p2_tag,
                p2_tag=p1_tag,
                c1_icon_url=c2_icon_url,
                c2_icon_url=c1_icon_url,
                vod_date=vod_date,
                event_name=event
            ))
        else:
            result.append(Vod(
                url=url,
                round=round,
                p1_tag=p1_tag,
                p2_tag=p2_tag,
                c1_icon_url=c1_icon_url,
                c2_icon_url=c2_icon_url,
                vod_date=vod_date,
                event_name=event
            ))
    return result

def parse_date(str):
    vod_parts = list(str.split('/'))
    if vod_parts == 3:
        try:
            month = int(vod_parts[0])
            day = int(vod_parts[1])
            year = int('20' + vod_parts[2])
        except Exception as e:
            print(e)

        return datetime(year, month, day)
    elif vod_parts == 2:
        try:
            month = int(vod_parts[0])
            day = int(vod_parts[1])
            year = datetime.now().year
        except Exception as e:
            print(e)
        return datetime(year, month, day)

    return None

# COMMANDS

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    response = input("This is going to drop the database. Type \"confirm\" to confirm: ")
    if response != "confirm":
        print("Aborting.")
        return

    init_db()
    click.echo('Initialized the database.')

@click.command('review-submissions')
def review_submissions_command():
    db = get_db()
    submissions = db.cursor().execute("SELECT id,url,p1,c1,p2,c2,round,event,date FROM submission WHERE status = ?;", (NOT_REVIEWED_STATUS,)).fetchall()
    click.echo(f"{len(submissions)} submissions to review.")
    # TODO: Support dates.
    for (id,url,p1,c1,p2,c2,round,event,date_str) in submissions:
        while True:
            # Build the info string.
            def display_info(id, url, p1, c1, p2, c2, event, round, date_str):
                info = f"ID={id} URL={url}"
                if p1:
                    info += f" p1=\"{p1}\""
                if c1:
                    info += f" c1=\"{c1}\""
                if p2:
                    info += f" p2=\"{p2}\""
                if c2:
                    info += f" c2=\"{c2}\""
                if event:
                    info += f" event=\"{event}\""
                if round:
                    info += f" round=\"{round}\""
                if date_str:
                    info += f" date=\"{date_str}\""
                click.echo(info)
            display_info(id, url, p1, c1, p2, c2, event, round, date_str)
            action = input("Approve [A] Edit [E] Skip [S] Reject [R]: ").lower()
            if action == 'a':
                event_id = ensure_event(event)
                p1_id = ensure_player(p1)
                p2_id = ensure_player(p2)
                c1_id = get_character_id(c1) or ''
                c2_id = get_character_id(c2) or ''
                vod_date = parse_date(date_str) or None
                db.cursor().execute('UPDATE submission SET status = ? WHERE id = ?;', (APPROVED_STATUS, id,))
                db.cursor().execute('''
                                    INSERT INTO vod (game_id, event_id, url, p1_id, p2_id, c1_id, c2_id, round, vod_date)
                                    VALUES          (?,       ?,        ?,   ?,     ?,     ?,     ?,     ?,     ?);''',
                                    (RIVALS_OF_AETHER_TWO, event_id, url, p1_id, p2_id, c1_id, c2_id, round, vod_date.isoformat() if vod_date else ''))
                db.commit()
                break
            elif action == 'r':
                db.cursor().execute('UPDATE submission SET status = ? WHERE id = ?;', (REJECTED_STATUS, id,))
                db.commit()
                break
            elif action == 's':
                break
            elif action == 'e':
                url = prompt('URL', url)
                p1 = prompt('Player 1', p1)
                c1 = prompt('Char 1', c1)
                p2 = prompt('Player 2', p2)
                c2 = prompt('Char 2', c2)
                event = prompt('Event', event)
                round = prompt('Round', round)

                date_str = prompt('Date (MM/DD/YY)', date_str)
                vod_date = parse_date(date_str) or None

                display_info(id, url, p1, c1, p2, c2, event, round, date_str)
                response = input('Commit this to the database? [y/n] ')
                if response in ['y', 'yes']:
                    p1_id = ensure_player(p1)
                    p2_id = ensure_player(p2)
                    c1_id = get_character_id(c1)
                    c2_id = get_character_id(c2)
                    event_id = ensure_event(event)

                    db.cursor().execute('''
                        INSERT INTO vod (game_id, event_id, url, p1_id, p2_id, c1_id, c2_id, round, vod_date)
                        VALUES          (?,       ?,        ?,   ?,     ?,     ?,     ?,     ?,     ?);''',
                        (RIVALS_OF_AETHER_TWO, event_id, url, p1_id, p2_id, c1_id, c2_id, round, vod_date.isoformat() if vod_date else ''))
                    
                    db.commit()

                break
            else:
                click.echo('Unknown action.')

@click.command('ingest-csv')
@click.argument('filename')
def ingest_csv_command(filename):
    import csv

    db = get_db()
    num_vods = 0
    with open(filename) as csvfile:
        for url, p1, c1, p2, c2, event, round, vod_time in csv.reader(csvfile):
            if vod_exists(url):
                click.echo(f"Skipping existing vod {url}.")
                continue

            p1_id = ensure_player(p1)
            p2_id = ensure_player(p2)
            event_id = ensure_event(event)
            c1_id = get_character_id(c1)
            c2_id = get_character_id(c2)

            num_vods += 1
            db.cursor().execute("""
                              INSERT INTO vod (game_id, event_id, url, p1_id, p2_id, c1_id, c2_id, round, vod_date)
                              VALUES          (?,       ?,        ?,   ?,     ?,     ?,     ?,     ?,     ?);
                              """, (RIVALS_OF_AETHER_TWO, event_id, url, p1_id, p2_id, c1_id, c2_id, round, vod_time,))
    db.commit()
    click.echo(f"Ingested {num_vods} vods.")

@click.command('ingest-channel')
@click.argument('channel_id')
@click.argument('query')
@click.argument('format')
def ingest_channel_command(channel_id, query, format):
    import googleapiclient.discovery
    import googleapiclient.errors
    import os
    import re

    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    api_key = None
    with open('youtube_api_key') as f:
        api_key = f.readline().strip()

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)

    def get_page(page_token=None):
        request = youtube.search().list(
            part="snippet",
            maxResults=50,
            channelId=channel_id,
            q=query,
            pageToken=page_token
        )
        return request.execute()

    format_regex_str = (re.escape(format)
                    .replace('%SIDE', '(([\s*W\s*])|([\s*L\s*]))')
                    .replace('%E', '(?P<event>[\s*#*\(*\s*\w~#&;\-:.\)*]+)')
                    .replace('%P1', '(?P<p1>[\s*\w\$|&;~!?#.@\-\+]+)')
                    .replace('%P2', '(?P<p2>[\s*\w\$|&;~!?#.@\-\+]+)')
                    .replace('%C1', '(?P<c1>[\s*\w/*,*]+)')
                    .replace('%C2', '(?P<c2>[\s*\w/*,*]+)')
                    .replace('%V', '((vs.)|(vs)|(Vs.)|(VS.)|(Vs)|(VS))')
                    .replace('%ROA', '((RoA2)|(ROA2)|(RoA 2)|(ROA 2)|(RoAII)|(ROAII)|(Rivals II)|(Rivals 2)|(Rivals of Aether 2)|(Rivals of Aether II)|(Rivals II Bracket)|(Rivals 2 Bracket))?')
                    .replace('%R', '(?P<round>[\s*\(*\s*\w\-#&;\)*]+)'))
    print(format_regex_str)
    format_regex = re.compile(format_regex_str)

    db = get_db()

    def ingest_page(page):
        items = page.get('items')
        if not items:
            return []
        
        results = []
        for item in items:
            # Ignore playlists, just grab videos.
            if not item.get('id') or not item['id'].get('videoId'):
                continue
            video_id = item['id']['videoId']
            url = f"https://www.youtube.com/watch?v={video_id}"
            snippet = item['snippet']
            published_at = snippet['publishedAt']
            title = snippet['title']

            existing_vod = db.cursor().execute("SELECT id from vod WHERE url = ? LIMIT 1;", (url,)).fetchone()
            if existing_vod:
                click.echo(f'ALREADY PRESENT: {title}')
                continue

            info = format_regex.match(title.strip())
            if not info:
                click.echo(f'DOES NOT MATCH: {title}')
                continue
            p1 = info.group('p1')
            p2 = info.group('p2')

            c1 = None
            if info.groupdict().get('c1'):
                c1 = info.group('c1').lower().split(',')[0].split('/')[0].replace('P1 ', '').replace('P2 ', '')
            else:
                c1 = prompt(f"c1 for {url}")
            c2 = None
            if info.groupdict().get('c2'):
                c2 = info.group('c2').lower().split(',')[0].split('/')[0].replace('P1 ', '').replace('P2 ', '')
            else:
                c2 = prompt(f"c2 for {url}")
            event = info.groupdict().get('event') or 'Unknown'
            round = info.groupdict().get('round') or ''

            # TODO: Parse round name info.
            event_id = ensure_event(event)
            p1_id = ensure_player(p1)
            p2_id = ensure_player(p2)
            c1_id = get_character_id(c1)
            if not c1_id:
                # click.echo(f"Unknown character {c1} for {url}, skipping VOD.")
                continue

            c2_id = get_character_id(c2)
            if not c2_id:
                # click.echo(f"Unknown character {c2} for {url}, skipping VOD.")
                continue

            result = f'p1={p1} c1={c1} p2={p2} c2={c2} event={event} round={round} vod_date={published_at} url={url}'
            click.echo(result)
            results.append(result)

            db.cursor().execute("""
                              INSERT INTO vod (game_id, event_id, url, p1_id, p2_id, c1_id, c2_id, vod_date, round)
                              VALUES          (?,       ?,        ?,   ?,     ?,     ?,     ?,     ?,        ?);
                              """, (RIVALS_OF_AETHER_TWO, event_id, url, p1_id, p2_id, c1_id, c2_id, published_at, round,))
        
        return results

    
    page = get_page()
    results = []
    results += ingest_page(page)
    while page.get('nextPageToken'):
        page = get_page(page['nextPageToken'])
        results += ingest_page(page)
    
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

    click.echo('\n'.join(results))
    response = input(f'Are you sure you want to commit {len(results)} VODs? [y/n] ')
    if response in ['y', 'yes']:
        db.commit()
    else:
        click.echo('Aborting.')
        return

@click.command('export-vods')
@click.argument('filename')
def export_vods_command(filename):
    import csv

    db = get_db()
    vods = db.cursor().execute("""
    SELECT vod.id, vod.url, p1.tag, p2.tag, c1.name, c2.name, e.name, vod.round, vod.vod_date
    FROM vod
        INNER JOIN event e ON e.id = vod.event_id
        INNER JOIN player p1 ON p1.id = vod.p1_id
        INNER JOIN player p2 ON p2.id = vod.p2_id
        INNER JOIN game_character c1 ON c1.id = vod.c1_id
        INNER JOIN game_character c2 ON c2.id = vod.c2_id
    ORDER BY vod_date ASC
    """, ()).fetchall()
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        vod_writer = csv.writer(csvfile)
        for id, url, p1_tag, p2_tag, c1_name, c2_name, event_name, round, vod_date in vods:
            row = [url, p1_tag, c1_name, p2_tag, c2_name, event_name, round if round else '', vod_date if vod_date else '']
            vod_writer.writerow(row)

def prompt(text, default=None):
    value = input(f'{text} ' + (f'[{default}]' if default else '') + ': ')
    return value if value else default
    

sqlite3.register_converter(
    "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(review_submissions_command)
    app.cli.add_command(ingest_channel_command)
    app.cli.add_command(ingest_csv_command)
    app.cli.add_command(export_vods_command)