import json


def load_data(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Error loading JSON file: {error}")
        return None


def get_player_id(data):
    heroes_data = {}
    if "heroes" in data and "-1" in data["heroes"]:
        for hero_name, hero_info in data["heroes"]["-1"].items():
            player_id = hero_info.get("playerID")
            if player_id is not None:
                heroes_data[player_id] = {"hero_name": hero_name, "items": []}
    print(heroes_data)
    return heroes_data


def assign_items(data, heroes_data):
    if "items" in data:
        for tick, items_info in data["items"].items():
            for item_id, item_info in items_info.items():
                player_owner_id = item_info.get("playerOwnerID")
                if player_owner_id in heroes_data:
                    heroes_data[player_owner_id]["items"].append(
                        {"tick": int(tick), "item": item_info.get("name", None)}
                    )


def print_heroes_data(heroes_data):
    for player_id, hero_info in heroes_data.items():
        print(f"Hrdina: {hero_info['hero_name']} (PlayerID: {player_id})")
        for item_entry in sorted(hero_info["items"], key=lambda x: x["tick"]):
            print(f"  Tick {item_entry['tick']}: {item_entry['item']}")
        print("-" * 40)


def main():
    data = load_data("8182713861_1523041035_combined_log.json")
    if data is None:
        return

    heroes_data = get_player_id(data)
    assign_items(data, heroes_data)
    print_heroes_data(heroes_data)


if __name__ == "__main__":
    main()
