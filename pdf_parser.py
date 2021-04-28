from tika import parser
import json


def file_reader(fname, json_file):
    parsed_pdf = parser.from_file(fname)
    actual_data = []
    data = parsed_pdf['content']
    temp_ls = data.split("\n")
    for item in temp_ls:
        if item != "":
            actual_data.append(item)
    profile_feature = actual_data[2].split(" ")
    conditions_and_symptoms = actual_data[5].split(" ")
    json_file[profile_feature[0]] = {
        "Profile": {
          "birth_year": profile_feature[2],
          "birth_month": profile_feature[1],
          "Sex": profile_feature[3],
          "Ethnicity": profile_feature[4]
        },
      "Conditions_or_symptoms": conditions_and_symptoms[1:]
      }

    return json_file


def file_to_json(json_file):
    with open("data_intergratie.json", "w+") as new_json:
        print("uploading the jason file... ")
        json.dump(json_file, new_json)
        print("file is done")
    print(json_file)


if __name__ == '__main__':
    json_file = {}
    file_names = ["PGPC-1.pdf","PGPC-11.pdf","PGPC-21.pdf"]
    for file_name in file_names:
        json_file =file_reader(fname=file_name, json_file=json_file)
    file_to_json(json_file)

