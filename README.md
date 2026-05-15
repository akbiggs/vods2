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
    pip install -r requirements.txt
    ```

7. Initialize the database. Type "confirm" when the script asks you to.

    ```sh
    python3 -m flask init-db
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

### Adding VODs

Manually adding VODs can be added in two ways:

1. From a CSV file
2. From a Google Sheet

_A Google Sheet is recommended but instructions for both are provided below._

#### Adding VODs from a CSV file

```sh
python3 -m flask ingest-csv
```

This defaults to `data/vods.csv` however you can customize the path to the CSV file with an additional argument.

```sh
python3 -m flask ingest-csv directory/file.csv
```

### Adding VODs from a Google Sheet

Using a Google Sheet is recommended over a CSV file because it allows contributors to update VOD data without needing to commit changes to a tracked file or create pull requests. However the setup is longer.

---

#### 1. Create a Google Cloud project

You must enable the Google Sheets API:

https://developers.google.com/workspace/guides/create-project

---

#### 2. Create a service account and download credentials

- Create a service account in your Google Cloud project
- Generate a **JSON key file**
- Download it and place it in the top-level `vods2` directory

The file must be named:

```txt
google_service_account.json
```

#### 3. Share your Google Sheet with the service account

Then:

- Open your Google Sheet
- Click Share
- Add the email within the `client_email` field as an editor.

Without this step, the application will not be able to access the sheet.

#### 4. Configure your sheet in the project

Open `utils/authenticate_google_sheet.py` and set the following variables:

```python
sheet_id = 'YOUR_SHEET_ID'
worksheet_name = 'YOUR_WORKSHEET_NAME'
```

You can find the sheet ID in the URL:

`https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`

You can find the worksheet name at the bottom of the sheet.

For example our Google Sheet's URL is `https://docs.google.com/spreadsheets/d/1RRblTHe9hmlQDmOw05dglEXmnuH0fcB7f-ZqHjBOyT4` and the worksheet name is `vods`.

```python
sheet_id = '1RRblTHe9hmlQDmOw05dglEXmnuH0fcB7f-ZqHjBOyT4'
worksheet_name = 'vods'
```

#### 5. Importing and exporting VODs from the Google Sheet

```sh
python3 -m flask ingest-sheet
python3 -m flask export-sheet
```

On production, new updates are typically pulled by running:

```sh
python3 -m flask export-sheet
```

### Adding VODs from a YouTube channel

You will need to
[get a YouTube API key](https://developers.google.com/youtube/v3/getting-started)
and put it in a `youtube_api_key` file in the top-level `vods2` folder. Note
that there is no file extension on `youtube_api_key`.

You can add VODs from a YouTube channel to the database using the following
command:

```sh
python3 -m flask ingest-channel <channel_id> '<search_query>' '<video_title_format>'
```

where:

- `channel_id` is the YouTube channel ID. I get the ID using [this website](https://www.streamweasels.com/%20tools/youtube-channel-id-and-%20user-id-convertor/).
    - The channel IDs for the websites I pull from are stored in [`data/channel_ids.txt`](https://github.com/akbiggs/vods2/blob/main/data/channel_ids.txt).
- `search_query` is an optional query to reduce what videos get queried from the channel. For example if you are trying to get VODs that have the word "Blah" in the title, you can type `'"Blah"'`.
- `video_title_format` describes the format of the video title (where the event name, the player names, and the character names are).
    - `%P1`: Where the first player name goes.
    - `%P2`: Where the second player name goes.
    - `%C1`: Where the first player's character(s) goes.
    - `%C2`: Where the second player's character(s) goes.
    - `%E`: (optional) The event name.
    - `%R`: (optional) The round name.
    - `%V`: (optional) Some versus text, for example "vs", "VS", "vs.".
    - `%ROA`: (optional) Some reference to Rivals of Aether II, for example "RoA2", "Rivals of Aether II", "Rivals 2".

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

- `playlist_url` is the url of the playlist you wish to add.
- `event_name` is the name of the event or tournament name you wish to add.
- `video_title_format` describes the format of the video title (where the event name, the player names, and the character names are).
    - `%P1`: Where the first player name goes.
    - `%P2`: Where the second player name goes.
    - `%C1`: Where the first player's character(s) goes.
    - `%C2`: Where the second player's character(s) goes.
    - `%E`: (optional) The event name.
    - `%R`: (optional) The round name.
    - `%V`: (optional) Some versus text, for example "vs", "VS", "vs.".
    - `%ROA`: (optional) Some reference to Rivals of Aether II, for example "RoA2", "Rivals of Aether II", "Rivals 2".

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

After verifying the new VODs you can export them to either a CSV file or a Google Sheet, or both.

#### Exporting VODs to a CSV file

```sh
python3 -m flask export-csv
```

On the production site to get the new VODs, I pull the changes to
`data/vods.csv` and then run:

```sh
python3 -m flask ingest-csv
```

#### Exporting VODs to a Google Sheet

```sh
python3 -m flask export-sheet
```

On the production site to get the new Vods, I run:

```sh
python3 -m flask ingest-sheet
```

### Hosting

I use [PythonAnywhere](https://www.pythonanywhere.com) to host the site.
