# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "google-api-python-client",
#     "google-auth-httplib2",
#     "google-auth-oauthlib",
# ]
# ///


import json
import os

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_to_drive():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    creds_info = json.loads(creds_json)

    creds = Credentials.from_service_account_info(
        creds_info, scopes=["https://www.googleapis.com/auth/drive.file"]
    )

    service = build("drive", "v3", credentials=creds)

    folder_id = os.environ.get("GOOGLE_FOLDER_ID")
    basename = os.environ.get("BASENAME", "resume")

    # Upload timestamped version
    timestamp_file = [
        f
        for f in os.listdir(".")
        if f.startswith(f"{basename}") and f.endswith(".pdf") and "latest" not in f
    ][0]

    file_metadata = {
        "name": timestamp_file,
        "parents": [folder_id] if folder_id else [],
    }

    media = MediaFileUpload(timestamp_file, mimetype="application/pdf")

    file = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )

    print(f"Timestamped file uploaded with ID: {file.get('id')}")

    latest_filename = f"{basename}_latest.pdf"
    query = f"name='{latest_filename}'"
    if folder_id:
        query += f" and '{folder_id}' in parents"

    results = service.files().list(q=query).execute()
    items = results.get("files", [])

    if items:
        # Update existing file
        file_id = items[0]["id"]
        media = MediaFileUpload(latest_filename, mimetype="application/pdf")

        updated_file = (
            service.files().update(fileId=file_id, media_body=media).execute()
        )

        print(f"Latest {basename} updated with ID: {updated_file.get('id')}")
    else:
        # Create new latest file
        file_metadata = {
            "name": latest_filename,
            "parents": [folder_id] if folder_id else [],
        }

        media = MediaFileUpload(latest_filename, mimetype="application/pdf")

        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        print(f"Latest {basename} uploaded with ID: {file.get('id')}")


if __name__ == "__main__":
    upload_to_drive()
