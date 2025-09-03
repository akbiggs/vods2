- Switch from CSV to Google Sheets to enable people to contribute.
- Automate ingestion of data/regular_queries.txt.
  - Need compliance to get more YouTube API quota for this, as currently we do not have
    enough daily quota to run all the queries (we will get an API exception).
    To get compliance, need to fill out compliance form, see https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits
  - Once we have compliance, we can for example have a daily cronjob for something like:
     
     ```sh
     git pull origin main && \
       flask ingest-csv data/vods.csv && \
       flask run-regular-queries && \  # <this is what needs to be done>
       flask export-vods data/vods.csv && \
       git add . && git commit -m "Automatic regular queries" && git push origin main
     ```

- Add the following channels:
  - https://www.youtube.com/@gamequestpg/streams
  - https://youtube.com/@RivalsofAetherEurope/videos
  - ~~https://www.youtube.com/@rivalsofasia7265/videos~~ **DONE**
  - https://www.youtube.com/@LADAETHER
  - https://www.youtube.com/@SuperiorCalRivals2/videos hasn't been parsed correctly apparently?
  - https://www.youtube.com/@broscalamity/videos
  - https://www.youtube.com/@thedunkdojogaming/videos
  - https://www.youtube.com/@dgttx512/videos
  - ~~https://www.youtube.com/@PGHRivals/videos~~ **DONE**
  - Most of these are from https://docs.google.com/spreadsheets/d/1C3rJHZWzKMurMJmjACMEB1JZziPyNMrj57b5fE-4t9A/edit?gid=0#gid=0
- Work on vod-splitter for faster ingestion of large untagged vods https://github.com/Ludini1/vod-splitter
- Backfill large untagged vods (for example Hop On has a lot of good high-level content, Hop On #24 - #1 need to be ingested)
- Finish up non-home pages
- Maybe a Google Form for people to suggest YouTube channels to be added, to reduce DMs? I don't feel strongly, I'm fine
  with the current setup.
