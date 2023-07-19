import os
import APIs.proposal as proposal


class StartExperiment:
    def __init__(self, str_Experiment_ID="", dict_Environment_Variable={}):
        self.str_Experiment_ID = str_Experiment_ID

        if dict_Environment_Variable != {}:
            self.dict_Environment_Variable = dict_Environment_Variable
            self.str_Save_Directory = self.dict_Environment_Variable[
                "storage_directory"] + self.str_Experiment_ID + "/"
            self.str_Proposal_File = self.str_Save_Directory + self.str_Experiment_ID + ".json_prop"
            self.str_Metadata_Directory = self.str_Save_Directory + "metadata/"
            self.str_Original_Data_Directory = self.str_Save_Directory + "data/"

    def set_Experiment_ID(self, str_Experiment_ID):
        self.str_Experiment_ID = str_Experiment_ID

    def set_Saving_Directory(self, strSavingDirectory):
        strSavingDirectory = strSavingDirectory + +self.str_Experiment_ID + "/"
        self.str_Save_Directory = strSavingDirectory
        self.str_Proposal_File = strSavingDirectory + self.str_Experiment_ID + ".json_prop"
        self.str_Metadata_Directory = strSavingDirectory + "metadata/"
        self.str_Original_Data_Directory = strSavingDirectory + "data/"

    def set_Proposal_List_Filename(self, strDatabaseJson):
        self.strDatabaseJson = strDatabaseJson

    def start_Experiment(self):
        try:
            os.makedirs(self.str_Save_Directory)
            os.makedirs(self.str_Metadata_Directory)
            os.makedirs(self.str_Original_Data_Directory)
        except FileExistsError:
            pass
        current_Proposal = proposal.Proposal()
        print(self.str_Proposal_File)
        try:
            current_Proposal.readProposalFromJson(self.str_Proposal_File)
        except FileNotFoundError:
            return {"status": False, "message": "Failed making directory"}

        current_Proposal.setProposalInformationValue("is_used_now", True)
        print(current_Proposal.getDictProposal())
        print(self.str_Proposal_File)
        current_Proposal.saveSingleProposal(self.str_Proposal_File)
        return {"status": True, "message": "Success"}

        # proposalList = proposal.ProposalList()
        # proposalList.read_Proposal_List_From_Database_Json(
        #     self.strDatabaseJson)
        # index = proposalList.search_ID(self.str_Experiment_ID)
        # if index == -1:
        #     return {"status": False, "message": "Failed making directory"}
        # else:
        #     proposal_current = proposalList.get_Proposal(index)
        #     proposal_current = proposal.Proposal()
        #     proposal_current.saveSingleProposal("{}{}.json_prop".format(
        #         self.strSavingDirectory, self.str_Experiment_ID))
        #     return {"status": True, "message": "Success"}
