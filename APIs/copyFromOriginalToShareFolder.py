from APIs.metadata import MetaDataList

import os
import shutil


class Copy_From_Original_To_Share:

    def __init__(self,
                 str_Experiment_ID: str = "",
                 str_Storage_Directory: str = "",
                 str_Share_Directory: str = ""):
        self.str_Experiment_ID = str_Experiment_ID
        self.str_Storage_Directory = str_Storage_Directory
        self.str_Share_Directory = str_Share_Directory

    def set_Experiment_ID(self, str_Experiment_ID):
        self.str_Experiment_ID = str_Experiment_ID

    def set_Storage_Directory(self, str_Storage_Directory):
        self.str_Storage_Directory = str_Storage_Directory

    def set_Share_Directory(self, str_Share_Directory):
        self.str_Share_Directory = str_Share_Directory

    def copy_Original_To_Share(self,
                               str_Experiment_ID="",
                               str_Share_Directory=""):
        # if str_Experiment_ID != "":
        #     self.str_Experiment_ID = str_Experiment_ID
        # if str_Share_Directory != "":
        #     self.str_Share_Directory = str_Share_Directory

        dictReturnMessage = {}
        metaDataList = MetaDataList()
        metaDataList.set_Str_Experiment_ID(self.str_Experiment_ID)
        metaDataList.set_Str_Data_Directory(self.str_Storage_Directory)
        list_File_Names = metaDataList.load_File_List_From_File()
        # list_File_Names = metaDataList.get_List_File_Name()
        if list_File_Names == []:
            dict_Experiment_Information = metaDataList.get_Experiment_Information(
            )
            dictReturnMessage["status"] = False
            dictReturnMessage["message"] = "Meta Data File is not found."
            returnArgs = {}
            returnArgs["list_file_name"] = []
            returnArgs["experiment_information"] = dict_Experiment_Information
        else:
            dict_Experiment_Information = metaDataList.get_Experiment_Information(
            )
            # metaDataList.load_All_Meta_From_File_List()
            for file_name in list_File_Names:
                data_directory = self.str_Storage_Directory + "{}/{}/data/".format(
                    self.str_Experiment_ID, self.str_Experiment_ID)
                file_directory = data_directory + file_name
                print(file_name)
                try:
                    if os.path.isdir(file_directory):
                        try:
                            os.makedirs(self.str_Share_Directory + file_name,
                                        exist_ok=True)
                        except FileExistsError:
                            pass
                    else:
                        only_file_name = os.path.basename(file_directory)
                        try:
                            os.makedirs(self.str_Share_Directory +
                            file_directory[len(data_directory):-1*len(only_file_name)],
                                        exist_ok=True)
                        except FileExistsError:
                            pass
                        shutil.copy(
                            file_directory, self.str_Share_Directory +
                            file_directory[len(data_directory):])

                except FileNotFoundError:
                    pass
            dictReturnMessage["status"] = True
            dictReturnMessage["message"] = "Success."
            returnArgs = {}
            returnArgs["list_file_name"] = list_File_Names
            returnArgs["experiment_information"] = dict_Experiment_Information
        dictReturnMessage["args"] = returnArgs
        return dictReturnMessage
