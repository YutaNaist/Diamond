import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging

import datetime
import time


class GoogleSpreadSheetHandler:

    def __init__(self,
                 str_Authorize_Json: str = "",
                 logger: logging.Logger = None) -> None:
        if logger is None:
            logger = logging.getLogger(__name__)
        else:
            self.logger = logger
        # str_ID_Spread_Sheet="",
        # self.str_ID_Spread_Sheet = str_ID_Spread_Sheet
        self.str_Authorize_Json = str_Authorize_Json
        scope = ['https://www.googleapis.com/auth/drive']
        self.credential = ServiceAccountCredentials.from_json_keyfile_name(
            self.str_Authorize_Json, scope)
        self.client = gspread.authorize(self.credential)
        self.last_updated_ID_List_Sheet = ""
        self.last_updated_Input_sheet = ""

    def load_All_Value_From_Input_Sheet(self,
                                        str_URL_Spread_Sheet: str = ""
                                        ) -> list:
        try:
            sheet = self.client.open_by_url(str_URL_Spread_Sheet)
            last_Update = sheet.lastUpdateTime
            worksheet = sheet.get_worksheet(0)
            #self.last_updated_Input_sheet = last_Update
            listAll = worksheet.get_all_values()
            s_format = '%Y/%m/%d %H:%M:%S'
            newest_date = datetime.datetime.strptime(listAll[1][0], s_format)
            for i in range(1, len(listAll)):
                compare_data = (datetime.datetime.strptime(listAll[i][0], s_format))
                if compare_data > newest_date:
                    newest_date = compare_data
            self.logger.debug(newest_date, self.last_updated_Input_sheet)
            if newest_date == self.last_updated_Input_sheet:
                return []
            else:
                self.last_updated_Input_sheet = newest_date
                return listAll

        except gspread.exceptions.APIError:
            self.logger.warning("APIError in Load Spread Sheet")
            time.sleep(10)
            return self.load_All_Value_From_Input_Sheet(str_URL_Spread_Sheet)

    def load_All_Value_From_Spread_Sheet(self,
                                         str_URL_Spread_Sheet: str = ""
                                         ) -> list:
        try:
            # sheet = self.client.open_by_key(str_ID_Spread_Sheet)
            sheet = self.client.open_by_url(str_URL_Spread_Sheet)
            worksheet = sheet.get_worksheet(0)
            return worksheet.get_all_values()
        except gspread.exceptions.APIError:
            self.logger.warning("APIError in Load Spread Sheet")
            time.sleep(10)
            return self.load_All_Value_From_Spread_Sheet(str_URL_Spread_Sheet)

    def update_Spread_Sheet_IDs_From_Sheet(self,
                                           str_URL_Spread_Sheet: str) -> bool:
        sheet = self.client.open_by_url(str_URL_Spread_Sheet)
        last_Update_Time = sheet.lastUpdateTime
        if last_Update_Time == self.last_updated_ID_List_Sheet:
            return True
        else:
            try:
                worksheet = sheet.get_worksheet(0)
                data = worksheet.get_all_values()
                self.list_URL_SpreadSheet_Input = []
                self.list_URL_SpreadSheet_Brows = []
                self.list_last_update_Date_SpreadSheet = []
                for i in range(len(data) - 1):
                    if data[i + 1][1] != "" and data[i + 1][2] != "":
                        self.list_URL_SpreadSheet_Input.append(data[i + 1][1])
                        self.list_URL_SpreadSheet_Brows.append(data[i + 1][2])
                        self.list_last_update_Date_SpreadSheet.append("")
                self.last_updated_ID_List_Sheet = last_Update_Time
                return False
            except gspread.exceptions.APIError:
                self.logger.warning("APIError in update IDs")
                # self.logger.warning("APIError in update IDs")
                time.sleep(10)
                return self.update_Spread_Sheet_IDs_From_Sheet(
                    str_URL_Spread_Sheet)

    def get_list_ID_Spread_Sheet_Input(self) -> list:
        return self.list_URL_SpreadSheet_Input

    def get_list_ID_Spread_Sheet_Brows(self) -> list:
        return self.list_URL_SpreadSheet_Brows

    def load_All_Value_From_Spread_Sheet_Input(self, index: int) -> list:
        # print("Get Input")
        # print(self.list_last_update_Date_SpreadSheet[index])
        str_URL_Spread_Sheet_Input = self.list_URL_SpreadSheet_Input[index]
        str_last_update_Spread_Sheet_Input = self.list_last_update_Date_SpreadSheet[
            index]
        try:
            sheet = self.client.open_by_url(str_URL_Spread_Sheet_Input)

            last_Update = sheet.lastUpdateTime
            # print(last_Update)
            if last_Update == str_last_update_Spread_Sheet_Input:
                return []
            else:
                worksheet = sheet.get_worksheet(0)
                self.list_last_update_Date_SpreadSheet[index] = last_Update
                return worksheet.get_all_values()
        except gspread.exceptions.APIError:
            self.logger.warning("APIError in load sheet input")
            # print(e)
            time.sleep(10)
            # print("resend")
            return self.load_All_Value_From_Spread_Sheet_Input(index)

    '''
    def overwrite_Value_To_Spread_Sheet(str_ID_Spread_Sheet,
                                        str_Authorize_Json, list_All_Value,
                                        int_Row, int_Col):
        scope = ['https://www.googleapis.com/auth/drive']
        credential = ServiceAccountCredentials.from_json_keyfile_name(
            str_Authorize_Json, scope)
        client = gspread.authorize(credential)
        sheet = client.open_by_key(str_ID_Spread_Sheet)
        worksheet = sheet.get_worksheet(0)
        len_Original_Rows = len(worksheet.get_all_values())

        col_last = len(list_All_Value[0])  # DataFrameの列数
        row_last = len(list_All_Value)  # DataFrameの行数
        len_row = max(row_last, len_Original_Rows)
        cell_list = worksheet.range('A1:' + self.toAlpha(col_last) + str(len_row))

        for cell in cell_list:
            if cell.row > row_last:
                val = ""
            else:
                val = list_All_Value[cell.row - 1][cell.col - 1]
            cell.value = val
        worksheet.update_cells(cell_list)
    '''

    def overwrite_2D_Array_To_Spread_Sheet(self, str_URL_Spread_Sheet: str,
                                           str_Save_Range: str,
                                           list_All_Value: list) -> None:
        try:
            sheet = self.client.open_by_URL(str_URL_Spread_Sheet)
            worksheet = sheet.get_worksheet(0)
            worksheet.update(str_Save_Range, list_All_Value)
        except gspread.exceptions.APIError:
            self.logger.warning(
                "APIError in overwrite 2d array to spread sheet")
            # print(e)
            time.sleep(10)
            self.overwrite_2D_Array_To_Spread_Sheet(self, str_URL_Spread_Sheet,
                                                    str_Save_Range,
                                                    list_All_Value)

    def overwrite_All_Value_To_Spread_Sheet(self, str_URL_Spread_Sheet: str,
                                            list_All_Value: list) -> None:
        try:
            sheet = self.client.open_by_url(str_URL_Spread_Sheet)
            worksheet = sheet.get_worksheet(0)
            len_Original_Rows = worksheet.row_count

            col_last = len(list_All_Value[0])  # DataFrameの列数
            row_last = len(list_All_Value)  # DataFrameの行数

            len_row = max(row_last, len_Original_Rows)
            worksheet_range = 'A1:' + self.toAlpha(col_last) + str(len_row + 1)
            blank_Row = ["" for i in range(col_last)]
            for i in range(len_row):
                if i >= row_last:
                    list_All_Value.append(blank_Row)
            worksheet.update(worksheet_range, list_All_Value)
        except gspread.exceptions.APIError:
            self.logger.warning(
                "APIError in overwrite all value to spread sheet")
            # print(e)
            time.sleep(10)
            self.overwrite_All_Value_To_Spread_Sheet(str_URL_Spread_Sheet)

    def overwrite_All_Value_To_Spread_Sheet_Brows(
            self, index: int, list_All_Value: list) -> None:
        # print("over write Brows")
        str_URL_Spread_Sheet = self.list_URL_SpreadSheet_Brows[index]
        # print(index, "check1")
        try:
            sheet = self.client.open_by_url(str_URL_Spread_Sheet)
            # print(index, "check2")
            worksheet = sheet.get_worksheet(0)
            len_Original_Rows = worksheet.row_count

            col_last = len(list_All_Value[0])  # DataFrameの列数
            row_last = len(list_All_Value)  # DataFrameの行数

            len_row = max(row_last, len_Original_Rows)
            # print(index, "check3")
            worksheet_range = 'A1:' + self.toAlpha(col_last) + str(len_row + 1)
            blank_Row = ["" for i in range(col_last)]
            # print(index, "check4")
            for i in range(len_row):
                if i >= row_last:
                    list_All_Value.append(blank_Row)
            worksheet.update(worksheet_range, list_All_Value)
            # print(index, "check6")
        except gspread.exceptions.APIError:
            self.logger.warning("APIError in overwrite spread sheet Brwos")
            # print(e)
            time.sleep(10)
            # print("resend")
            self.overwrite_All_Value_To_Spread_Sheet_Brows(
                index, list_All_Value)

    def overwrite_ID_Value_To_Spread_Sheet(self, index: int, list_All_ID: list,
                                           int_Col: int) -> None:
        str_URL_Spread_Sheet = self.list_URL_SpreadSheet_Input[index]
        # print("over write ID")
        try:
            sheet = self.client.open_by_url(str_URL_Spread_Sheet)
            worksheet = sheet.get_worksheet(0)

            list_ID_Save = []
            row_last = len(list_All_ID)  # DataFrameの行数
            for i in range(row_last):
                list_ID_Save.append([list_All_ID[i]])
            worksheet_range = self.toAlpha(int_Col) + '2:' + self.toAlpha(
                int_Col) + str(row_last + 2)
            worksheet.update(worksheet_range, list_ID_Save)

            str_ID_Spread_Sheet = self.list_URL_SpreadSheet_Input[index]
            sheet = self.client.open_by_url(str_ID_Spread_Sheet)
            update_Time = sheet.lastUpdateTime
            self.list_last_update_Date_SpreadSheet[index] = update_Time
        except gspread.exceptions.APIError:
            self.logger.warning("APIError in overwrite ID")
            # print(e)
            time.sleep(10)
            # print("resend")
            self.overwrite_ID_Value_To_Spread_Sheet(index, list_All_ID,
                                                    int_Col)

    def toAlpha(self, num: int) -> str:
        if num <= 26:
            return chr(64 + num)
        elif num % 26 == 0:
            return self.toAlpha(num // 26 - 1) + chr(90)
        else:
            return self.toAlpha(num // 26) + chr(64 + num % 26)

    def set_Last_Update_Input(self, index: int) -> None:
        str_URL_Spread_Sheet = self.list_URL_SpreadSheet_Input[index]
        try:
            sheet = self.client.open_by_url(str_URL_Spread_Sheet)
            update_Time = sheet.lastUpdateTime
            self.list_last_update_Date_SpreadSheet[index] = update_Time
        except gspread.exceptions.APIError:
            self.logger.warning("APIError in check last update")
            # print(e)
            time.sleep(10)
            self.set_Last_Update_Input(index)


if __name__ == "__main__":
    import json
    environmentValuable = json("environment_variable-copy.json")
    gsHandler = GoogleSpreadSheetHandler(
        environmentValuable["database_directory"] +
        environmentValuable["authorize_json_google_api"],
        logger=None)
    gsHandler.update_Spread_Sheet_IDs_From_Sheet(
        environmentValuable["api_key_spreadsheet_list"])
