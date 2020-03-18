from apiclient import discovery
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.oauth2 import service_account
import googleapiclient.discovery
import tempfile
import io


class GoogleSharedDrive:
    def __init__(self, serviceAccountFile: str):
        self.serviceAccountFile = serviceAccountFile

        self.service, self.sharedDrives = self.__access_shared_drives(
            self.serviceAccountFile
        )

    def __access_shared_drives(self, serviceAccountFile):
        """
        Instantiate the Googledrive.

        Parameters:
            serviceAccountFile- str, the json credentail file of the service account

        Return: 
            1) service object, 2) list of the shared drives stored in root
        """
        # Set the variables
        SCOPES = [
            "https://www.googleapis.com/auth/drive",
        ]

        # Set the credentials with above variables
        credentials = service_account.Credentials.from_service_account_file(
            serviceAccountFile, scopes=SCOPES
        )

        # Start the service
        service = discovery.build("drive", "v3", credentials=credentials)

        # List all the shared drives
        sharedDrives = service.teamdrives().list().execute()

        return service, sharedDrives

    def fetch_folder_id(self, folderName):
        """
        This function only finds the root folders.

        Parameters:
            folderName- str, the folder name you want

        Return: 
            The folder ID that is stored in root 
        """
        list_field = self.sharedDrives["teamDrives"]
        for field in list_field:
            if field.get("name") == folderName:
                fieldID = field["id"]
                break
            else:
                fieldID = "Cant find folder"

        return fieldID

    def create_new_folder(self, parentFolder, folderName):
        """
        This function helps to create a new folder in the specific shared drive folder.

        Parameters:
            parentFolder- str, ID of the parent folder. This is required if not the service account
                        will create it in its own drive. 
            folderName- str, the folder name you want

        Return: 
            The new folder object you just created. 
        """
        folder_metadata = {
            "name": folderName,
            "mimeType": "application/vnd.google-apps.folder",
            # Google TeamDrive's specific folder
            "parents": [parentFolder],
        }

        newFolder = (
            self.service.files()
                .create(body=folder_metadata, supportsAllDrives=True)
                .execute()
        )

        return newFolder

    def create_new_file(self, folderID, fileName, content, mimeType):
        # ToDO: Work on this to make it more robust WIP
        file_metadata = {"name": fileName, "parents": [folderID]}

        with tempfile.NamedTemporaryFile(mode="w") as tf:
            tf.write(content)

            # https://developers.google.com/api-client-library/python/guide/media_upload
            media = MediaFileUpload(tf.name, mimetype=mimeType)

            # https://developers.google.com/drive/v3/web/manage-uploads
            cloudFile = (
                self.service.files()
                    .create(body=file_metadata, supportsAllDrives=True)
                    .execute()
            )

        return cloudFile

    def __check_upload_duplicates(self, folderID, outFileName):
        """
        This function will check for duplicates inthe folder for the particular ouput file name
        if so, it will append an index to the front of the file
        
        Parameters:
            folderID - str, the ID of the folder
            outFileName - str, the name of your uploaded file
        
        Return: 
            str, the id of the newly created file
        """
        # Fetch list of files in the specific folder
        filesList_in_folder = self.service.files().list(q=f"'{folderID}' in parents and trashed=false",
                                                        supportsAllDrives=True,  # this will deprecate after Jun 2020
                                                        includeItemsFromAllDrives=True).execute()
        # Grab all the file name 
        files_name = [file['name'] for file in filesList_in_folder['files']]
        i = 1
        outFileName_chk = outFileName
        while outFileName_chk in files_name:
            outFileName_chk = f'{i}_' + outFileName
            i += 1
            
        return outFileName_chk
    
    def upload_file(self, folderID, upFilePath, outFileName):
        """
        This function will upload a file from your desired directory to the 
        GoogleDrive. In addition, it will check if there is any duplicates of the same
        name. If so, it will add a count to it. 
        
        Parameters:
            folderID - str, the ID of the folder
            upFilePath - str, the path to your file
            outFileName - str, the name of your uploaded file
        
        Return: 
            str, the id of the newly created file
        """
        # Check to see if there is any duplicates of the same name
        outFileName_rev = self.__check_upload_duplicates(folderID, outFileName)
        # Upload file
        file_metadata = {"name": outFileName_rev, "parents": [folderID]}

        media = MediaFileUpload(upFilePath, mimetype="*/*", resumable=True)

        uploaded_file_metadata = (
            self.service.files()
                .create(body=file_metadata, media_body=media, supportsAllDrives=True)
                .execute()
        )

        return uploaded_file_metadata

    def read_file(self, file_id):
        filecontent = self.service.files().get_media(fileId=file_id).execute()
        return filecontent

    def delete_file(self, file_id):
        """Permanently delete a file, skipping the trash.

        Args:
          file_id: ID of the file to delete.
        """
        self.service.files().delete(fileId=file_id, supportsAllDrives=True).execute()

    def download_file(self, fileID, downFilePath):
        """
        This function will download a file from GoogleDrive using the file ID to your local
        directory.
        Parameters:
            fileID - str, the ID of the file
            downFilePath - str, the path to your file with the name of the file
        Return:
            None
        """
        request = self.service.files().get_media(fileId=fileID)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))
        with io.open(downFilePath, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())

    def search_fileID_in_folder_using_fileName(self, folderID, fileName):
        """
        This function will search for a file ID in a specific folder using the fileName
        Parameters:
            folderID - str, the ID of the folder
            fileName - str, the name of the file you want to need
        Return:
            str, the ID of the file you are searching for
        """
        filesList_in_folder = self.service.files().list(q=f"'{folderID}' in parents and trashed=false",
                                                        supportsAllDrives=True,  # this will deprecate after Jun 2020
                                                        includeItemsFromAllDrives=True).execute()

        for file in filesList_in_folder['files']:
            if file['name'] == fileName:
                file_id = file.get('id')
                break
            else:
                file_id = 'No such file in the directory'

        return file_id
