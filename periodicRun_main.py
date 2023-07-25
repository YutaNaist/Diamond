import json
import logging

from pydrive2.auth import GoogleAuth

import commandsForDiamond


def make_logger(environment_Variable):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    log_File_Handler = logging.FileHandler(environment_Variable["log_directory"] + 'log_periodic.log')
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


environment_Variable = json.load(
    open("C:/Program Files/diamond/environment_variable.json", mode="r", encoding='utf-8'))
logger = make_logger(environment_Variable)
ipaddress = environment_Variable["host_ip"]
port = environment_Variable["host_port"]

Google_Auth_For_Drive = GoogleAuth(
    environment_Variable["setting_yaml_google_drive_api"])
Google_Auth_For_Drive.LocalWebserverAuth()
Google_Auth_For_Drive.CommandLineAuth()

cmd = commandsForDiamond.CommandsDiamond(
    logger=logger, environment_Variable=environment_Variable)
cmd.set_Google_Auth_For_Drive(Google_Auth_For_Drive)
# cmd.set_Google_Auth_For_Drive(None)

if __name__ == '__main__':
    cmd.periodic_Update_Spread_Sheet()
