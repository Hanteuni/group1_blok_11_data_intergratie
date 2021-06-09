import sys
import json
from tika import parser


def file_reader(fname, json_file_annotation):
    """Reads in the pdf file using the tika libary, and converts it to a .json structered dictionairy
    :param fname: path to the PGCP person pdf
    :param json_file_annotation: .JSON formatted dictionary
    :return: .json formatted dictionary containing the pdf data
    """
    parsed_pdf = parser.from_file(fname)
    actual_data = []
    data = parsed_pdf['content']
    temp_ls = data.split("\n")
    for item in temp_ls:
        # checks wether the pdf item isn't empty
        if item != "":
            actual_data.append(item)
    profile_feature = actual_data[2].split(" ")
    conditions_and_symptoms = actual_data[5].split(" ")
    json_file_annotation[profile_feature[0]] = {
        "Profile": {
            "birth_year": profile_feature[2],
            "birth_month": profile_feature[1],
            "Sex": profile_feature[3],
            "Ethnicity": profile_feature[4]
        },
        "Conditions_or_symptoms": conditions_and_symptoms[1:]
    }

    return json_file


def file_to_json(json_file_dict):
    """Write the .json formatted dictonary to a .json file.
    :param json_file_dict: .json formatted dictonairy
    :return: a local .json file
    """
    with open(sys.argv[2], "w+") as new_json:
        print("uploading the jason file... ")
        json.dump(json_file_dict, new_json)
        print("file is done")



if __name__ == '__main__':
    json_file = {}
    json_file =file_reader(fname=sys.argv[1], json_file_annotation=json_file)
    file_to_json(json_file)
