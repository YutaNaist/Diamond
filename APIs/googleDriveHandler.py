from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import logging

import os


class GoogleDriveHandler:
    def __init__(self,
                 google_Auth=None,
                 setting_path: str = 'settings.yaml',
                 logger=None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        if google_Auth is None:
            self.gauth = GoogleAuth(setting_path)
            self.gauth.LocalWebserverAuth()
        else:
            self.gauth = google_Auth
        self.drive = GoogleDrive(self.gauth)

    def set_experiment_ID(self, str_experiment_ID):
        self.experiment_ID = str_experiment_ID

    def create_folder(self, folder_name):
        ret = self.check_files(folder_name)
        if ret:
            folder = ret
            print(f"{folder['title']}: exists")
        else:
            folder = self.drive.CreateFile({
                'title':
                folder_name,
                'mimeType':
                'application/vnd.google-apps.folder'
            })
            folder.Upload()
        return folder

    def create_folder_Force(self, folder_name, folder_id):
        if folder_id is None:
            folder = self.drive.CreateFile({
                'title':
                folder_name,
                'mimeType':
                'application/vnd.google-apps.folder',
            })
        else:
            folder = self.drive.CreateFile({
                'title': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                "parents": [
                    {
                        "id": folder_id
                    },
                ]
            })
        folder.Upload()
        return folder

    def check_files(
        self,
        folder_name,
    ):
        query = f'title = "{os.path.basename(folder_name)}"'
        list = self.drive.ListFile({'q': query}).GetList()
        if len(list) > 0:
            return list[0]
        return False

    def upload(
        self,
        local_file_path: str,
        save_folder_name: str = 'sample',
        is_convert: bool = True,
    ):

        if save_folder_name:
            folder = self.create_folder(save_folder_name)

        print(self.drive.ListFile({'parents': [{'id': folder["id"]}]}))

        file = self.drive.CreateFile({
            'title': os.path.basename(local_file_path),
            'parents': [{
                'id': folder["id"]
            }]
        })
        print(type(file))
        print(file)
        print()
        file.SetContentFile(local_file_path)
        print(type(file))
        print(file)
        print(dict(file))
        print()
        file.Upload({'convert': is_convert})
        file.Delete()

        drive_url = f"https://drive.google.com/uc?id={str( file['id'] )}"
        return drive_url

    def upload_Folder(self, upload_Path, upload_Dir_Name, folder_ID=None):
        # if self.gauth.credentials is None:
        #     self.gauth.LocalWebserverAuth()
        # elif self.gauth.access_token_expired:
        #     self.gauth.Refresh()
        # else:
        #     self.gauth.Authorize()
        path = upload_Path
        print(upload_Dir_Name)

        # if self.check_files(upload_Dir_Name):
        #     return
        folder = self.create_folder_Force(upload_Dir_Name, folder_ID)
        # if folder_ID is None:
        #     folder_id = folder["id"]
        # else:
        #     folder_id = folder_ID
        folder_id = folder["id"]

        for x in os.listdir(path):
            if os.path.isdir(path + "/" + x):
                self.upload_Folder(path + "/" + x, x, folder_ID=folder_id)
            else:
                f = self.drive.CreateFile({"parents": [
                    {
                        "id": folder_id
                    },
                ]})
                f['title'] = x
                # print(f)
                f.SetContentFile(os.path.join(path, x))
                # print(f)
                f.Upload()
                # print(f)

            f = None
