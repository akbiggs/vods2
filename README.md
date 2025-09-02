# Rivals of Aether 2 VODs

This is a simple website for collecting and searching Rivals of Aether 2 VODs. https://www.rivals2vods.com

## Developer instructions

These are instructions for running the site locally.

### Set up your developer environment

These instructions support Windows (PowerShell) and Unix.

You only need to do this once.

1. [Install Python 3.10+](https://www.python.org/downloads/).
2. Clone the repository:

    ```sh
    git clone https://github.com/akbiggs/vods2
    ```

3. Enter the directory.

    ```sh
    cd vods2
    ```

4. Create a virtual environment in the project directory:

    ```sh
    python3 -m venv .venv
    ```

5. Activate your virtual environment. On Windows (PowerShell):

    ```sh
    .venv\Scripts\activate.ps1
    ```

    On Unix:

    ```sh
    chmod +x .venv/bin/activate && source .venv/bin/activate
    ```

6. Install dependencies.

    ```sh
    python3 -m pip install click==8.1.7 flask==3.1.0 flask-paginate==2024.4.12
    ```

7. Initialize the database. Type "confirm" when the script asks you to.

    ```sh
    python3 -m flask init-db
    ```

8. Import the VODs.

    ```sh
    python3 -m flask ingest-csv data/vods.csv
    ```

### Running the site locally

To see your changes locally:

1. Activate your virtual environment. On Windows (PowerShell):

    ```sh
    .venv\Scripts\activate.ps1
    ```

    On Unix:

    ```sh
    .venv/bin/activate
    ```

2. Run the site in debug mode. This allows you to refresh and see your changes.

    ```
    python3 -m flask run --debug
    ```

3. Go to http://localhost:5000 to see the site.

### Adding VODs manually

To add new VODs manually, you can edit `data/vods.csv` to add new rows and then
run:

```sh
python3 -m flask ingest-csv data/vods.csv
```

### Adding VODs from a YouTube channel

Adding VODs from a YouTube channel currently requires the Google Python API
Client to use YouTube's API.

```sh
python3 -m pip install google-api-python-client==2.179.0
```

You also need to
[get a YouTube API key](https://developers.google.com/youtube/v3/getting-started)
and put it in a `youtube_api_key` file in the top-level `vods2` folder. Note
that there is no file extension on `youtube_api_key`.

You can add VODs from a YouTube channel to the database using the following
command:

```sh
python3 -m flask ingest-channel <channel_id> '<search_query>' '<video_title_format>'
```

where:

-   `channel_id` is the YouTube channel ID. I get the ID using [this website](https://www.streamweasels.com/%20tools/youtube-channel-id-and-%20user-id-convertor/).
    -   The channel IDs for the websites I pull from are stored in [`data/channel_ids.txt`](https://github.com/akbiggs/vods2/blob/main/data/channel_ids.txt).
-   `search_query` is an optional query to reduce what videos get queried from the channel. For example if you are trying to get VODs that have the word "Blah" in the title, you can type `'"Blah"'`.
-   `video_title_format` describes the format of the video title (where the event name, the player names, and the character names are).
    -   `%P1`: Where the first player name goes.
    -   `%P2`: Where the second player name goes.
    -   `%C1`: Where the first player's character(s) goes.
    -   `%C2`: Where the second player's character(s) goes.
    -   `%E`: (optional) The event name.
    -   `%R`: (optional) The round name.
    -   `%V`: (optional) Some versus text, for example "vs", "VS", "vs.".
    -   `%ROA`: (optional) Some reference to Rivals of Aether II, for example "RoA2", "Rivals of Aether II", "Rivals 2".

For example, if you want to add Rivals II videos from [Collision Gaming Series](https://www.youtube.com/@CollisionSeries), an example video title is "Bay State Beatdown 138 Rivals 2 - FC | Vidad (Clairen) vs yc | Pip (Maypul) - Grand Finals", and the corresponding command would be:

```sh
python3 -m flask ingest-channel UCn_LdOLhjFF3_fgBrk-7y9A '""' '%E Rivals 2 - %P1 (%C1) %V %P2 (%C2) - %R'
```

If you only want VODs from Bay State Beatdown 138, the command would be:

```sh
python3 -m flask ingest-channel UCn_LdOLhjFF3_fgBrk-7y9A '"Bay State Beatdown 138"' '%E Rivals 2 - %P1 (%C1) %V %P2 (%C2) - %R'
```

### Adding VODs from a YouTube playlist

You can add VODs from a YouTube playlist to the database using the following
command:

```sh
python3 -m flask ingest-playlist "playlist_url" '<event_name>' '<video_title_format>'
```

where:

-   `playlist_url` is the url of the playlist you wish to add.
-   `event_name` is the name of the event or tournament name you wish to add.
-   `video_title_format` describes the format of the video title (where the event name, the player names, and the character names are).
    -   `%P1`: Where the first player name goes.
    -   `%P2`: Where the second player name goes.
    -   `%C1`: Where the first player's character(s) goes.
    -   `%C2`: Where the second player's character(s) goes.
    -   `%E`: (optional) The event name.
    -   `%R`: (optional) The round name.
    -   `%V`: (optional) Some versus text, for example "vs", "VS", "vs.".

For example if you want to add the playlist for [Monthly of Aether #9: NA](https://www.youtube.com/playlist?list=PLG_10Q9RHnFwFQwGbNUmz_hO6mUJiAnei), an example video title is:

> Ant ( Absa ) vs Bbatts ( Fleet ) - [ Pools ]

The corresponding command would be:

```sh
python3 -m flask ingest-playlist "https://www.youtube.com/playlist?list=PLG_10Q9RHnFwFQwGbNUmz_hO6mUJiAnei" "Monthly of Aether #9: NA" "%P1 ( %C1 ) %V %P2 ( %C2 ) - [ %R ]"
```

### Adding VODs automatically from a large VOD (experimental)

Sometimes large VODs are uploaded without timestamps for matches. We try to
support these vods by analyzing the video for matches automatically.

This currently requires Google's genai library to use Gemini's video analysis.

```sh
python3 -m pip install -q -U google-genai==1.32.0
```

You also need to
[get a Gemini API key](https://aistudio.google.com/apikey)
and put it in a `gemini_api_key` file in the top-level `vods2` folder. Note
that there is no file extension on `gemini_api_key`.

You can then ingest a large VOD using:

```sh
python3 -m flask extract-vods "<youtube_url>" "<event_name>"
```

For example for Wasteland Warriors #22:

```sh
python3 -m flask extract-vods "https://www.youtube.com/watch?v=gWtNu_6hoDY" "Wasteland Warriors #22"
```

### Exporting VODs list

After verifying the new VODs you can export them to `data/vods.csv` using the
following command:

```sh
python3 -m flask export-vods data/vods.csv
```

On the production site to get the new VODs, I pull the changes to
`data/vods.csv` and then run:

```sh
python3 -m flask ingest-csv data/vods.csv
```

### Hosting

I use [PythonAnywhere](https://www.pythonanywhere.com) to host the site.
