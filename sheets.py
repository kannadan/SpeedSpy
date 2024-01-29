import gspread
from google.oauth2.service_account import Credentials
import db
# Define the scope
scope = ['https://www.googleapis.com/auth/spreadsheets']

# Add your service account file
creds = Credentials.from_service_account_file('credentials.json', scopes=scope)

# Authorize the clientsheet 

def write_to_sheet(list_of_values):
    client = gspread.authorize(creds)
    # Get the instance of the Spreadsheet
    sheet = client.open_by_key('1NbDjCfU674umROOy3OqA_ubMJ9npm4zEsTU2-bx2Az8')

    # Get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    # Add the values to the selected Google Sheet
    sheet_instance.append_row(list_of_values)

if __name__ == "__main__":
    
    runs = db.getAllruns()
    write_to_sheet(runs[-1])
    print(runs[-1])