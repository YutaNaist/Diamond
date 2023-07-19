from APIs.metadata import MetaDataList


class GetMetaData:
    pass

    def set_UsageID(self, str_UsageID):
        self.str_UsageID = str_UsageID

    def set_Storage_Directory(self, str_Storage_Directory):
        self.str_Storage_Directory = str_Storage_Directory

    def getMetaData(self, str_UsageID=""):
        if str_UsageID != "":
            self.str_UsageID = str_UsageID
        dictReturnMessage = {}
        metaDataList = MetaDataList()
        metaDataList.set_Str_Usage_ID(self.str_UsageID)
        metaDataList.set_Str_Data_Directory(self.str_Storage_Directory)
        metaDataList.load_File_List_From_File()
        list_File_Names = metaDataList.get_List_File_Name()
        if list_File_Names == []:
            dict_Experiment_Information = metaDataList.get_Experiment_Information(
            )
            dictReturnMessage["status"] = False
            dictReturnMessage["message"] = "Meta Data File is not found."
            returnArgs = {}
            returnArgs["list_file_name"] = []
            returnArgs["dict_dict_meta_data"] = {}
            returnArgs["experiment_information"] = dict_Experiment_Information
        else:
            dict_Experiment_Information = metaDataList.get_Experiment_Information(
            )
            metaDataList.load_All_Meta_From_File_List()
            list_Dict_Meta_Data = metaDataList.get_List_Dict_Meta_Data()
            dictReturnMessage["status"] = True
            dictReturnMessage["message"] = "Success."
            returnArgs = {}
            returnArgs["list_file_name"] = list_File_Names
            returnArgs["dict_dict_meta_data"] = list_Dict_Meta_Data
            returnArgs["experiment_information"] = dict_Experiment_Information
        dictReturnMessage["args"] = returnArgs
        return dictReturnMessage
