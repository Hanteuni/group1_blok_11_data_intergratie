import json
import boto3

json_file = {}


def file_reader(fname, variant_type):
    counter = 0
    type_dict = {}
    with open(fname,"r") as file:
        for line in file:
            variants = []
            if not line.startswith("#") and counter < 11:
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


def write_to_json(missense_dict, frame_shift_dict, person):
    json_file[person] = {
    "missense_variant": missense_dict,
    "frame_shift_variant": frame_shift_dict }


def json_writer():
    with open("data_intergratie_variants.json", "w+") as new_json:
        print("uploading the jason file... ")
        json.dump(json_file, new_json)
        print("file is done")


def athena_search(missense_dict):
    pass

if __name__ == '__main__':
        fname_missense = "PGCP_0001_S1_ann.filter_missense_first.vcf"
        missense_dict = file_reader(fname=fname_missense, variant_type="missense_variant")
        athena_search(missense_dict)
    # participants = ["PGCP_0001","PGCP_0011","PGCP_0021"]
    # for participant in participants:
    #     fname_missense = "{}_S1_ann.filter_missense_first.vcf".format(participant)
    #     fname_frame_shift = "{}_S1_ann.frameshift_variant_first.vcf".format(participant)
    #     missense_dict = file_reader(fname=fname_missense, variant_type="missense_variant")
    #     frame_shift_dict = file_reader(fname=fname_missense, variant_type="frame_shift_variant")
    #     write_to_json(missense_dict,frame_shift_dict,person=participant)
    # json_writer()




