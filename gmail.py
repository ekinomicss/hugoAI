import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from dateutil.parser import parse


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def getGmail():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "C:/Users/zorer/Downloads/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
      print("No messages found.")
      return

    print("Recent emails:")
    for message in messages:
      # Use the message ID to fetch the email details
      msg = service.users().messages().get(userId='me', id=message['id']).execute()

      # Extract subject and sender from the email headers
      headers = msg["payload"]["headers"]
      subject = next(header["value"] for header in headers if header["name"].lower() == "subject")
      sender = next(header["value"] for header in headers if header["name"].lower() == "from")
      dateRaw = next(header["value"] for header in headers if header["name"].lower() == "date")
      dateObj = parse(dateRaw)
      formatted_date = dateObj.strftime("%Y-%m-%d")

      if (formatted_date=="2024-03-17"):
        print(f"From: {sender}")
        print(f"Subject: {subject}\n")

  except HttpError as error:
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  getGmail()