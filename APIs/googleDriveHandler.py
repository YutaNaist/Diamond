from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import logging

import os
import json


class GoogleDriveHandler:
    def __init__(
        self, google_Auth=None, setting_path: str = "settings.yaml", logger=None
    ):
        self.parent_folder_id = ""
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

    def set_parent_folder_id(self, str_parent_folder_id):
        self.parent_folder_id = str_parent_folder_id

    def create_folder(self, folder_name):
        ret = self.check_files(folder_name)
        if ret:
            folder = ret
            print(f"{folder['title']}: exists")
        else:
            folder = self.drive.CreateFile(
                {"title": folder_name, "mimeType": "application/vnd.google-apps.folder"}
            )
            folder.Upload()
        return folder

    def create_folder_Force(self, folder_name, folder_id):
        if folder_id is None:
            folder = self.drive.CreateFile(
                {
                    "title": folder_name,
                    "mimeType": "application/vnd.google-apps.folder",
                }
            )
        else:
            folder = self.drive.CreateFile(
                {
                    "title": folder_name,
                    "mimeType": "application/vnd.google-apps.folder",
                    "parents": [
                        {"id": folder_id},
                    ],
                }
            )
        folder.Upload()
        return folder

    def check_files(
        self,
        folder_name,
    ):
        query = f'title = "{os.path.basename(folder_name)}"'
        list = self.drive.ListFile({"q": query}).GetList()
        if len(list) > 0:
            return list[0]
        return False

    def upload(
        self,
        local_file_path: str,
        save_folder_name: str = "sample",
        is_convert: bool = True,
    ):
        if save_folder_name:
            folder = self.create_folder(save_folder_name)

        file = self.drive.CreateFile(
            {
                "title": os.path.basename(local_file_path),
                "parents": [{"id": folder["id"]}],
            }
        )
        file.SetContentFile(local_file_path)
        file.Upload({"convert": is_convert})
        file.Delete()

        drive_url = f"https://drive.google.com/uc?id={str( file['id'] )}"
        return drive_url

    def upload_Folder(self, upload_Path, upload_Dir_Name, folder_ID=None):
        path = upload_Path

        folder = self.create_folder_Force(upload_Dir_Name, folder_ID)

        folder_id = folder["id"]

        for x in os.listdir(path):
            if os.path.isdir(path + "/" + x):
                self.upload_Folder(path + "/" + x, x, folder_ID=folder_id)
            else:
                f = self.drive.CreateFile(
                    {
                        "parents": [
                            {"id": folder_id},
                        ]
                    }
                )
                f["title"] = x
                f.SetContentFile(os.path.join(path, x))
                f.Upload()

            f = None
        return folder_id

    def delete_folder(self, parent_id):
        file = self.drive.CreateFile({"id": parent_id})
        file.Delete()

    def get_file(self, id):
        # file = self.drive.CreateFile({"id": id})
        # file = self.drive.ListFile({"q": f"appProperties has \{ key = 'id' and value = '{id}' \} "}).GetList()
        # file = self.drive.ListFile({"q": f"'id' = '{id}'"}).GetList()
        # file = self.drive.ListFile({"q": f"title = 'Test001'"}).GetList()
        files = self.drive.ListFile(
            {"q": f"'1V3NRaZKANmpythm5AG8DBAvbaWDsNIj3' in parents"}
        ).GetList()
        # print(file[0].GetPermissions())
        print(len(files))
        for f in files:
            if id == f.get("id"):
                print(f)
                print()

    def get_permission(self, file_id):
        file = self.drive.CreateFile({"id": file_id})
        # file.cre
        print(file.GetPermissions())

    def share_file(self, folder_id, user_gmail):
        files = self.drive.ListFile(
            {"q": f"'1V3NRaZKANmpythm5AG8DBAvbaWDsNIj3' in parents"}
        ).GetList()
        # print(file[0].GetPermissions())
        print(len(files))
        for file in files:
            if folder_id == file.get("id"):
                print(file.GetPermissions())
                print()
                file.InsertPermission(
                    new_permission={
                        "type": "user",
                        "value": user_gmail,
                        "role": "writer",
                    }
                )
                print(file.GetPermissions())


if __name__ == "__main__":
    dict_Environment_Variable = json.load(open("environment_variable.json", "r"))
    Google_Auth_For_Drive = GoogleAuth(
        dict_Environment_Variable["database_directory"]
        + dict_Environment_Variable["setting_yaml_google_drive_api"]
    )
    Google_Auth_For_Drive.LocalWebserverAuth()
    Google_Auth_For_Drive.CommandLineAuth()
    str_Setting_Yaml = (
        dict_Environment_Variable["database_directory"]
        + dict_Environment_Variable["setting_yaml_google_drive_api"]
    )

    gdh = GoogleDriveHandler(Google_Auth_For_Drive, str_Setting_Yaml)
    gdh.set_experiment_ID("0000-0000-0001")
    up_load_path = "C:/Users/yutay/OneDrive/デスクトップ/Test/TestGoogle/test"
    # gdh.get_file("1AJ5EzZzvsu4phMcpvwWDigKenfZAkKE1")
    # gdh.get_permission("1AJ5EzZzvsu4phMcpvwWDigKenfZAkKE1")
    gdh.share_file("1AJ5EzZzvsu4phMcpvwWDigKenfZAkKE1", "yuta.yamamoto@g.ext.naist.jp")

    # id = gdh.upload_Folder(
    #     up_load_path, "Test001", folder_ID="1V3NRaZKANmpythm5AG8DBAvbaWDsNIj3"
    # )
    # print(id)
    # try:
    #     gdh.delete_folder("1BNysDBuRNuHaAsSwzOhOeREv9isFzlZL")
    # except BaseException:
    #     pass
