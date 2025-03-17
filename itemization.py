import json
from collections import defaultdict
import re

#saves itemization into txt and json files
def load_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found!")
        return None
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from file {file_path}")
        return None


def clean_item_name(item_name):
    return re.sub(r"CDOTA_Item_|(\(\d+\).*)", "", item_name)


def list_player_items(
    data, output_txt="itemization.txt", output_json="itemization.json"
):
    hero_items = defaultdict(list)

    for hero_data in data.values():
        hero_name = hero_data["hero_name"].replace("CDOTA_Unit_Hero_", "")
        for item in hero_data["items"].values():
            item_name = clean_item_name(item["name"])  # .replace("CDOTA_Item_", "")
            for event in item["history"]:
                if event["status"] == "purchased":
                    minute = int(event["tick"]) // 60
                    hero_items[hero_name].append((minute, item_name))

    output = []
    for hero, items in hero_items.items():
        items.sort()
        grouped_items = defaultdict(list)
        for minute, item in items:
            grouped_items[minute].append(item)

        hero_data = {"hero": hero, "items": []}
        for minute, item_names in grouped_items.items():
            hero_data["items"].append({"minute": minute, "items": item_names})
        output.append(hero_data)

    formatted_output = ""
    for hero_data in output:
        formatted_output += f"\n {hero_data['hero']}: "
        item_strings = []
        for item_info in hero_data["items"]:
            item_strings.append(
                f"\n min {item_info['minute']} > {', '.join(item_info['items'])}"
            )
        formatted_output += " ".join(item_strings) + "\n"

#    print(formatted_output)

    with open(output_txt, "w") as f:
        f.write(formatted_output)
    with open(output_json, "w") as f:
        json.dump(output, f, indent=1)

    print(f"Data written to {output_txt}")


def main():
    try:
        data = load_data("item_output.json")
        if data is None:
            print("Failed to load data file.")
            return
        list_player_items(data)
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
