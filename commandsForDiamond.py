from APIs.checkUsageID import checkID
from APIs.finishExperiment import FinishExperiment
from APIs.periodicUpdate import PeriodicUpdate
from APIs.checkAndGetSingleProposal import CheckAndGetSingleProposal
from APIs.startExperiment import StartExperiment
from APIs.getMetaData import GetMetaData
from APIs.copyFromOriginalToShareFolder import Copy_From_Original_To_Share

import json
import logging
# from proposal import ProposalList


class CommandsDiamond:
    def __init__(self, logger=None, environment_Variable=None):
        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        if environment_Variable is None:
            self.environment_Variable = {}
            self.read_environment_variable()
        else:
            self.environment_Variable = environment_Variable

    def set_Google_Auth_For_Drive(self, google_Auth_For_Drive):
        self.google_Auth_For_Drive = google_Auth_For_Drive
        # logger(self.google_Auth_For_Drive)

    def read_environment_variable(self):
        self.environment_Variable = json.load(
            open("C:/diamond/environment_variable.json",
                 mode="r",
                 encoding='utf-8'))
        # self.environment_Variable[]

    def check_UsageID(self, command, args, identifier):
        # コマンドとargsを両方とも受け取って。コマンドがあっていない場合にfalseを返す。
        # コマンド処理と実際の処理が分かれているのでダブルチェックがあるといい。
        # メモ：isFinish は別管理したほうが良い。一つのファイルを書きだすのは一つのプログラムに限る。
        # DBを作る場合はSQL Lightを使うのが簡単。ファイルベース。
        # 本格的なDBを設計する場合はMaria DB
        if command != 'Check_UsageID':
            return None
        experiment_ID = args['experiment_id']
        checkIDExecuter = checkID(
            dict_Environment_Variable=self.environment_Variable)
        """
        # checkIDExecuter.setDatabaseFilename(
        #     self.environment_Variable["database_user_information_json_loading"]
        # )
        # checkIDExecuter.set_Data_Directory(
        #     self.environment_Variable["storage_directory"],
        #     self.environment_Variable["proposal_directory"])
        # checkIDExecuter.set_ID_Filename(
        #     self.environment_Variable["database_user_id_json_loading"])
        # checkIDExecuter.loadDatabase()
        """
        dictReturnMsg = checkIDExecuter.check_ID_Is_Exists(experiment_ID)
        dictReturnMsg["command"] = command
        dictReturnMsg["identifier"] = identifier
        return dictReturnMsg

    def finish_Experiment(self, command, args, identifier):

        if command != 'Finish_Experiment':
            return None
        experiment_ID = args['experiment_id']
        # metaData = args['metaData']
        strShareDirectory = args['storagePCShareDirectory']
        isAppendExisting = args['isAppendExisting']
        listFilleNames = args['file_names']
        listDictMetaDatas = args["meta_data"]
        dict_Experiment_Information = args["experiment_information"]

        finishExperimentExecuter = FinishExperiment(
            experiment_ID=experiment_ID,
            share_Directory=strShareDirectory,
            list_File_Names=listFilleNames,
            dict_Environment_Variable=self.environment_Variable,
            google_Auth_For_Drive=self.google_Auth_For_Drive,
            logger=self.logger)

        finishExperimentExecuter.setListDictMetaDatas(listDictMetaDatas)
        finishExperimentExecuter.set_dict_Experiment_information(
            dict_Experiment_Information)
        finishExperimentExecuter.setIsAppendExisting(isAppendExisting)
        dictReturnMsg = finishExperimentExecuter.finishExperiment()
        dictReturnMsg["command"] = command
        dictReturnMsg["identifier"] = identifier
        return dictReturnMsg

    def read_Use_Information_From_Shared_Excel(self, command, args,
                                               identifier):
        if command != 'Read_Use_Info_From_Excel':
            return None
        return args

    def periodic_Update_Spread_Sheet(self):
        periodicUpdateExecutor = PeriodicUpdate(
            self.logger, dict_Environment_Variable=self.environment_Variable)
        # periodicUpdateExecutor.set_logger(self.logger)
        periodicUpdateExecutor.runSchedule()

    def check_And_Get_Single_Proposal(self, command, args, identifier):
        if command != 'Check_And_Get_Single_Proposal':
            return None
        usageID = args['experiment_id']
        checkAndGetSingleProposalExecuter = CheckAndGetSingleProposal()
        checkAndGetSingleProposalExecuter.setProposalDirectory(
            self.environment_Variable["proposal_directory"])
        dictReturnMsg = checkAndGetSingleProposalExecuter.checkAndGetSingleProposal(
            usageID)
        dictReturnMsg["command"] = command
        dictReturnMsg["identifier"] = identifier
        return dictReturnMsg

    def start_Experiment(self, command, args, identifier):
        if command != 'Start_Experiment':
            return None
        experiment_ID = args['experiment_id']
        startExperimentExecuter = StartExperiment(
            str_Experiment_ID=experiment_ID,
            dict_Environment_Variable=self.environment_Variable)
        '''
        # startExperimentExecuter.set_Proposal_List_Filename(
        #     self.environment_Variable["database_proposal_list_json_loading"])
        # startExperimentExecuter.set_UsageID(usageID)
        # startExperimentExecuter.set_Saving_Directory(
        # self.environment_Variable["storage_directory"])
        '''
        dictReturnMsg = startExperimentExecuter.start_Experiment()
        dictReturnMsg["command"] = command
        dictReturnMsg["identifier"] = identifier
        return dictReturnMsg

    def get_Meta_Data(self, command, args, identifier):
        if command != 'Get_Meta_Data':
            return None
        usageID = args['experiment_id']
        getMetaDataExecuter = GetMetaData()
        getMetaDataExecuter.set_UsageID(usageID)
        getMetaDataExecuter.set_Storage_Directory(
            self.environment_Variable["storage_directory"])
        dictReturnMsg = getMetaDataExecuter.getMetaData(usageID)
        dictReturnMsg["command"] = command
        dictReturnMsg["identifier"] = identifier
        return dictReturnMsg

    def Copy_From_Original_To_Share(self, command, args, identifier):
        if command != 'Copy_From_Original_To_Share':
            return None
        experiment_ID = args['experiment_id']
        share_Directory = args['storagePC_share_directory']
        copy_Original_Executer = Copy_From_Original_To_Share()
        copy_Original_Executer.set_Experiment_ID(experiment_ID)
        copy_Original_Executer.set_Storage_Directory(
            self.environment_Variable["storage_directory"])
        copy_Original_Executer.set_Share_Directory(share_Directory)
        dictReturnMsg = {}
        # dictReturnMsg["args"] = {"experiment_information": {}}
        dictReturnMsg = copy_Original_Executer.copy_Original_To_Share()
        dictReturnMsg["command"] = command
        dictReturnMsg["identifier"] = identifier
        return dictReturnMsg
