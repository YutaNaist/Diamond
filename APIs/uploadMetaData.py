# import APIs.proposal as proposal


class UploadMetaData:

    def __init__(self):
        pass

    def set_UsageID(self, strUsageID):
        self.strUsageID = strUsageID

    def set_Saving_Directory(self, strSavingDirectory):
        self.strSavingDirectory = strSavingDirectory
        self.strMetadataDirectory = strSavingDirectory + "metadata/"

    def upload_MetaData(self):
        pass
