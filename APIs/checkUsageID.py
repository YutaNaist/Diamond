from APIs.proposal import ProposalList, Proposal
import json


class checkID:
    def __init__(self, dict_Environment_Variable={}):
        # self._strDataBaseFilename = ""
        if dict_Environment_Variable != {}:
            self.str_Storage_Directory = dict_Environment_Variable[
                "storage_directory"]
            self.str_Proposal_Directory = dict_Environment_Variable[
                "proposal_directory"]
            self.str_IDs_Filename = dict_Environment_Variable[
                "database_user_id_json_loading"]

    def loadDatabase(self):
        self.proposalListCurrentList = ProposalList()
        self.proposalListCurrentList.read_Proposal_List_From_Database_Json(
            self._strDataBaseFilename)

    def setDatabaseFilename(self, strJsonFilename):
        self._strDataBaseFilename = strJsonFilename

    def set_Data_Directory(self, str_Storage_Directory,
                           str_Proposal_Directory):
        self.str_Storage_Directory = str_Storage_Directory
        self.str_Proposal_Directory = str_Proposal_Directory

    def set_ID_Filename(self, str_IDs_Filename):
        self.str_IDs_Filename = str_IDs_Filename

    def check_ID_Is_Exists(self, str_Experiment_ID):
        dictReturnMessage = {}
        IDs = json.load(open(self.str_IDs_Filename, mode="r"))
        proposal = Proposal()
        if not (str_Experiment_ID in IDs):
            dictReturnMessage["status"] = False
            dictReturnMessage["message"] = "Error: Experiment ID is not found"
            returnArgs = {}
            dictReturnMessage["args"] = returnArgs
        else:
            try:
                proposal.readProposalFromJson(self.str_Storage_Directory +
                                              str_Experiment_ID + "/" +
                                              str_Experiment_ID + ".json_prop")
                if proposal.getIsEnable() is False:
                    dictReturnMessage["status"] = False
                    dictReturnMessage[
                        "message"] = "Error: This Experiment ID is found but the ID is not enable."
                    returnArgs = {}
                    dictReturnMessage["args"] = returnArgs
                elif proposal.getIsUsed() is True:
                    dictReturnMessage["status"] = False
                    dictReturnMessage[
                        "message"] = "Error: This Experiment ID is used in other place."
                    returnArgs = {}
                    returnArgs["database"] = proposal.getDictProposal()
                    dictReturnMessage["args"] = returnArgs
                else:
                    dictReturnMessage["status"] = True
                    dictReturnMessage["message"] = "Experiment ID is found"
                    returnArgs = {}
                    returnArgs["database"] = proposal.getDictProposal()
                    dictReturnMessage["args"] = returnArgs
            except FileExistsError:
                dictReturnMessage["status"] = False
                dictReturnMessage[
                    "message"] = "Error: UsageID is found but the file does not exist."
                returnArgs = {}
                dictReturnMessage["args"] = returnArgs
        return dictReturnMessage
