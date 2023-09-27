from APIs.proposal import Proposal
from APIs.googleDriveHandler import GoogleDriveHandler

import os
import glob
import shutil
import json

# import multiprocessing
# from multiprocessing import Process
import threading


class FinishExperiment:
    def __init__(
        self,
        experiment_ID="",
        share_Directory="",
        list_File_Names=[],
        dict_Environment_Variable={},
        google_Auth_For_Drive=None,
        logger=None,
    ):
        self.experiment_ID = experiment_ID
        self.jsonFileName = "../databaseUser.json"
        self.isAppendExisting = False
        self.metaData = {}
        self.str_Storage_Directory = "D:/Data/"
        self.str_Share_Directory = "C:/Share/"
        self.set_Proposal_Directory = self.str_Storage_Directory + "Proposals/"
        self.str_Experiment_Directory = (
            self.str_Storage_Directory + self.experiment_ID + "/"
        )
        self.is_Share_With_Google = False
        self.str_Share_Google_Address = ""
        self.str_parent_id_in_google_drive = ""
        self.logger = logger

        if share_Directory != "":
            self.str_Share_Directory = share_Directory

        self.list_File_Names = list_File_Names
        if dict_Environment_Variable != {}:
            self.jsonFileName = (
                dict_Environment_Variable["database_directory"]
                + dict_Environment_Variable["database_user_information_json_loading"]
            )
            self.str_API_Key_Drive = (
                dict_Environment_Variable["database_directory"]
                + dict_Environment_Variable["authorization_json_google_drive_api"]
            )
            self.str_Setting_Yaml = (
                dict_Environment_Variable["database_directory"]
                + dict_Environment_Variable["setting_yaml_google_drive_api"]
            )

            self.str_Storage_Directory = dict_Environment_Variable["storage_directory"]
            self.str_Experiment_Directory = (
                self.str_Storage_Directory + self.experiment_ID + "/"
            )
            self.set_Proposal_Directory = dict_Environment_Variable[
                "proposal_directory"
            ]
            # self.str_filename_All_IDs = dict_Environment_Variable["database_user_id_json_loading"]
        self.set_Google_Auth_For_Drive(google_Auth_For_Drive)

    def setDictMetaData(self, dictMetaData_):
        # self.metaData = dictMetaData_
        pass

    def setFilePathOfJsonDatabase(self, jsonFileName):
        self.jsonFileName = jsonFileName

    def setBaseDirectoryForStorage(self, str_Storage_Directory):
        self.str_Storage_Directory = str_Storage_Directory
        self.set_Proposal_Directory = self.str_Storage_Directory + "Proposals/"
        self.str_Experiment_Directory = (
            self.str_Storage_Directory + self.experiment_ID + "/"
        )
        if not os.path.exists(self.set_Proposal_Directory):
            os.mkdir(self.set_Proposal_Directory)

    def setBaseDirectoryForShare(self, str_Share_Directory):
        self.str_Share_Directory = str_Share_Directory

    def setIsAppendExisting(self, isAppendExisting):
        self.isAppendExisting = isAppendExisting

    def set_Google_Auth_For_Drive(self, google_Auth_For_Drive):
        self.google_Auth_For_Drive = google_Auth_For_Drive

    def setListFileNames(self, listFileNames):
        self.list_File_Names = listFileNames

    def set_API_Key_Google_Drive(
        self, str_Directory_API_Key_Drive, str_Directory_Setting_Yaml
    ):
        self.str_API_Key_Drive = str_Directory_API_Key_Drive
        self.str_Setting_Yaml = str_Directory_Setting_Yaml

    def setListDictMetaDatas(self, listDictMetaDatas):
        self.listDictMetaDatas = listDictMetaDatas

    def finishExperiment(self):
        # self.proposalList = ProposalList()
        # self.proposalList.readProposalListFromDataBaseJson(self.jsonFileName)
        # self.current_Proposal.saveSingleProposal(proposal_filename)

        dictReturnMsg = {}
        self.str_parent_id_in_google_drive = self.dict_Experiment_Information[
            "str_parent_id_in_google_drive"
        ]

        self._save_Experiment_information()
        # self._makeFilenamesLists()
        try:
            if self._moveExperimentResults():
                self._makeUserInfoJson()
                self._makeMetaDataJsons()

                # self._up_load_to_Google()
                if self.is_Share_With_Google is True:
                    thread_upload = threading.Thread(target=self._up_load_to_Google)
                    thread_upload.daemon = True
                    thread_upload.start()
                    # process_upload = Process(target=self._up_load_to_Google,
                    #                          args=())
                    # process_upload.start()

                dictReturnMsg["status"] = True
                dictReturnMsg["message"] = "Success"
            else:
                dictReturnMsg["status"] = False
                dictReturnMsg[
                    "message"
                ] = "The folder of ID: {} is already exists.".format(self.experiment_ID)
        except shutil.Error:
            pass
            filesInShareFolder = glob.glob(self.str_Share_Directory + "/*")
            dictReturnMsg["status"] = False
            dictReturnMsg[
                "message"
            ] = "The filename of ({}) has been already used. Please change filename!".format(
                filesInShareFolder[0]
            )
        except BaseException as exception:
            dictReturnMsg["status"] = False
            dictReturnMsg["message"] = "Error with {}".format(exception)
        self._save_Experiment_information()
        # filesInShareFolder = glob.glob(self.str_Share_Directory + "/*")
        # for folder in filesInShareFolder:
        #     print(folder)
        #     # os.remove(folder)
        return dictReturnMsg

    def _moveExperimentResults(self):
        if not os.path.exists(self.str_Experiment_Directory):
            os.mkdir(self.str_Experiment_Directory)
        self._moveExperimentResultsMain(
            self.str_Share_Directory, self.str_Experiment_Directory
        )
        return True
        """
        # if self.isAppendExisting:
        # else:
        #     if os.listdir(str_Experiment_Directory + "data/"):
        #         return False
        #     else:
        #         if not os.path.exists(str_Experiment_Directory):
        #             os.mkdir(str_Experiment_Directory)
        #         self._moveExperimentResultsMain(originalDirectory,
        #                                         str_Experiment_Directory)
        #         return True
        """

    def _moveExperimentResultsMain(self, str_Share_Directory, str_Experiment_Directory):
        dataDirectory = str_Experiment_Directory + self.experiment_ID + "/data/"
        if not os.path.exists(dataDirectory):
            os.mkdir(dataDirectory)
        # filesInShareFolder = glob.glob(originalDirectory + "*", recursive=True)
        for i, file in enumerate(self.list_File_Names):
            full_Path_Original = str_Share_Directory + file
            full_Path_Storage = dataDirectory + file
            if os.path.isdir(full_Path_Original):
                try:
                    os.makedirs(full_Path_Storage)
                except BaseException:
                    pass
        for i, file in enumerate(self.list_File_Names):
            full_Path_Original = str_Share_Directory + file
            full_Path_Storage = dataDirectory + file
            if os.path.isfile(full_Path_Original):
                shutil.move(full_Path_Original, full_Path_Storage)
        for i, file in enumerate(self.list_File_Names):
            full_Path_Original = str_Share_Directory + file
            if os.path.isdir(full_Path_Original):
                shutil.rmtree(full_Path_Original)
        """
        # for file in filesInShareFolder:
        #     file = file.replace("\\", "/")
        #     if os.path.isfile(file):
        #         fileName = file.split("/")[-1]
        #         shutil.move(file, dataDirectory + fileName)
        #     else:
        #         os.makedirs()
        #         pass
        # if os.path.isfile(file):
        #     shutil.copy2(file, movedDirectory)
        # else:
        #     shutil.copytree(file, movedDirectory + "/test")
        """

    def _makeUserInfoJson(self):
        self.current_Proposal = Proposal()
        proposal_filename = (
            self.str_Experiment_Directory + self.experiment_ID + ".json_prop"
        )

        self.current_Proposal.readProposalFromJson(proposal_filename)
        self.current_Proposal.setProposalInformationValue("is_finished", True)
        self.current_Proposal.setProposalInformationValue("is_used_now", False)
        dict_Current_Proposal = self.current_Proposal.getDictProposal()
        if dict_Current_Proposal["data_delivery"]["status"][0] == "1":
            self.is_Share_With_Google = True
            self.str_Share_Google_Address = dict_Current_Proposal["data_delivery"][
                "gmail_address"
            ]
        else:
            self.is_Share_With_Google = False
        self.current_Proposal.saveSingleProposal(
            self.str_Experiment_Directory + self.experiment_ID + ".json_prop"
        )
        # self.current_Proposal.saveSingleProposal(self.set_Proposal_Directory +
        #                                          self.experiment_ID +
        #                                          ".json_prop")
        """
        intIndexID = self.proposalList.searchID(self.experiment_ID)
        if intIndexID != -1:
            proposalCurrentProposal = self.proposalList.getProposal(intIndexID)
            dict_Current_Proposal = proposalCurrentProposal.getDictProposal()
            if "Upload to Google" in dict_Current_Proposal["data_delivery"][
                    "status"]:
                self.is_Share_With_Google = True
                self.str_Share_Google_Address = dict_Current_Proposal[
                    "data_delivery"]["gmail_address"]
            else:
                self.is_Share_With_Google = False

            proposalCurrentProposal.saveSingleProposal(
                self.str_Experiment_Directory + self.experiment_ID + ".json_prop")
            # if proposalCurrentProposal.getDictProposal()["data_delivery"]["status"] == "Google"
            # print(self.set_Proposal_Directory + self.experiment_ID + ".json_prop")
            proposalCurrentProposal.saveSingleProposal(self.set_Proposal_Directory +
                                                       self.experiment_ID +
                                                       ".json_prop")
        """

    def _makeMetaDataJsons(self):
        metaDirectory = (
            self.str_Experiment_Directory + self.experiment_ID + "/metadata/"
        )
        if not os.path.exists(metaDirectory):
            os.mkdir(metaDirectory)
        for i, file in enumerate(self.list_File_Names):
            directory = metaDirectory
            fileSplit = file.split("/")
            if len(fileSplit) > 1:
                for j in range(len(fileSplit) - 1):
                    directory = directory + "/" + fileSplit[j]
                    if not os.path.exists(directory):
                        os.mkdir(directory)
            jsonFileName = directory + "/" + fileSplit[-1] + ".json_meta"
            json.dump(
                self.listDictMetaDatas[i],
                open(jsonFileName, "w", encoding="utf-8"),
                indent=4,
                ensure_ascii=False,
            )

    def _makeFilenamesLists(self):
        json.dump(
            self.list_File_Names,
            open(
                self.str_Experiment_Directory + "filenames.json", "w", encoding="utf-8"
            ),
            indent=4,
            ensure_ascii=False,
        )

    def _save_Experiment_information(self):
        experiment_Information_File_Name = (
            self.str_Experiment_Directory + "experiment_information.json"
        )
        json.dump(
            self.dict_Experiment_Information,
            open(experiment_Information_File_Name, "w", encoding="utf-8"),
            indent=4,
            ensure_ascii=False,
        )

    def set_dict_Experiment_information(self, dict_Experiment_Information):
        self.dict_Experiment_Information = dict_Experiment_Information

    def _up_load_to_Google(self):
        if self.is_Share_With_Google is False:
            return True
        else:
            google_Drive_Handler = GoogleDriveHandler(
                google_Auth=self.google_Auth_For_Drive,
                setting_path=self.str_Setting_Yaml,
            )
            google_Drive_Handler.set_experiment_ID(self.experiment_ID)
            up_Load_Directory = self.str_Storage_Directory + "{}/{}".format(
                self.experiment_ID, self.experiment_ID
            )
            up_Load_Directory_Name = up_Load_Directory.split("/")[-1]
            if self.str_parent_id_in_google_drive != "":
                google_Drive_Handler.delete_folder(self.str_parent_id_in_google_drive)
            parent_id = google_Drive_Handler.upload_Folder(
                up_Load_Directory, up_Load_Directory_Name
            )
            return True
            # file_List = glob.glob(up_Load_Directory + "**", recursive=True)
            # for file in file_List:
            #     file = file.replace("\\", "/")
            #     # fileName = file.split("/")[-1]

            #     if os.path.isdir(file):
            #         print("directory")
            #     else:
            #         print("file")


if __name__ == "__main__":
    pass
