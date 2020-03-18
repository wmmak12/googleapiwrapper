# TL:DR
Simple wrapper for some of google api functions for python namely:
Google Shared Drive and Google Email

# How to use #

Example to use the googledrivewrapper.py

```python
from googleapiwrapper.googledrivewrapper import GoogleSharedDrive

# Load your service account credentials. Google to find out how to do it
SERVICE_ACCOUNT_FILE = './credentials.json'

# instantiate the Drive
shared_drives = GoogleSharedDrive(SERVICE_ACCOUNT_FILE)

# Find the ID for the folder name
folder_1_id = shared_drives.fetch_folder_id('<YOURPROJECTNAME>')

# Create a new folder in previous folder
newFolder = shared_drives.create_new_folder(folder_1_id, '<new folder>')
# Create another folder in new folder's folder
subfile = shared_drives.create_new_folder(newFolder['id'], 'new sub folder')

# Upload a new file in new folder, will output the file meta data
file_metadata = shared_drives.upload_file(newFolder['id'], './<file you need>', 'new_file.xlsx')
# Get the file ID
fileID = file_metadata.get('id')

# Search a file ID using file Name in a specific folder
# You will need to provide the folder ID for this function
input_folder_id = "<YOURFOLDERID>"
file_name = "test.xlsx"
fileID = shared_drives.search_fileID_in_folder_using_fileName(input_folder_id, file_name)

# Download file from GoogleDrive
input_file_id = '<YOURFOLDERID>'
shared_drives.download_file(input_file_id, './test.xlsx')
```


Example to use the googleemailwrapper.py

```python
from googleapiwrapper.googleemailwrapper import GoogleEmail

SERVICE_ACCOUNT_FILE = "./credentials.json"
EMAIL_FROM = "<YOUREMAILADDRESS>"
EMAIL_TO = "<OTHEREMAILADDRESS>"
EMAIL_SUBJECT = "Hello, Test"
EMAIL_CONTENT = "Testing. Thanks, it works"

# instantiate the Email
gmail = GoogleEmail(SERVICE_ACCOUNT_FILE, EMAIL_FROM)

# Create the email contents
message = gmail.create_message(EMAIL_TO, EMAIL_SUBJECT, EMAIL_CONTENT, ['test.csv'])

# Send email
sent = gmail.send_message()

```
