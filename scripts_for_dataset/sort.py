import json
import shutil
from copy import copy
import argparse

def fix_markup_for_present_image(image_info, dir_name, names_translation, markups):
    image_name = image_info["image"].partition(".rf.")[0]
    current_index_name = names_translation["translation"][image_name].split("/")[-1]
    image_info["image"] = current_index_name
    index = 0
    for exist_markup in markups[dir_name]["objects"]:
        if exist_markup["image"] == current_index_name:
            break
        index += 1
    markups[dir_name]["objects"][index] = image_info
    
    index = 0
    for exist_markup in markups[""]["objects"]:
        if exist_markup["image"] == dir_name + "/" + current_index_name:
            break
        index += 1
    image_info_level_up = copy(image_info)
    image_info_level_up["image"] = dir_name + "/" + image_info_level_up["image"]
    markups[""]["objects"][index] = image_info_level_up

def insert_new_value_in_markup(image_info, dir_name, names_translation, markups):
    image_name = image_info["image"]
    current_index = names_translation["dirs_info"][dir_name]
    names_translation["dirs_info"][dir_name] += 1
    image_format = image_name.split('.')[-1]
    image_info["image"] = f'{current_index:05}.{image_format}'
    names_translation["translation"][image_name.partition(".rf.")[0]] = \
        dir_name + "/" + image_info["image"]
    markups[dir_name]["objects"].append(image_info)
    image_info_level_up = copy(image_info)
    image_info_level_up["image"] = dir_name + "/" + image_info_level_up["image"]
    markups[""]["objects"].append(image_info_level_up)
    shutil.copyfile(images_path + image_name, dataset_path + image_info_level_up["image"])    

def insert_in_markup(image_info, dir_name, names_translation, markups):
    image_name = image_info["image"]
    if image_name.partition(".rf.")[0] in names_translation["translation"]:
        fix_markup_for_present_image(image_info, dir_name, names_translation, markups)
    else:
        insert_new_value_in_markup(image_info, dir_name, names_translation, markups)

def define_folder(qr_counter, dm_counter, atypical_counter):
    if dm_counter != 0 and qr_counter != 0:
        return True, "dm_qr"
    elif dm_counter == 0 and qr_counter == 1:
        return True, "qr_1"
    elif dm_counter == 0 and qr_counter > 1:
        return True, "qr_many"
    elif dm_counter == 1 and qr_counter == 0:
        return True, "dm_1"
    elif dm_counter > 1 and qr_counter == 0:  
        return True, "dm_many"  
    elif atypical_counter != 0:
        return True, "atypical"
    else:
        return False, ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True, type=str, help="Path to images folder")
    parser.add_argument("-m", required=True, type=str, help="Path to markup file")
    parser.add_argument("-d", required=True, type=str, help="Path to dataset folder")
    parser.add_argument("-n", required=True, type=str, help="Path to names translation path")
    args = parser.parse_args()

    images_path = args.i + "/"
    markup_path = args.m
    dataset_path = args.d + "/"
    names_translation_path = args.n

    with open(names_translation_path, "r") as f:
        names_translation = json.load(f)

    dirs = ["qr_1", "qr_many", "dm_1", "dm_many", "dm_qr", "atypical", ""]
    markups = dict()

    for dir_ in dirs:
        with open(dataset_path + dir_ + "/markup.json", "r") as f:
            data = json.load(f)
            markups[dir_] = data

    with open(markup_path, "r") as f:
        data = json.load(f)

    for image_info in data["objects"]:
        image_name = image_info["image"]
        qr_counter = 0
        dm_counter = 0
        atypical_counter = 0
        for bbox in image_info["markup"]:
            if bbox["type"] == 0:
                qr_counter += 1
            elif bbox["type"] == 1:
                dm_counter += 1
            else:
                atypical_counter += 1

        success, dir_to_save = define_folder(qr_counter, dm_counter, atypical_counter)
        if not success:
            assert(f'Error, please check markup for {image_name}')
        insert_in_markup(image_info, dir_to_save, names_translation, markups)

    with open(names_translation_path, "w") as f:
        json.dump(names_translation, f, indent=2)

    for dir_ in dirs:
        data = markups[dir_]
        with open(dataset_path + dir_ + "/markup.json", "w") as f:
            json.dump(data, f, indent=2)