import datetime
import sched
from multiprocessing import Process
import time
import json
import os
import logging

# import glob

import gspread

try:
    from APIs.proposal import ProposalList, Proposal
    from APIs.googleSpreadSheetHandler import GoogleSpreadSheetHandler
except ModuleNotFoundError:
    from proposal import ProposalList, Proposal
    from googleSpreadSheetHandler import GoogleSpreadSheetHandler


class PeriodicUpdate:
    # periodicExecutionTime = {"hour": 0, "minute": 0, "second": 0}
    # __periodicInterval = 86400
    # loadExcelList = [
    #     "C:/Users/yutay/OneDrive - 奈良先端科学技術大学院大学/ARIM/SoftwareDevelop/diamond/Usage_statuis_smartlab.xlsx"
    # ]

    def __init__(
        self, logger=None, dict_Environment_Variable={}, Google_Auth_For_Drive=None
    ):
        self.str_file_Json_Database = "./"
        self.str_ID_Spread_Sheet_ID_List = ""
        self.str_Authorize_Json = ""
        self.dict_Periodic_Execution_Time = {"hour": 10, "minute": 20, "second": 0}
        self.int_Periodic_Interval = 60
        self.stopFlag = False
        self.floatExecutingTime = 0.0
        self.IDs = []
        self.is_flag_second_read = False

        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        # self.dict_Environment_Variable = dict_Environment_Variable
        if dict_Environment_Variable != {}:
            self.str_filename_temp_generate_json = (
                dict_Environment_Variable["database_directory"]
                + dict_Environment_Variable["temp_generate_ID_json"]
            )
            try:
                self.list_Temp_Generate_ID = json.load(
                    open(self.str_filename_temp_generate_json, mode="r")
                )
            except BaseException:
                self.list_Temp_Generate_ID = [3241, 0]

            self.dict_Instrument_ID = json.load(
                open(
                    dict_Environment_Variable["database_directory"]
                    + dict_Environment_Variable["instrument_database_json"],
                    mode="r",
                    encoding="utf-8",
                )
            )

            self.dict_Periodic_Execution_Time = dict_Environment_Variable[
                "periodic_running_starting"
            ]
            self.int_Periodic_Interval = dict_Environment_Variable[
                "periodic_running_interval_second"
            ]
            self.str_ID_Spread_Sheet_ID_List = dict_Environment_Variable[
                "api_key_spreadsheet_list"
            ]

            self.database_directory = dict_Environment_Variable["database_directory"]

            self.str_Authorize_Json = (
                self.database_directory
                + dict_Environment_Variable["authorization_json_google_api"]
            )
            self.str_file_Json_Database = (
                self.database_directory
                + dict_Environment_Variable["database_user_information_json_loading"]
            )
            self.filePathOfAllIds = (
                self.database_directory
                + dict_Environment_Variable["database_user_id_json_loading"]
            )
            self.str_API_Key_Drive = (
                self.database_directory
                + dict_Environment_Variable["authorization_json_google_drive_api"]
            )
            self.str_Setting_Yaml = (
                self.database_directory
                + dict_Environment_Variable["setting_yaml_google_drive_api"]
            )

            self.storageDirectory = dict_Environment_Variable["storage_directory"]
            self.proposalDirectory = dict_Environment_Variable["proposal_directory"]

            self.str_url_spreadsheet_input = dict_Environment_Variable[
                "spreadsheet_url_input"
            ]

            self.google_Spread_Sheet_Handler = GoogleSpreadSheetHandler(
                str_Authorize_Json=self.str_Authorize_Json, logger=self.logger
            )

            self.proposal_List_To_Save = ProposalList(
                google_Spread_Sheet_Handler=self.google_Spread_Sheet_Handler,
                logger=self.logger,
            )

    def set_logger(self, logger):
        self.logger = logger

    def set_Data_Directory(self, storageDirectory, proposalDirectory):
        self.storageDirectory = storageDirectory
        self.proposalDirectory = proposalDirectory

    def set_API_Key_SpreadsheetList(self, list_API_Key_Spreadsheet):
        self.str_ID_Spread_Sheet_ID_List = list_API_Key_Spreadsheet

    def set_API_Key_Google_Drive(
        self, str_Directory_API_Key_Drive, str_Directory_Setting_Yaml
    ):
        self.str_API_Key_Drive = str_Directory_API_Key_Drive
        self.str_Setting_Yaml = str_Directory_Setting_Yaml

    def set_Authorization_Json(self, str_Authorization_Json):
        self.str_Authorize_Json = str_Authorization_Json

    def setStartConditionAndInterval(self, periodicExecutionTime, periodicInterval):
        self.dict_Periodic_Execution_Time = periodicExecutionTime
        self.int_Periodic_Interval = periodicInterval

    def setListLoadExcel(self, listLoadExcel):
        self.listLoadExcel = listLoadExcel

    def setFilePathOfJsonDatabase(self, filePathOfJsonDatabase, filePathOfAllIds):
        self.str_file_Json_Database = filePathOfJsonDatabase
        self.filePathOfAllIds = filePathOfAllIds

    def calculateFirstInterval(self):
        dtNow = datetime.datetime.now()
        # dtTomorrow = dtNow + datetime.timedelta(days=1)
        dtTomorrow = datetime.datetime.now()
        dtTomorrow = datetime.datetime(
            year=dtTomorrow.year,
            month=dtTomorrow.month,
            day=dtTomorrow.day,
            hour=self.dict_Periodic_Execution_Time["hour"],
            minute=self.dict_Periodic_Execution_Time["minute"],
            second=self.dict_Periodic_Execution_Time["second"],
        )
        timeDelta = (dtTomorrow - dtNow).total_seconds()
        return int(timeDelta)

    def runSchedule(self):
        schedule = sched.scheduler()
        calculationInterval = self.calculateFirstInterval()
        schedule.enter(
            calculationInterval,
            1,
            self.periodicRun,
            kwargs={
                "schedule": schedule,
                #    "interval": self.int_Periodic_Interval
                "interval": calculationInterval,
            },
        )
        schedule.run()
        while True:
            try:
                # print("periodic check 3")
                intNextInterval = (
                    self.int_Periodic_Interval - self.floatExecutingTime // 1
                )
                self.floatExecutingTime = (
                    self.floatExecutingTime - self.floatExecutingTime // 1
                )
                schedule = sched.scheduler()
                schedule.enter(
                    intNextInterval,
                    1,
                    self.periodicRun,
                    kwargs={
                        "schedule": schedule,
                        #   "interval": self.int_Periodic_Interval
                        "interval": intNextInterval,
                    },
                )
                print(datetime.datetime.now())
                schedule.run()
            except BaseException as e:
                print("check 1")
                logging.warning(e)

    def periodicRun(self, schedule, interval):
        # print("periodic check 5")
        startTime = time.time()
        try:
            self.logger.info("periodic update running.")
            self.updateJsonDatabase()
            self.logger.info("periodic update finish")
        except gspread.exceptions.APIError:
            self.logger.warning("periodic update failed By Google Error.")
        # except BaseException as e:
        #     print("check 2")
        #     self.logger.warning(e)
        endTime = time.time()
        self.floatExecutingTime += endTime - startTime
        # print(endTime - startTime)
        # print("periodic check 6")

    def runProcess(self):
        pros = Process(target=self.runSchedule, args=())
        pros.start()

    def updateJsonDatabase(self):
        """
        Main component for periodic running.
        The ID is generated from list in the self.list_Temp_Generate_ID.
        ID = list_generate[0] * list_generate[1]. list_generate[0] should be odd number. list_generate[1] is incremental number.
        The user information is read from the spread sheet.
        The ids of spread sheet is concentrated in the one spreadsheet, which should be read at first.
        If all of the spread sheet is not updated, is_Updated should be False and the operation after that should be skipped.
        """

        # Import ID list from Database/all_IDs.json
        # try:
        self.IDs = json.load(open(self.filePathOfAllIds, mode="r", encoding="utf-8"))
        """
        # except FileExistsError:
        #     pass
        # except FileNotFoundError:
        #     pass
        # print("periodic: make proposal directory")
        """

        # Read Google Spread sheet ID list from spreadsheet.
        # self.google_Spread_Sheet_Handler = GoogleSpreadSheetHandler(str_Authorize_Json=self.str_Authorize_Json)
        self.google_Spread_Sheet_Handler.update_Spread_Sheet_IDs_From_Sheet(
            self.str_ID_Spread_Sheet_ID_List
        )
        self.logger.debug("load ID List")

        # Load each spreadsheet. is_Update will be False if all spreadsheets is not updated.
        self.proposal_List_To_Save = ProposalList(
            google_Spread_Sheet_Handler=self.google_Spread_Sheet_Handler,
            logger=self.logger,
        )

        # is_Update = self.proposal_List_To_Save.load_From_SpreadSheet_List(
        #     list_generate_ID=self.list_Temp_Generate_ID,
        #     dict_Instrument_ID=self.dict_Instrument_ID)
        is_Update = self.proposal_List_To_Save.load_From_SpreadSheet_Input(
            self.str_url_spreadsheet_input, self.dict_Instrument_ID
        )
        self.logger.debug("load From Spread Sheet")
        self.logger.debug(is_Update)

        # Save all proposal to Database/proposals.json
        self.proposal_List_To_Save.save_All_Proposals(self.str_file_Json_Database)
        self.logger.debug("save all proposals")
        json.dump(
            self.list_Temp_Generate_ID,
            open(self.str_filename_temp_generate_json, mode="w"),
        )
        self.logger.debug("json dump temp generate id")

        if is_Update is True or self.is_flag_second_read is True:
            self.logger.info("periodic: make proposal directory")
            proposals = self.proposal_List_To_Save.get_List_All_Proposals()
            for proposal in proposals:
                id = proposal.getID()
                self.logger.info(id)
                isEnable = proposal.getIsEnable()
                if isEnable is False:
                    continue

                base_Path = self.storageDirectory + id + "/"
                proposal_Path = base_Path + id + ".json_prop"
                proposal_Log_Path = base_Path + id + ".json_prop_log"
                base_Path_id = self.storageDirectory + id + "/" + id + "/"
                data_Path = base_Path_id + "data/"
                metadata_Path = base_Path_id + "metadata/"
                dict_Proposal = proposal.getDictProposal()
                if not (id in self.IDs) and id != "":
                    self.IDs.append(id)
                    try:
                        os.makedirs(base_Path)
                        os.makedirs(base_Path_id)
                        os.makedirs(data_Path)
                        os.makedirs(metadata_Path)
                    except FileExistsError:
                        pass
                else:
                    old_proposal = Proposal()
                    old_proposal.readProposalFromJson(proposal_Path)
                    dict_old_proposal = old_proposal.getDictProposal()
                    dict_Proposal["is_used_now"] = dict_old_proposal["is_used_now"]
                    dict_Proposal["is_finished"] = dict_old_proposal["is_finished"]
                # proposal.saveSingleProposal(base_Path + id + ".json_prop")
                json.dump(
                    dict_Proposal,
                    open(proposal_Path, mode="w", encoding="utf-8"),
                    ensure_ascii=False,
                    indent=4,
                )

                dictLogs = []
                dictLogs.append(dict_Proposal)
                json.dump(
                    dictLogs,
                    open(proposal_Log_Path, mode="w", encoding="utf-8"),
                    ensure_ascii=False,
                    indent=4,
                )
                # except FileExistsError:
                #     pass
                # except FileNotFoundError:
                #     pass

        if is_Update is True or self.is_flag_second_read is True:
            self.logger.info("periodic: write to brows sheet")
            self.proposal_List_To_Save.update_Spread_Sheet_For_Brows()
        else:
            self.logger.info("periodic: skip writing to brows sheet")

        if is_Update is True:
            self.is_flag_second_read = True
        else:
            self.is_flag_second_read = False
        """
        for i, idSpreadSheet in enumerate(listIDSpreadSheet[1]):
            self.logger.info(i)
            time.sleep(5)
            self.proposal_List_To_Save.update_Spread_Sheet_For_Brows(
                idSpreadSheet)
        """
        json.dump(
            self.IDs,
            open(self.filePathOfAllIds, mode="w", encoding="utf-8"),
            ensure_ascii=False,
            indent=4,
        )
        # del proposalListToSave
        # print("periodic update finish")
        return 0


# %%
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_Stream_Handler = logging.StreamHandler()
    sh_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(process)d - %(message)s", "%Y/%m/%d %H:%M:%S"
    )
    log_Stream_Handler.setFormatter(sh_formatter)
    logger.addHandler(log_Stream_Handler)

    environment_Valuable = json.load(open("environment_variable-copy2.json", mode="r"))
    periodicUpdateExecutor = PeriodicUpdate(
        logger=logger, dict_Environment_Variable=environment_Valuable
    )
    print("periodic check 1")
    periodicUpdateExecutor.runSchedule()
