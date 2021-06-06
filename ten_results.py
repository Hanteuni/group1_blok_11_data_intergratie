import json
import httplib2 as http
from urllib.parse import urlparse
import tqdm
import time


json_file = {}


def file_reader(fname, variant_type):
    counter = 0
    type_dict = {}
    with open(fname, "r") as file:
        for line in file:
            variants = []
            if not line.startswith("#") and len(type_dict) < 10:
                info = line.split("\t")
                info_split = info[7].split("|")
                # print(info_split)
                if variant_type == "missense_variant":
                    indices = [i for i, x in enumerate(info_split) if x == "missense_variant"]
                if variant_type == "frame_shift_variant":
                    indices = [i for i, x in enumerate(info_split) if x == "missense_variant"]
                for index in indices:
                    variant = info_split[index + 8]
                    variants.append(variant)
                gene_name = info_split[3]
                type_dict[gene_name] = variants
    return type_dict


def write_to_json(missense_dict, frame_shift_dict,missense_name_dict, frame_shift_name_dict, person):
    json_file[person] = {
        "missense_variant": missense_dict,
        "missense_HGNC_name": missense_name_dict,
        "frame_shift_variant": frame_shift_dict,
        "frame_shift_HGNC_name": frame_shift_name_dict}


def json_writer():
    with open("data_intergratie_variants.json", "w+") as new_json:
        print("uploading the jason file... ")
        json.dump(json_file, new_json)
        print("file is done")


def get_HGNC_name(dict,name=""):
    name_dict = {}
    for variant in tqdm.tqdm(dict, total=len(dict), desc="Retrieving names from HGNC"):
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
        #
        if response['status'] == '200':
            data = json.loads(content)
            try:
                # print(
                #     'Name:' + data['response']['docs'][0]['name'])
                name_dict[variant] = data['response']['docs'][0]['name']
            except IndexError:
                name_dict[variant] = "NO HNGC NAME"
        else:
            print('Error detected: ' + response['status'])
    return name_dict


if __name__ == '__main__':
    participants = ["PGCP_0001","PGCP_0011","PGCP_0021"]
    for participant in participants:
        fname_missense = "{}_S1_ann.filter_missense_first.vcf".format(participant)
        fname_frame_shift = "{}_S1_ann.frameshift_variant_first.vcf".format(participant)
        missense_dict = file_reader(fname=fname_missense, variant_type="missense_variant")
        frame_shift_dict = file_reader(fname=fname_missense, variant_type="frame_shift_variant")
        missense_name_dict = get_HGNC_name(missense_dict,name="missense")
        frame_shift_name_dict = get_HGNC_name(frame_shift_dict,name="frame_shift")
        write_to_json(missense_dict,frame_shift_dict,missense_name_dict, frame_shift_name_dict, person=participant)
    json_writer()
