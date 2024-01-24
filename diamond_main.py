import json
import logging

# from multiprocessing import Process

from flask import Flask, request, jsonify
from pydrive2.auth import GoogleAuth

import commandsForDiamond
from load_environment_variable import load_environment_variable


def make_logger(dict_Environment_Variable):
    log_config = json.load(open("log_config_diamond.json", mode="r"))
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(__name__)

    # logger = logging.getLogger(__name__)
    # logger.setLevel(logging.DEBUG)

    # log_File_Handler = logging.FileHandler(
    #     dict_Environment_Variable["database_directory"] + 'log_diamond.log')
    # # log_File_Handler = logging.handlers.RotatingFileHandler(
    # #     'C:/diamond/log_diamond.log', maxBytes=100_000_000, BackupCount=10)
    # fh_formatter = logging.Formatter(
    #     '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s -%(process)d - %(message)s'
    # )
    # log_File_Handler.setFormatter(fh_formatter)

    # log_Stream_Handler = logging.StreamHandler()
    # sh_formatter = logging.Formatter(
    #     '%(asctime)s - %(levelname)s - %(process)d - %(message)s',
    #     '%Y/%m/%d %H:%M:%S')
    # log_Stream_Handler.setFormatter(sh_formatter)

    # logger.addHandler(log_File_Handler)
    # logger.addHandler(log_Stream_Handler)
    return logger


dict_Environment_Variable = load_environment_variable()
logger = make_logger(dict_Environment_Variable)
ipaddress = dict_Environment_Variable["host_ip"]
port = dict_Environment_Variable["host_port"]

Google_Auth_For_Drive = GoogleAuth(
    dict_Environment_Variable["database_directory"]
    + dict_Environment_Variable["setting_yaml_google_drive_api"]
)
Google_Auth_For_Drive.LocalWebserverAuth()
Google_Auth_For_Drive.CommandLineAuth()

cmd = commandsForDiamond.CommandsDiamond(
    logger=logger, dict_Environment_Variable=dict_Environment_Variable
)
cmd.set_Google_Auth_For_Drive(Google_Auth_For_Drive)
# cmd.set_Google_Auth_For_Drive(None)

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/request", methods=["POST"])
def get_request():
    json_data = request.get_json()
    print()
    logger.info(json_data["command"])
    logger.info(json_data["identifier"])
    # logger.debug(json_data["args"])
    print()
    # print(json_data["identifier"])
    command = json_data["command"]
    args = json_data["args"]
    identifier = json_data["identifier"]
    # response_data = {}
    response = cmd.check_UsageID(command, args, identifier)
    if response is not None:
        return jsonify(response)

    response = cmd.finish_Experiment(command, args, identifier)
    if response is not None:
        return jsonify(response)

    # response = cmd.read_Use_Information_From_Shared_Excel(
    #     command, args, identifier)
    # if response is not None:
    #     return jsonify(response)

    # response = cmd.check_And_Get_Single_Proposal(command, args, identifier)
    # if response is not None:
    # return jsonify(response)

    response = cmd.start_Experiment(command, args, identifier)
    if response is not None:
        return jsonify(response)

    response = cmd.get_Meta_Data(command, args, identifier)
    if response is not None:
        return jsonify(response)

    response = cmd.Copy_From_Original_To_Share(command, args, identifier)
    if response is not None:
        return jsonify(response)

    return {
        "message": "Error: No such command",
        "command": command,
        "status": False,
        "identifier": identifier,
    }


@app.route("/test", methods=["POST"])
def test():
    x = 0
    for i in range(100):
        x = x + 1
    print(request.data)
    # json_data = request.get_json()
    print(x)
    json_data = {}
    json_data["status"] = True
    json_data["message"] = "Calculation OK"
    json_data["result"] = x
    print(json_data)
    return jsonify(json_data)


def runFlask(**kwargs):
    app.run(**kwargs)


if __name__ == "__main__":
    # processScheduleUpdate = Process(
    #     target=cmd.periodic_Update_From_Excel_Files(), args=())
    # print("Periodic update process start")
    # processScheduleUpdate.daemon = True
    # # print(get_Database())
    while True:
        try:
            app.run(host=ipaddress, port=port)
        except BaseException as e:
            logger.warning(e)
    # # app.run(host='163.221.235.207', port=5462)
    # app.run(host='192.168.11.40', port=5462)
    # processScheduleUpdate.start()
    # processScheduleUpdate.join()

    # processServer = Process(
    #     target=runFlask,
    #     kwargs={
    #         # 'host': '192.168.150.10',
    #         # 'port': 5462,
    #         'host': ipaddress,
    #         'port': port,
    #         'threaded': True
    #     })
    # processServer.start()
    # cmd = commandsForDiamond.CommandsDiamond()
    # cmd.periodic_Update_Spread_Sheet()
