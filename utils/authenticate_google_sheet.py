import click
import gspread

from google.oauth2.service_account import Credentials
from gspread.worksheet import Worksheet


def get_vods_sheet() -> Worksheet | None:

    click.echo('Authenticating with Google Sheets...')

    scope = ['https://www.googleapis.com/auth/spreadsheets']

    # These values should be replaced with your actual Google Sheet ID and worksheet name

    sheet_id = '1RRblTHe9hmlQDmOw05dglEXmnuH0fcB7f-ZqHjBOyT4'
    worksheet_name = 'vods'

    try:
        credentials = Credentials.from_service_account_file(
            'google_service_account.json',
            scopes=scope,
        )

        client = gspread.authorize(credentials)
        click.echo('Google Sheets authentication successful.')
        click.echo('Obtained sheet successfully.')
        return client.open_by_key(sheet_id).worksheet(worksheet_name)

    except Exception as e:
        click.echo(f'Google Sheets error: {e}')
        return None