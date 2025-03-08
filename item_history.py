import json


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


def get_player_id(data):
    heroes_data = {}

    if "heroes" in data and "-1" in data.get("heroes", {}):
        for hero_name, hero_info in data["heroes"]["-1"].items():
            player_id = hero_info.get("playerID")
            if player_id is not None:
                heroes_data[player_id] = {"hero_name": hero_name, "items": {}}
    return heroes_data


def assign_items(data, heroes_data):
    if "items" in data:
        items_data = data["items"]
        for tick, items_info in items_data.items():
            for item_id, item_info in items_info.items():
                player_owner_id = item_info.get("playerOwnerID")
                if player_owner_id in heroes_data:
                    hero = heroes_data[player_owner_id]
                    if str(item_id) not in hero["items"]:
                        hero["items"][item_id] = {
                            "name": item_info.get("name", "INCORRECT INFO - CHECK"),
                            "history": [],
                        }
                    if "deleted" in item_info:
                        status = "deleted"
                    else:
                        status = "purchased"

                    hero["items"][item_id]["history"].append(
                        {"tick": tick, "status": status}
                    )


def print_heroes_data(heroes_data, output_file="item_output.json"):
    output_data = {}
    for player_id, hero_info in heroes_data.items():
        print(f"Hero: {hero_info['hero_name']} (PlayerID: {player_id})")
        output_data[player_id] = {
            "hero_name": hero_info["hero_name"],
            "items": {},
        }
        items = hero_info["items"]

        if not items:
            print("  No items purchased")
            output_data[player_id][:"items"] = "No items purchased"
            continue

        for item_id, item_data in items.items():
            #            print(f"  Item {item_id}: {item_data['name']}")
            output_data[player_id]["items"][item_id] = {
                "name": item_data["name"],
                "history": [],
            }
            history_sorted = sorted(item_data["history"], key=lambda x: x["tick"])

            if not history_sorted:
                #                print("  No history recorded")
                output_data[player_id]["items"][item_id]["history"] = (
                    "No history recorded"
                )
                continue

            for entry in history_sorted:
                #                print(f"    Tick {entry['tick']}: {entry['status']}")
                output_data[player_id]["items"][item_id]["history"].append(
                    {"tick": entry["tick"], "status": entry["status"]}
                )

    #        print("-" * 40)
    with open(output_file, "w") as f:
        json.dump(output_data, f, indent=1)

    print(f"Data written to {output_file}")


def main():
    try:
        data = load_data("8188745568_1293535117_combined_log.json")
        if data is None:
            print("Failed to load data file.")
            return

        heroes_data = get_player_id(data)
        assign_items(data, heroes_data)

        if not heroes_data:
            print("No hero data found in the log.")
        else:
            print_heroes_data(heroes_data)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
