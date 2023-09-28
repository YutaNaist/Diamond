import json
import yaml
import logging

from pydrive2.auth import GoogleAuth

import commandsForDiamond
from load_environment_variable import load_environment_variable


def make_logger(dict_Environment_Variable):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_File_Handler = logging.FileHandler(
        dict_Environment_Variable["database_directory"] + 'log_periodic.log')
    # log_File_Handler = logging.handlers.RotatingFileHandler(
    #     'C:/diamond/log_diamond.log', maxBytes=100_000_000, BackupCount=10)
    fh_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s -%(process)d - %(message)s'
    )
    log_File_Handler.setFormatter(fh_formatter)

    log_Stream_Handler = logging.StreamHandler()
    sh_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(process)d - %(message)s',
        '%Y/%m/%d %H:%M:%S')
    log_Stream_Handler.setFormatter(sh_formatter)

    logger.addHandler(log_File_Handler)
    logger.addHandler(log_Stream_Handler)
    return logger


dict_Environment_Variable = load_environment_variable()
logger = make_logger(dict_Environment_Variable)
ipaddress = dict_Environment_Variable["host_ip"]
port = dict_Environment_Variable["host_port"]

google_auth_setting_yaml_filename = dict_Environment_Variable[
    "database_directory"] + dict_Environment_Variable[
        "setting_yaml_google_drive_api"]
google_auth_setting_yaml = yaml.load(open(google_auth_setting_yaml_filename,
                                          mode="r"),
                                     Loader=yaml.SafeLoader)
google_auth_setting_yaml['client_config_file'] = dict_Environment_Variable[
    "database_directory"] + "/Google_API_Keys/Certificate-Drive.json"

# print(google_auth_setting_yaml)
yaml.safe_dump(google_auth_setting_yaml,
               open(google_auth_setting_yaml_filename, mode="w"),
               default_flow_style=False,
               allow_unicode=True)

Google_Auth_For_Drive = GoogleAuth(
    dict_Environment_Variable["database_directory"] +
    dict_Environment_Variable["setting_yaml_google_drive_api"])
Google_Auth_For_Drive.LocalWebserverAuth()
Google_Auth_For_Drive.CommandLineAuth()

cmd = commandsForDiamond.CommandsDiamond(
    logger=logger, dict_Environment_Variable=dict_Environment_Variable)
cmd.set_Google_Auth_For_Drive(Google_Auth_For_Drive)
# cmd.set_Google_Auth_For_Drive(None)

if __name__ == '__main__':
    cmd.periodic_Update_Spread_Sheet()
