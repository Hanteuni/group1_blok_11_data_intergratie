import json
import httplib2 as http
from urllib.parse import urlparse
import tqdm
import time
import sys

json_file = {}


def file_reader(fname, variant_type):
    """Reads and parses the variant file in the first on the first ten annotations.
    On what it filters depends on the variant type as paramater, which is either frame_shift
    or missense
    :param fname: the path to the annotated filter variant file
    :param variant_type: either missense or frame_shift
    :return:
    """
    type_dict = {}
    with open(fname, "r") as file:
        for line in file:
            variants = []
            # len(type_dict) is there to ensure there are only 10 results
            if not line.startswith("#") and len(type_dict) < 10:
                info = line.split("\t")
                # info[7] contains the annotation string
                info_split = info[7].split("|")
                # checks which variant it has and goes through the annotation where the missense is
                if variant_type == "missense_variant":
                    indices = [i for i, x in enumerate(info_split) if x == "missense_variant"]
                if variant_type == "frame_shift_variant":
                    indices = [i for i, x in enumerate(info_split) if x == "frame_shift_variant"]
                # pares the info from the variant string
                for index in indices:
                    # the variant is always 8 indexes further from the wordt missense/frame_shift_variant
                    variant = info_split[index + 8]
                    variants.append(variant)
                gene_name = info_split[3]
                type_dict[gene_name] = variants
    return type_dict


def write_to_json(missense_dict, frame_shift_dict, missense_name_dict, frame_shift_name_dict, person):
    """Writes both the missense and frame_shift dictionaries to a single formatted .json files.
    :param missense_dict: Dictionarie with all the missense variants from the filtered annotation file
    :param frame_shift_dict: Dictionarie with all the frame_shift variants from the filtered annotation file
    :param missense_name_dict: Dictonary containing all the HNGC names of the missense variants
    :param frame_shift_name_dict: Dictonary containing all the HNGC names of the missense variants
    :param person: To which PGCP person all the annotion belongs
    :return: A dictionary that contains all 4 of the dictionaries
    """
    json_file[person] = {
        "missense_variant": missense_dict,
        "missense_HGNC_name": missense_name_dict,
        "frame_shift_variant": frame_shift_dict,
        "frame_shift_HGNC_name": frame_shift_name_dict}


def json_writer():
    """"Writes the json dictonary that was created in the write_to_json fuction to a local file
    """
    with open("data_intergratie_variants_test.json", "w+") as new_json:
        print("uploading the jason file... ")
        json.dump(json_file, new_json)
        print("file is done")


def get_HGNC_name(variant_dict):
    """ For every variant name, the full out name of the variant is retrieved from the HNGC database.
    If a name is not in the HNGC database it will return a NO HNGC NAME as name
    :param variant_dict: The dictonary created in file_reader containing
    :return: a dictonary with the HNGC names
    """
    name_dict = {}
    for variant in tqdm.tqdm(variant_dict, total=len(variant_dict), desc="Retrieving names from HGNC"):
        # a time.sleep to prevent from getting kicked from HNGC server
        time.sleep(3)
        headers = {
            'Accept': 'application/json',
        }
        uri = 'http://rest.genenames.org'
        path = '/fetch/symbol/{}'.format(variant)
        target = urlparse(uri + path)
        method = 'GET'
        body = ''
        h = http.Http()
        response, content = h.request(
            target.geturl(),
            method,
            body,
            headers)
        # Making sure there isn't any connection issues
        if response['status'] == '200':
            data = json.loads(content)
            try:
                name_dict[variant] = data['response']['docs'][0]['name']
            except IndexError:
                name_dict[variant] = "NO HNGC NAME"
        else:
            print('Error detected: ' + response['status'])
    return name_dict


def main(missense_file, frame_shift_file, person):
    missense_dict = file_reader(fname=missense_file, variant_type="missense_variant")
    frame_shift_dict = file_reader(fname=frame_shift_file, variant_type="frame_shift_variant")
    missense_name_dict = get_HGNC_name(missense_dict)
    frame_shift_name_dict = get_HGNC_name(frame_shift_dict)
    write_to_json(missense_dict, frame_shift_dict, missense_name_dict, frame_shift_name_dict, person=person)
    json_writer()


if __name__ == '__main__':
    """
    System argv: missense annation filepath, frame shift annotion filepath, json_key/PGCP-person name
    """
    if len(sys.argv) < 4:
        print("missing arguments; need missense annotation; frame_shift annotation and person\n"
              "exiting now...")
        exit()
    main(sys.argv[1], sys.argv[2], sys.argv[3])
