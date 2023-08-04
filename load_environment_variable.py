import json


def load_environment_variable() -> dict:
    path_of_environment_valuable_json = "C:/Program Files/diamond/environment_variable.json"
    #path_of_environment_valuable_json = "./environment_variable-copy2.json"
    dict_Environment_Variable = json.load(
        open(path_of_environment_valuable_json, mode="r", encoding='utf-8'))
    return dict_Environment_Variable
