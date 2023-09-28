# %%
import re
import json
import pandas
import datetime
import logging

# import time
# import random

try:
    from APIs.googleSpreadSheetHandler import GoogleSpreadSheetHandler
except ModuleNotFoundError:
    from googleSpreadSheetHandler import GoogleSpreadSheetHandler


class ErrorProposal(Exception):
    pass


class Proposal:
    def __init__(self, logger=None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self._listKeys = [
            "id",
            "index",
            "creators",
            "contact",
            "instrument",
            "experiment_date",
            "data_delivery",
            "arim_upload",
            "updated_at",
            "enable_status",
            "is_used_now",
            "is_finished",
            "url_for_edit",
        ]
        self._dictProposal = {}
        pass

    def addProposalInformationFromDictionary(self, dictJsonDatabase_):
        for key in self._listKeys:
            try:
                self._dictProposal[key] = dictJsonDatabase_[key]
            except KeyError:
                raise ErrorProposal(
                    "ErrorProposal: The key of {} is missing".format(key)
                )

    def getID(self):
        return self._dictProposal["id"]

    def setProposalInformationValue(self, key, value):
        self._dictProposal[key] = value

    def getProposalInformationValue(self, key):
        return self._dictProposal[key]

    def getIsUsed(self):
        return self._dictProposal["is_used_now"]

    def getIsEnable(self):
        return self._dictProposal["enable_status"]

    def getDictProposal(self):
        return self._dictProposal

    def getlistKeys(self):
        return self._listKeys

    def setNewItemToProposal(self, key, value):
        if not (key in self._listKeys):
            self._listKeys.append(key)
        self._dictProposal[key] = value

    def readProposalFromJson(self, filename_):
        with open(filename_, mode="r", encoding="utf-8") as f:
            self._dictProposal = json.load(f)
            self._listKeys = list(self._dictProposal.keys())

    def saveSingleProposal(self, filename_):
        # with open(filename_, mode="w", encoding="utf-8") as f:
        if (
            self._dictProposal["enable_status"] == "Enable"
            and self._dictProposal["id"] != "0000-000-000001"
        ):
            with open(filename_, mode="w", encoding="utf-8") as f:
                json.dump(self._dictProposal, f, ensure_ascii=False, indent=4)

    def updateTimeToCurrentTime(self):
        currentTime = datetime.datetime.now()
        currentTimeText = "{:04}/{:02}/{:02} {:02}:{:02}".format(
            currentTime.year,
            currentTime.month,
            currentTime.day,
            currentTime.hour,
            currentTime.minute,
        )
        self._dictProposal["updated_at"] = currentTimeText


class ProposalList:
    def __init__(
        self, str_Authorize_Json="", google_Spread_Sheet_Handler=None, logger=None
    ):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        self.str_Filename_Proposal_List = ""
        self._proposals = []
        self._listIDs = []
        self._numberOfProposals = 0
        self._list_generate_ID = [1, 0]
        self.int_Last_Colum_SpreadSheet = 21
        self.default_Experiment_ID = "0000-0000-00001"

        if str_Authorize_Json == "":
            self.str_Authorize_Json = (
                "C:/share/diamond/testproject-spreadsheet-385502-7ac002cbfaa5.json"
            )
        else:
            self.str_Authorize_Json = str_Authorize_Json
        if google_Spread_Sheet_Handler is None:
            self.google_Spread_Sheet_Handler = GoogleSpreadSheetHandler(
                self.str_Authorize_Json, logger=self.logger
            )
        else:
            self.google_Spread_Sheet_Handler = google_Spread_Sheet_Handler
        self.listIDsSpreadSheet = []

    def search_ID(self, strID_):
        if strID_ in self._listIDs:
            return self._listIDs.index(strID_)
        else:
            return -1

    def update_Proposal_From_Single_Proposal(self, proposal_To_Add):
        strID = proposal_To_Add.getID()
        index = self.search_ID(strID)
        if index == -1:
            self._proposals.append(proposal_To_Add)
            self._numberOfProposals += 1
            self._listIDs.append(strID)
        else:
            self._proposals[index] = proposal_To_Add
        return strID

    def update_Proposal_By_Dict(self, dict_Proposal):
        proposalToAdd = Proposal()
        try:
            aID = dict_Proposal["id"]
        except ErrorProposal:
            raise ErrorProposal("ErrorProposal: The key is missing")
        proposalToAdd.addProposalInformationFromDictionary(dict_Proposal)
        self.update_Proposal_From_Single_Proposal(proposalToAdd)
        return aID

    def read_Proposal_List_From_Database_Json(self, str_Filename_Json):
        self.str_Filename_Proposal_List = str_Filename_Json
        listDictJson = json.load(open(str_Filename_Json, mode="r", encoding="utf-8"))
        for dictJson in listDictJson:
            self.update_Proposal_By_Dict(dictJson)

    def get_Proposal(self, index_):
        return self._proposals[index_]

    def get_List_All_Proposals(self):
        return self._proposals

    def delete_Proposal(self, index_):
        del self._proposals[index_]
        del self._listIDs[index_]
        self._numberOfProposals -= 1

    def delete_Proposals_Checking_Enable_Status(self):
        for i in range(self._numberOfProposals - 1, -1, -1):
            dict_Proposal = self._proposals[i].getDictProposal()
            if (
                dict_Proposal["enable_status"] == "Disable"
                or dict_Proposal["id"] == self.default_Experiment_ID
            ):
                self.delete_Proposal(i)

    def load_From_SpreadSheet_Input(
        self,
        str_url_spreadsheet_input="",
        dict_Instrument_ID={},
        is_flag_second_read=False,
    ):
        bool_Flag_Updated = False
        self.logger.debug("Start Load From Spread Sheet")
        all_Value_Spread_Sheet = (
            self.google_Spread_Sheet_Handler.load_All_Value_From_Input_Sheet(
                str_url_spreadsheet_input, is_force_read=is_flag_second_read
            )
        )
        if all_Value_Spread_Sheet != []:
            if is_flag_second_read is False:
                bool_Flag_Updated = True
            else:
                bool_Flag_Updated = False
            (
                list_Dict_Spread_Sheet,
                list_ID_SpreadSheet,
            ) = self.translate_SpreadSheet_To_Dict(
                all_Value_Spread_Sheet, dict_Instrument_ID
            )
            for k, dict_Spread_Sheet in enumerate(list_Dict_Spread_Sheet):
                # str_ID = list_ID_SpreadSheet[i]
                self.update_Proposal_By_Dict(dict_Spread_Sheet)
            self.delete_Proposals_Checking_Enable_Status()
        return bool_Flag_Updated

    def translate_SpreadSheet_To_Dict(self, list_SpreadSheet, dict_instrument_id={}):
        # keys = list_SpreadSheet[0]
        listDictProposals = []
        list_ID = []
        for i in range(1, len(list_SpreadSheet)):
            try:
                s_format = "%Y/%m/%d %H:%M:%S"
                newest_date = datetime.datetime.strptime(
                    list_SpreadSheet[i][0], s_format
                )
            except ValueError:
                continue
            # if (list_SpreadSheet[i][0]) == "":
            dictProposal = {}
            # dictProposal["index"] = dictExcelFile["Index"]
            dictProposal["index"] = 0

            dictProposal["creators"] = []

            dictParson = {}
            dictParson["name"] = list_SpreadSheet[i][2]
            dictParson["email"] = list_SpreadSheet[i][3]
            dictParson["affiliation"] = list_SpreadSheet[i][4]
            dictProposal["creators"].append(dictParson)

            dictContact = {}

            dictContact["email"] = list_SpreadSheet[i][2]
            dictContact["phone_number"] = list_SpreadSheet[i][5]
            dictContact["address"] = list_SpreadSheet[i][6]
            dictProposal["contact"] = dictContact

            dictInstrument = {}
            dictInstrument["name"] = list_SpreadSheet[i][7]
            try:
                dictInstrument["identifier"] = dict_instrument_id[
                    list_SpreadSheet[i][7]
                ]
            except KeyError:
                dictInstrument["identifier"] = "NR-000"
            dictProposal["instrument"] = dictInstrument

            dictExperimentDate = {}

            dictExperimentDate["start_date"] = list_SpreadSheet[i][8].split(" ")[0]
            dictExperimentDate["start_time"] = list_SpreadSheet[i][8].split(" ")[-1]
            dictExperimentDate["end_date"] = list_SpreadSheet[i][9].split(" ")[0]
            dictExperimentDate["end_time"] = list_SpreadSheet[i][9].split(" ")[-1]
            dictProposal["experiment_date"] = dictExperimentDate

            dictDataDelivery = {}
            dictDataDelivery["status"] = list_SpreadSheet[i][12]
            dictDataDelivery["gmail_address"] = list_SpreadSheet[i][13]
            if list_SpreadSheet[i][12][0] == "1":
                dictDataDelivery["is_share_with_google"] = True
            else:
                dictDataDelivery["is_share_with_google"] = False
            dictProposal["data_delivery"] = dictDataDelivery

            dictARIMUpload = {}
            dictARIMUpload["status"] = list_SpreadSheet[i][10]
            dictARIMUpload["id"] = list_SpreadSheet[i][11]
            dictARIMUpload["uploaded"] = False
            dictProposal["arim_upload"] = dictARIMUpload

            dictProposal["created_at"] = list_SpreadSheet[i][8]
            dictProposal["updated_at"] = list_SpreadSheet[i][8]

            dictProposal["enable_status"] = list_SpreadSheet[i][18]
            dictProposal["is_used_now"] = False
            dictProposal["is_finished"] = False
            dictProposal["url_for_edit"] = list_SpreadSheet[i][16]

            created_ID = list_SpreadSheet[i][17]
            if created_ID == "" or created_ID == self.default_Experiment_ID:
                created_ID = self.default_Experiment_ID
            dictProposal["id"] = created_ID
            list_ID.append(dictProposal["id"])
            listDictProposals.append(dictProposal)
        return listDictProposals, list_ID

    def load_From_SpreadSheet_List(
        self, list_generate_ID=[1, 0], dict_Instrument_ID={}
    ):
        list_ID_SpreadSheet_Input = (
            self.google_Spread_Sheet_Handler.get_list_ID_Spread_Sheet_Input()
        )
        bool_Flag_Updated = False
        int_Len_ID_SpreadSheet = len(list_ID_SpreadSheet_Input)
        for i, ID_Spread_Sheet in enumerate(list_ID_SpreadSheet_Input):
            self.logger.debug(
                "Progress Load Spread Sheet: {}/{}".format(i, int_Len_ID_SpreadSheet)
            )
            all_Value_Spread_Sheet = (
                self.google_Spread_Sheet_Handler.load_All_Value_From_Spread_Sheet_Input(
                    i
                )
            )
            if all_Value_Spread_Sheet != []:
                bool_Flag_Updated = True
                # all_Value_Spread_Sheet = self.google_Spread_Sheet_Handler.load_All_Value_From_Spread_Sheet(
                #     str_ID_Spread_Sheet_, self.str_Authorize_Json)
                df_Spreadsheet = pandas.DataFrame(
                    all_Value_Spread_Sheet[1:], columns=all_Value_Spread_Sheet[0]
                )
                (
                    list_Dict_Spread_Sheet,
                    list_ID_SpreadSheet,
                ) = self.translate_DataFrame_To_Dict(
                    df_Spreadsheet,
                    list_generate_ID=list_generate_ID,
                    dict_Instrument_ID=dict_Instrument_ID,
                )
                for k, dict_Spread_Sheet in enumerate(list_Dict_Spread_Sheet):
                    # str_ID = list_ID_SpreadSheet[i]
                    self.update_Proposal_By_Dict(dict_Spread_Sheet)

                self.google_Spread_Sheet_Handler.overwrite_ID_Value_To_Spread_Sheet(
                    i, list_ID_SpreadSheet, self.int_Last_Colum_SpreadSheet
                )
                self.delete_Proposals_Checking_Enable_Status()
        return bool_Flag_Updated

    def load_From_SpreadSheet(
        self,
        str_ID_Spread_Sheet_="",
        int_Index_Sheet=0,
        list_generate_ID=[1, 0],
        dict_Instrument_ID={},
        google_Spread_Sheet_Handler=None,
    ):
        if google_Spread_Sheet_Handler is None:
            google_Spread_Sheet_Handler = GoogleSpreadSheetHandler("")
        try:
            all_Value_Spread_Sheet = (
                google_Spread_Sheet_Handler.load_All_Value_From_Spread_Sheet(
                    str_ID_Spread_Sheet_, self.str_Authorize_Json
                )
            )
            dfSpreadsheet = pandas.DataFrame(
                all_Value_Spread_Sheet[1:], columns=all_Value_Spread_Sheet[0]
            )
        except PermissionError:
            return False
        listDictSpreadSheet, list_ID_SpreadSheet = self.translate_DataFrame_To_Dict(
            dfSpreadsheet,
            int_Index_Sheet,
            list_generate_ID=list_generate_ID,
            dict_Instrument_ID=dict_Instrument_ID,
        )
        try:
            self.google_Spread_Sheet_Handler.overwrite_ID_Value_To_Spread_Sheet(
                str_ID_Spread_Sheet_,
                list_ID_SpreadSheet,
                self.int_Last_Colum_SpreadSheet,
            )
        except PermissionError:
            return False
        for dictSpreadsheet in listDictSpreadSheet:
            self.update_Proposal_By_Dict(dictSpreadsheet)
        self.delete_Proposals_Checking_Enable_Status()
        return True

    def translate_DataFrame_To_Dict(
        self, df_Spread_Sheet, list_generate_ID=[3215, 0], dict_Instrument_ID={}
    ):
        listDictProposals = []
        list_ID = []
        for i in range(df_Spread_Sheet.shape[0]):
            dict_Spread_Sheet = df_Spread_Sheet.iloc[i].fillna("").to_dict()
            if (dict_Spread_Sheet["User Name"]) == "":
                continue
            dictProposal = {}
            # dictProposal["index"] = dictExcelFile["Index"]
            dictProposal["index"] = list_generate_ID[0] * list_generate_ID[1]

            dictProposal["creators"] = []

            dictParson = {}
            dictParson["name"] = dict_Spread_Sheet["User Name"]
            dictParson["email"] = dict_Spread_Sheet["Email Address"]
            dictParson["affiliation"] = dict_Spread_Sheet["Affiliation"]
            dictProposal["creators"].append(dictParson)

            dictContact = {}

            dictContact["email"] = dict_Spread_Sheet["Email Address"]
            dictContact["phone_number"] = dict_Spread_Sheet["Phone Number"]
            dictContact["address"] = dict_Spread_Sheet["Address"]
            dictProposal["contact"] = dictContact

            dictInstrument = {}
            dictInstrument["name"] = dict_Spread_Sheet["Instrument"]
            try:
                dictInstrument["identifier"] = dict_Instrument_ID[
                    dict_Spread_Sheet["Instrument"]
                ]
            except KeyError:
                dictInstrument["identifier"] = "NR-000"
            dictProposal["instrument"] = dictInstrument

            dictExperimentDate = {}
            str_Start_Date = "{}/{}/{}".format(
                dict_Spread_Sheet["Start Year"],
                dict_Spread_Sheet["Start Month"],
                dict_Spread_Sheet["Start Day"],
            )
            str_Start_Time = "{}:{:02}:{:02}".format(
                dict_Spread_Sheet["Start Hour"], dict_Spread_Sheet["Start Minute"], 0
            )
            str_End_Date = "{}/{}/{}".format(
                dict_Spread_Sheet["Start Year"],
                dict_Spread_Sheet["End Month"],
                dict_Spread_Sheet["End Day"],
            )
            str_End_Time = "{}:{:02}:{:02}".format(
                dict_Spread_Sheet["End Hour"], dict_Spread_Sheet["End Minute"], 0
            )

            dictExperimentDate["start_date"] = str_Start_Date
            dictExperimentDate["start_time"] = str_Start_Time
            dictExperimentDate["end_date"] = str_End_Date
            dictExperimentDate["end_time"] = str_End_Time
            dictProposal["experiment_date"] = dictExperimentDate

            dictDataDelivery = {}
            dictDataDelivery["status"] = dict_Spread_Sheet["Data Delivery"]
            dictDataDelivery["gmail_address"] = dict_Spread_Sheet["Gmail address"]
            if "Upload to Google" in dict_Spread_Sheet["Data Delivery"]:
                dictDataDelivery["is_share_with_google"] = True
            else:
                dictDataDelivery["is_share_with_google"] = False
            dictProposal["data_delivery"] = dictDataDelivery

            dictARIMUpload = {}
            dictARIMUpload["status"] = dict_Spread_Sheet["ARIM Upload"]
            dictARIMUpload["id"] = dict_Spread_Sheet["ARIM ID"]
            dictARIMUpload["uploaded"] = False
            dictProposal["arim_upload"] = dictARIMUpload

            dictProposal["created_at"] = str_Start_Date + " " + str_Start_Time
            dictProposal["updated_at"] = str_Start_Date + " " + str_Start_Time

            dictProposal["enable_status"] = dict_Spread_Sheet["Enable"]
            dictProposal["is_used_now"] = False
            dictProposal["is_finished"] = False

            created_ID = dict_Spread_Sheet["Created ID"]
            if created_ID == "" or created_ID == self.default_Experiment_ID:
                dictProposal["id"] = self.generate_Experiment_ID(
                    dictProposal=dictProposal, list_generate_ID=list_generate_ID
                )
            else:
                dictProposal["id"] = created_ID
            list_ID.append(dictProposal["id"])
            listDictProposals.append(dictProposal)
        return listDictProposals, list_ID

    def save_All_Proposals(self, str_Filename_To_Save_Json=""):
        listDictProposal = []
        for proposal in self._proposals:
            dict_Proposal = proposal.getDictProposal()
            if (
                dict_Proposal["enable_status"] == "Enable"
                and dict_Proposal["id"] != self.default_Experiment_ID
            ):
                listDictProposal.append(dict_Proposal)
        if str_Filename_To_Save_Json == "":
            str_Filename_To_Save_Json = self.str_Filename_Proposal_List
        with open(str_Filename_To_Save_Json, mode="w", encoding="utf-8") as f:
            json.dump(listDictProposal, f, indent=4, ensure_ascii=False)

    def update_Spread_Sheet_For_Brows(self):
        list_Str_ID_Brows_Spread_Sheet = (
            self.google_Spread_Sheet_Handler.get_list_ID_Spread_Sheet_Brows()
        )
        # str_ID_Brows_Spread_Sheet = list_Str_ID_Brows_Spread_Sheet[0]
        listColumns = [
            "Experiment ID",
            "User Name",
            "Instrument",
            "Instrument ID",
            "Start Date",
            "End Date",
            "Contact Information",
            "Data Delivery",
            "GMail Account",
            "ARIM Upload",
            "ARIM ID",
            "URL For Edit",
        ]
        first_line = ["" for i in range(len(listColumns))]
        first_line[0] = "Register URL :"
        first_line[
            1
        ] = "https://docs.google.com/forms/d/e/1FAIpQLScRdnWUe8hBALouh2hC1t8HHosAzj-ma54EofLYek76IDGCQA/viewform?usp=sf_link"

        listSave = []
        listSave.append(first_line)
        listSave.append(listColumns)
        for proposal in self._proposals:
            dict_Proposal = proposal.getDictProposal()
            if dict_Proposal["enable_status"] == "Disable":
                continue
            listSaveSingle = []
            experiment_ID = dict_Proposal["id"]
            if experiment_ID == self.default_Experiment_ID:
                listSaveSingle.append("")
            else:
                listSaveSingle.append(proposal.getID())
            listSaveSingle.append(dict_Proposal["creators"][0]["name"])
            listSaveSingle.append(dict_Proposal["instrument"]["name"])
            listSaveSingle.append(dict_Proposal["instrument"]["identifier"])
            str_Start_Date = (
                dict_Proposal["experiment_date"]["start_date"]
                + " "
                + dict_Proposal["experiment_date"]["start_time"]
            )
            listSaveSingle.append(str_Start_Date)
            str_End_Date = (
                dict_Proposal["experiment_date"]["end_date"]
                + " "
                + dict_Proposal["experiment_date"]["end_time"]
            )
            listSaveSingle.append(str_End_Date)
            # listSaveSingle.append(
            #     proposal.getDictProposal()["experiment_date"]["end_date"])
            # listSaveSingle.append(
            #     proposal.getDictProposal()["experiment_date"]["end_time"])
            str_Contact_Information = ""
            str_Contact_Information += dict_Proposal["creators"][0]["email"]
            str_Contact_Information += "/"
            str_Contact_Information += dict_Proposal["creators"][0]["affiliation"]
            str_Contact_Information += "/"
            str_Contact_Information += dict_Proposal["contact"]["phone_number"]
            str_Contact_Information += "/"
            str_Contact_Information += dict_Proposal["contact"]["address"]
            listSaveSingle.append(str_Contact_Information)
            listSaveSingle.append(dict_Proposal["data_delivery"]["status"])
            listSaveSingle.append(dict_Proposal["data_delivery"]["gmail_address"])
            listSaveSingle.append(dict_Proposal["arim_upload"]["status"])
            listSaveSingle.append(dict_Proposal["arim_upload"]["id"])
            try:
                listSaveSingle.append(dict_Proposal["url_for_edit"])
            except KeyError:
                listSaveSingle.append("")
            listSave.append(listSaveSingle)

        int_Len_ID_SpreadSheet = len(list_Str_ID_Brows_Spread_Sheet)
        for i, str_ID_Brows_Spread_Sheet in enumerate(list_Str_ID_Brows_Spread_Sheet):
            self.logger.debug(
                "Progress Load Spread Sheet: {}/{}".format(i, int_Len_ID_SpreadSheet)
            )
            # print(i)
            # time.sleep(5)
            self.google_Spread_Sheet_Handler.overwrite_All_Value_To_Spread_Sheet_Brows(
                i, listSave
            )

    def generate_Experiment_ID(self, dictProposal, list_generate_ID=[3215, 0]):
        if not re.match(
            r"^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}$",
            dictProposal["experiment_date"]["start_date"],
        ):
            experiment_ID = self.default_Experiment_ID
        elif not re.match(
            r"^[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}$",
            dictProposal["experiment_date"]["end_date"],
        ):
            experiment_ID = self.default_Experiment_ID
        elif dictProposal["creators"][0]["name"] == "":
            experiment_ID = self.default_Experiment_ID
        elif dictProposal["instrument"]["name"] == "":
            experiment_ID = self.default_Experiment_ID
        else:
            strListStateDate = dictProposal["experiment_date"]["start_date"].split("/")
            datetimeStartDate = datetime.datetime(
                int(strListStateDate[0]),
                int(strListStateDate[1]),
                int(strListStateDate[2]),
            )
            Index = list_generate_ID[0] * list_generate_ID[1]
            Index_Temp = Index
            parity1 = 0
            parity2 = 0
            for k in range(20):
                if Index == 0:
                    break
                if k % 2 == 0:
                    parity1 += Index % 10
                else:
                    parity2 += Index % 10
                Index = Index // 10

            # parity = parity % 10
            experiment_ID = "{:02d}{:02d}-{:01d}{}-{:04d}{:01d}".format(
                datetimeStartDate.year % 100,
                datetimeStartDate.month % 100,
                parity1 % 10,
                dictProposal["instrument"]["identifier"][3:],
                Index_Temp % 10**4,
                parity2 % 10,
            )
            list_generate_ID[1] = (list_generate_ID[1] + 1) % 10**4
        return experiment_ID

    def get_Enabled_IDs(self):
        listIDs = []
        proposals = self._proposals
        for proposal in proposals:
            id = proposal.getID()
            if proposal.getIsEnable() and id != "0000-000-000001":
                listIDs.append()
        return listIDs


# %%
if __name__ == "__main__":
    proposal = ProposalList()
    proposal.loadIDListOfSpreadSheet()
    iDSheet = proposal.listIDsSpreadSheet[1]
    proposal.loadFromSpreadSheet(iDSheet)
    # for pro in proposal.getAllProposals():
    #     print(pro.getDictProposal())
    proposal.updateSpreadSheetForBrows()

    # proposal.loadFromExcel("./Usage_statius_smartlab.xlsx")
    # print(proposal.getProposal(0).getDictProposal())
