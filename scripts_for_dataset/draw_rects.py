import json
import cv2
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True, type=str, help="Path to images file")
    parser.add_argument("-m", required=True, type=str, help="Path to markup file")
    parser.add_argument("-s", required=True, type=str, help="Path to save images with boxes")
    args = parser.parse_args()

    images_path = args.i + "/"
    markup_path = args.m
    to_save_path = args.s + "/"

    with open(markup_path, "r") as f:
        data = json.load(f)
    
    type_names = dict()
    colors = [(0, 165, 255), (0, 165, 255), (125, 125, 125)]
    for type_value in data["types_list"]:
        type_names[type_value["id"]] = type_value["name"]

    for value in data["objects"]:
        image_name = value["image"]
        image = cv2.imread(images_path + image_name)
        markup = value["markup"]
        for markup_value in markup:
            bbox = markup_value["bbox"]
            type_id = markup_value["type"]
            color_id = min(2, int(type_id))
            image = cv2.rectangle(image, (bbox[0], bbox[1]), \
                (bbox[0] + bbox[2], bbox[1] + bbox[3]), colors[color_id], 5)
            cv2.putText(image, type_names[type_id], (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, min(bbox[2], bbox[3])/100, colors[color_id], int(min(bbox[2], bbox[3])/50))
            image_name = image_name.replace("/", "_")
            cv2.imwrite(to_save_path + image_name, image)

