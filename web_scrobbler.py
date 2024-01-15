import datetime
import sys
import pylast
import os
import time
import sqlite3
from flask import Flask, request, render_template, redirect, url_for, abort


app = Flask(__name__)

# Define the paths to the files
CONFIG_DIR = os.path.expanduser("~/.config/pylast/")
API_KEY_FILE = os.path.join(CONFIG_DIR, "api_key")
API_SECRET_FILE = os.path.join(CONFIG_DIR, "api_secret")
SESSION_KEY_FILE = os.path.join(CONFIG_DIR, ".session_key")
DB_FILE_PATH = os.path.join(CONFIG_DIR, "artists.db")

# Dry run, yes or no?
DRY = False

# Make sure the API_KEY and API_SECRET files exist
if not os.path.exists(API_KEY_FILE) or not os.path.exists(API_SECRET_FILE):
    print("API_KEY and/or API_SECRET file(s) not found.")
    sys.exit(1)

# Read API_KEY and API_SECRET from their files
with open(API_KEY_FILE, 'r') as file:
    API_KEY = file.read().strip()

with open(API_SECRET_FILE, 'r') as file:
    API_SECRET = file.read().strip()

# Check if the session key file exists; if not, generate and save session key
if not os.path.exists(SESSION_KEY_FILE):
    skg = pylast.SessionKeyGenerator(network)
    url = skg.get_web_auth_url()

    print(f"Please authorize this script to access your account: {url}\n")
    import webbrowser
    webbrowser.open(url)

    while True:
        try:
            SESSION_KEY = skg.get_web_auth_session_key(url)
            with open(SESSION_KEY_FILE, "w") as f:
                f.write(SESSION_KEY)
            break
        except pylast.WSError:
            time.sleep(1)
else:
    with open(SESSION_KEY_FILE, 'r') as file:
        SESSION_KEY = file.read().strip()

network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET, session_key=SESSION_KEY)

@app.route('/search', methods=['POST'])
def search():
    artist = request.form['artist']
    limit = request.form['limit']
    album_details = search_albums(artist, int(limit))
    current_time = time.strftime("%I:%M %p", time.localtime(time.time()))
    return render_template('album_selection.html', artist=artist, albums=album_details, current_time=current_time)

@app.route('/scrobble', methods=['POST'])
def scrobble():
    artist = request.form['artist']
    album = request.form['album']
    time_str = request.form.get('time_str', None)  # Default to None if not provided
    try:
        scrobble_album(artist, album, time_str)
        return render_template('scrobble_confirmation.html', artist=artist, album=album, time_str=time_str)
    except Exception as e:
        return render_template('error.html', error_message=str(e))

@app.route('/')
def index():
        artists = get_all_artists()
        return render_template('search.html', artists=artists)


@app.errorhandler(404)
def page_not_found(error):
    return "Page not found", 404


def scrobble_album(artist, album, time_str=None):
    # TODO: general error handling -- scrobbling albums with 0 tracks,
    #       searching for non-existant artists, etc
    add_artist_to_db(artist)
    album_info = network.get_album(artist, album)

    tracks = album_info.get_tracks()

    now = int(time.time())

    if time_str is not None:
        # Convert the input time string to a time object
        time_obj = datetime.datetime.strptime(time_str, "%I:%M %p").time()
        # Get the current date and combine with the input time to form a datetime object
        today_date = datetime.date.today()
        now = int(datetime.datetime.combine(today_date, time_obj).timestamp())

    # Calculate the scrobble times for each track
    scrobble_times = []
    total_duration = sum(track.get_duration() for track in tracks)
    #print(tracks)
    try:
        album_title = tracks[0].get_album().title
    except AttributeError:
        # trouble grabbing album title from first track; defaulting to whatever user input was
        album_title = album
    except IndexError:
        # TODO: maybe just hide 0 track albums then? this error will
        # still be needed for manual 'Artist' 'Album' scrobbles though
        print("sorry! last.fm doesn't think that album has any tracks, so it can't be scrobbled")
        exit()

    for track in reversed(tracks):
        track_duration = track.get_duration()
        total_duration -= track_duration

        # Calculate the timestamp for this track's scrobble time
        timestamp = now - (total_duration) // 1000
        # Add the scrobble time to the list
        scrobble_times.append(timestamp)

    # Scrobble each track at the corresponding scrobble time
    for i, track in enumerate(tracks):
        le_time = time.strftime("%I:%M %p", time.localtime(scrobble_times[i]))
        print(f"Track {i+1} - {track.title} @ {le_time}")
        if (not DRY):
            network.scrobble(
                artist=track.artist.name,
                title=track.title,
                album=album_title,
                timestamp=scrobble_times[i]
            )


def search_albums(artist, limit=10):
    artist_obj = network.get_artist(artist)
    albums = artist_obj.get_top_albums(limit)
    n_albums = len(albums)
    album_details = []

    for index, album in enumerate(albums, 1):
        try:
            track_count = len(album.item.get_tracks())
            album_name = album.item.get_name()
            rank = n_albums - index + 1
            album_details.append({'name': album_name, 'track_count': track_count, 'rank': rank})

        except pylast.WSError as e:
            print(f"Error while processing album: {e}")
            album_details.append({'name': f"Error: {e}", 'track_count': 0, 'rank': n_albums - index + 1})
            continue

    return album_details

def create_db():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_artist_to_db(artist):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO artists (name) VALUES (?)', (artist,))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Artist {artist} is already in the db")
    finally:
        conn.close()

def get_all_artists():
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM artists')
    artists = [row[0] for row in cursor.fetchall()]

    conn.close()
    return artists


if __name__ == '__main__':
    create_db()
    app.run(debug=True)