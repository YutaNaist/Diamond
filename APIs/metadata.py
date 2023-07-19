import json
# import os
# import shutil


class MetaData:
    def __init__(self):
        self.str_Original_Data_File_Name = ""
        self.str_Meta_Data_File_Name = ""
        self.dict_meta_Data = {}
        self.list_meta_Data_Key = []

    def set_Str_Data_Directory(self, str_Storage_Directory):
        self.str_Storage_Directory = str_Storage_Directory
    
    def set_Str_Usage_ID(self, str_Usage_ID):
        self.str_UsageID = str_Usage_ID

    def set_Dict_Meta_Data(self, dict_Meta_Data):
        self.dict_meta_Data = dict_Meta_Data
        self.list_meta_Data_Key = dict_Meta_Data.keys()

    def set_Str_Meta_Data_File_Name(self, str_Meta_Data_File_Name):
        self.str_Meta_Data_File_Name = str_Meta_Data_File_Name

    def load_Meta_Data_From_Json_File(self, str_File_Name_Json):
        # print(str_File_Name_Json)
        self.str_Meta_Data_Json_File_Name = str_File_Name_Json
        self.dict_meta_Data = json.load(
            open(self.str_Meta_Data_Json_File_Name, mode="r",
                 encoding="utf-8"))
        self.list_meta_Data_Key = self.dict_meta_Data.keys()

    def load_Meta_Data_From_Original_File_Name(self, str_Original_File_Name):
        self.str_Original_Data_File_Name = str_Original_File_Name
        self.str_Meta_Data_Json_File_Name = self.str_Storage_Directory + self.str_UsageID + "/metadata/" + str_Original_File_Name + ".json_meta"
        self.load_Meta_Data_From_Json_File(self.str_Meta_Data_Json_File_Name)

    def save_Meta_Data(self):
        json.dump(self.dict_meta_Data,
                  open(self.str_Storage_Directory + self.str_UsageID + "/" +
                       self.str_Meta_Data_File_Name + ".json_meta",
                       mode="w",
                       encoding='utf-8'),
                  ensure_ascii=False,
                  indent=4)

    def save_Meta_Data_From_Original(self,
                                     str_Original_File_Name,
                                     dict_Meta_Data={}):
        if dict_Meta_Data != {}:
            self.dict_meta_Data = dict_Meta_Data
            self.list_meta_Data_Key = dict_Meta_Data.keys()
        self.str_Original_Data_File_Name = str_Original_File_Name
        self.str_Meta_Data_File_Name = str_Original_File_Name + ".json_meta"
        self.save_Meta_Data()

    def get_Str_Meta_Data_File_Name(self):
        return self.str_Meta_Data_File_Name

    def get_Dict_Meta_Data(self):
        return self.dict_meta_Data

    def get_List_meta_Data_Key(self):
        return self.list_meta_Data_Key


class MetaDataList:
    def __init__(self):
        self.list_File_Name = []
        self.list_Meta_Data = []

    def set_List_File_Name(self, list_File_Name):
        self.list_File_Name = list_File_Name

    def set_Str_Data_Directory(self, str_Storage_Directory):
        self.str_Storage_Directory = str_Storage_Directory

    def set_Str_Usage_ID(self, str_Usage_ID):
        self.str_UsageID = str_Usage_ID

    def set_List_Dict_Meta_Data(self, list_Dict_Meta_Data):
        self.list_Meta_Data = []
        for i, file_Name in enumerate(self.list_File_Name):
            meta_Data = MetaData()
            meta_Data.set_Str_Data_Directory(self.str_Storage_Directory)
            meta_Data.set_Str_Usage_ID(self.str_UsageID)
            meta_Data.set_Str_Meta_Data_File_Name(file_Name)
            meta_Data.set_Dict_Meta_Data(list_Dict_Meta_Data[i])
            self.list_Meta_Data.append(meta_Data)

    def append_File_And_MetaData(self, str_File_Name, dict_Meta_Data):
        if not (str_File_Name in self.list_File_Name):
            self.list_File_Name.append(str_File_Name)
            meta_Data = MetaData()
            meta_Data.set_Str_Data_Directory(self.str_Storage_Directory)
            meta_Data.set_Str_Usage_ID(self.str_UsageID)
            meta_Data.set_Str_Meta_Data_File_Name(str_File_Name)
            meta_Data.set_Dict_Meta_Data(dict_Meta_Data)
            self.list_Meta_Data.append(meta_Data)
        else:
            index = self.list_File_Name.index(str_File_Name)
            meta_Data = MetaData()
            meta_Data.set_Str_Data_Directory(self.str_Storage_Directory)
            meta_Data.set_Str_Usage_ID(self.str_UsageID)
            meta_Data.set_Str_Meta_Data_File_Name(str_File_Name)
            meta_Data.set_Dict_Meta_Data(dict_Meta_Data)
            self.list_Meta_Data[index] = meta_Data

    def save_Meta_Datas(self, index):
        for meta in enumerate(self.list_Meta_Data):
            meta.save_Meta_Data()

    def save_List_File_Names(self):
        experiment_Directory = self.str_Storage_Directory + "{}/".format(
            self.str_UsageID)
        file_Name = experiment_Directory + "filenames.json"
        try:
            json.dump(open(file_Name, mode="w", encoding="utf-8"),
                      indent=4,
                      ensure_ascii=False)
        except FileExistsError:
            pass
        except FileNotFoundError:
            pass

    def load_File_List_From_File(self):
        experiment_Directory = self.str_Storage_Directory + "{}/".format(
            self.str_UsageID)
        file_Name = experiment_Directory + "filenames.json"
        try:
            self.list_File_Name = json.load(
                open(file_Name, mode="r", encoding="utf-8"))
        except FileExistsError:
            self.list_File_Name = []
        except FileNotFoundError:
            self.list_File_Name = []

    def load_All_Meta_From_File_List(self, list_File_Name=[]):
        if list_File_Name != []:
            self.list_File_Name = list_File_Name
        self.list_Meta_Data = []
        for fileName in self.list_File_Name:
            meta_Data = MetaData()
            meta_Data.set_Str_Data_Directory(self.str_Storage_Directory)
            meta_Data.set_Str_Usage_ID(self.str_UsageID)
            meta_Data.set_Str_Meta_Data_File_Name(fileName)
            meta_Data.load_Meta_Data_From_Original_File_Name(fileName)
            self.list_Meta_Data.append(meta_Data)

    def get_List_Dict_Meta_Data(self):
        list_Dict_Meta_Data = []
        self.load_All_Meta_From_File_List()
        for i, file in enumerate(self.list_File_Name):
            meta = self.list_Meta_Data[i]
            list_Dict_Meta_Data.append(meta.get_Dict_Meta_Data())
        return list_Dict_Meta_Data

    def get_List_File_Name(self):
        return self.list_File_Name

    def get_Meta_Data_From_Index(self, index):
        return self.list_Meta_Data[index].get_Dict_Meta_Data()
    
    def get_Experiment_Information(self):
        experiment_Directory = self.str_Storage_Directory + "{}/".format(
            self.str_UsageID)
        file_Name = experiment_Directory + "experiment_information.json"
        try:
            return json.load(open(file_Name, mode="r", encoding="utf-8"))
        except FileExistsError:
            return {}
        except FileNotFoundError:
            return {}

    # def get_Meta_Data_From_File_Name(file_Name):

    # meta = MetaData()
    # meta.get_Dict_Meta_Data()

    # def load_All_Meta_From_File_List(self):
    #     experiment_Directory = self.str_Storage_Directory + "{}/".format(
    #         self.str_UsageID)
    #     meta_Directory = experiment_Directory + "MetaData"
    #     self.list_Meta_Data = []
    #     for i, file in enumerate(self.list_File_Name):
    #         try:
    #             directory = meta_Directory
    #             fileSplit = file.split("/")
    #             if len(fileSplit) > 1:
    #                 for j in range(len(fileSplit) - 1):
    #                     directory = directory + "/" + fileSplit[j]
    #             json_File_Name = directory + "/" + fileSplit[-1] + ".json_meta"
    #             dict_Meta_Json = json.load(
    #                 open(json_File_Name, mode="r", encoding="utf-8"))
    #             self.list_Dict_Meta_Data.append(dict_Meta_Json)
    #         except FileExistsError:
    #             pass
