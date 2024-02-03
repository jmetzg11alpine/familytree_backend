import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import datetime
from models import Person
from database import SessionLocal
import csv
from dotenv import load_dotenv
import datetime
import subprocess
from urllib.parse import urlparse
load_dotenv()
EMAIL = os.getenv('EMAIL')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_URL = os.getenv('DATABASE_URL')
current_dir = os.path.dirname(os.path.abspath(__file__))
today = str(datetime.date.today())


def create_service():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = os.path.join(current_dir, 'data', 'see-my-family-db.json')
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    return service


def create_folder(service, name, parent_id=None):
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id] if parent_id else []
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    folder_id = file.get('id')

    user_permission = {'type': 'anyone', 'role': 'reader'}
    service.permissions().create(fileId=folder_id, body=user_permission, fields='id').execute()

    return folder_id


def share_folder_with_user(service, folder_id, user_email):
    user_permission = {'type': 'user', 'role': 'writer', 'emailAddress': user_email}
    service.permissions().create(fileId=folder_id, body=user_permission, fields='id').execute()


def get_data(csv_location):
    with SessionLocal() as db, open(csv_location, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'location', 'birth', 'parents', 'spouse', 'siblings', 'children', 'coor'])

        query = db.query(Person)
        for person in query:
            coor = str(person.lat) + ', ' + str(person.lng)
            writer.writerow([person.id, person.name, person.location, person.birth, person.parents, person.spouse, person.siblings, person.children, coor])


def upload_file(service, folder_id, file_path, file_name, mime_type):
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()


def upload_photos(service, photos_folder_id):
    relative_photos_dir = '../PHOTOS'
    photos_dir = os.path.abspath(os.path.join(current_dir, relative_photos_dir))
    for root, dirs, files in os.walk(photos_dir):
        subfolder_path = os.path.relpath(root, photos_dir)
        if subfolder_path == '.':
            continue
        current_folder_id = create_folder(service, subfolder_path, photos_folder_id)
        for file in files:
            if file.lower().endswith(('.png')):
                file_path = os.path.join(root, file)
                upload_file(service, current_folder_id, file_path, file, 'image/jpeg')


def upload_bios(service, bios_folder_id):
    relative_bios_dir = '../BIOS'
    bios_dir = os.path.abspath(os.path.join(current_dir, relative_bios_dir))
    for root, dirs, files in os.walk(bios_dir):
        for file in files:
            file_path = os.path.join(root, file)
            upload_file(service, bios_folder_id, file_path, file, 'text/plain')


def create_sql_dump(output_file, DATABASE_URL, DATABASE_PASSWORD):
    parsed_url = urlparse(DATABASE_URL)
    db_name = parsed_url.path[1:]
    user = parsed_url.username
    container_name = 'familytree_backend-db-1'
    command = (
        f"docker exec {container_name} "
        f"mysqldump -u{user} -p{DATABASE_PASSWORD} "
        f"--no-create-info --ignore-table={db_name}.user {db_name}"
    )
    print(command)
    try:
        with open(output_file, 'w') as file:
            subprocess.run(command, shell=True, check=True, stdout=file, stderr=subprocess.PIPE)
        print(f"mySQL backup created successfully at {output_file}")
    except Exception as e:
        print(e)


def get_folder_url(service, folder_id):
    folder = service.files().get(fileId=folder_id, fields='webViewLink').execute()
    return folder.get('webViewLink')


def save_url(folder_url):
    file_name = os.path.join(current_dir, 'data', 'data_url.txt')
    with open(file_name, 'w') as file:
        file.write(folder_url)


def main():
    service = create_service()
    today = datetime.date.today().strftime('%Y-%m-%d')
    parent_folder_id = create_folder(service, today)
    share_folder_with_user(service, parent_folder_id, EMAIL)

    csv_location = os.path.join(current_dir, 'data', 'data.csv')
    get_data(csv_location)
    upload_file(service, parent_folder_id, csv_location, 'data.csv', 'text/csv')

    photos_folder_id = create_folder(service, 'PHOTOS', parent_folder_id)
    upload_photos(service, photos_folder_id)

    bios_folder_id = create_folder(service, 'BIOS', parent_folder_id)
    upload_bios(service, bios_folder_id)

    sql_file = os.path.join(current_dir, 'data', f'{today}_dump.sql')
    create_sql_dump(sql_file, DATABASE_URL, DATABASE_PASSWORD)
    upload_file(service, parent_folder_id, sql_file, f'{today}_dump.sql', 'application/x-sql')

    folder_url = get_folder_url(service, parent_folder_id)
    save_url(folder_url)


def show_service_acount_info():
    SERVICE_ACCOUNT_FILE = os.path.join(current_dir, 'data', 'see-my-family-db.json')
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    about_info = service.about().get(fields='storageQuota, user').execute()
    storage_quota = about_info.get('storageQuota', {})
    user_info = about_info.get('user', {})
    print('-----------General Info-----------')
    print(f"Drive User: {user_info.get('emailAddress')}")
    print(f"Total Storage: {int(storage_quota.get('limit', 0)) / (1024*1024*1024):.2f} GB")
    print(f"Used Storage: {int(storage_quota.get('usage', 0)) / (1024*1024*1024):.2f} GB")
    print(f"Available Storage: {(int(storage_quota.get('limit', 0)) - int(storage_quota.get('usage', 0))) / (1024*1024*1024):.2f} GB\n")


def list_files():
    SERVICE_ACCOUNT_FILE = os.path.join(current_dir, 'data', 'see-my-family-db.json')
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    page_token = None
    counter = 0
    while True:
        print(f'----------{counter}------')
        results = service.files().list(
            pageSize=10,
            fields="nextPageToken, files(id, name, createdTime)",
            pageToken=page_token
        ).execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
            break
        else:
            print('Files:')
            for item in items:
                print(f"{item['name']} ({item['id']}) {item['createdTime']}")
        page_token = results.get('nextPageToken', None)
        counter += 1
        if page_token is None:
            break


def delete_all_files(before_date):
    '''before_date = '2024-02-02' '''
    SERVICE_ACCOUNT_FILE = os.path.join(current_dir, 'data', 'see-my-family-db.json')
    SCOPES = ['https://www.googleapis.com/auth/drive']
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    query = f"createdTime <= '{before_date}T23:59:59'"
    results = service.files().list(q=query, fields="files(id, name, createdTime)").execute()
    items = results.get('files', [])
    if not items:
        print("No files found to delete.")
        return
    for item in items:
        try:
            service.files().delete(fileId=item['id']).execute()
            print(f"Deleted: {item['name']} ({item['id']}) - Created: {item['createdTime']}")
        except Exception as e:
            print(f"An error occurred: {e}")


def list_and_clear():
    # list_files()
    # delete_all_files('2024-02-02')
    list_files()
    show_service_acount_info()


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'DELETE':
        list_and_clear()
    else:
        main()
