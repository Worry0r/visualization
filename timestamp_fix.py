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


def get_combatlog_end(data):
    forts = ["npc_dota_goodguys_fort", "npc_dota_badguys_fort"]
    combatlog = data.get("combatLog", {})

    for tick_str, events in combatlog.items():
        combatlog_tick = int(tick_str)
        death_events = events.get("DOTA_COMBATLOG_DEATH", [])

        for event in death_events:
            target = event.get("target")
            if target in forts:
                return combatlog_tick

    return None


def get_buildings_end(data):
    buildings = data.get("buildings", {})
    fort_entity_ids = set()

    for tick_str, tick_data in buildings.items():
        for entity_id_str, entity_data in tick_data.items():
            building_type = entity_data.get("buildingType", "")
            if building_type.startswith("CDOTA_BaseNPC_Fort"):
                fort_entity_ids.add(int(entity_id_str))

    destruction_tick = {}

    for tick_str, tick_data in buildings.items():
        tick = int(tick_str)
        for entity_id_str, entity_data in tick_data.items():
            entity_id = int(entity_id_str)
            if entity_id in fort_entity_ids:
                if isinstance(entity_data, dict) and entity_data.get("deleted") is True:
                    destruction_tick[entity_id] = tick

    return destruction_tick


def offset_combatlog(data, combatlog_end_tick, buildings_end_tick, output_file):
    if buildings_end_tick is None or combatlog_end_tick is None:
        print("No end ticks found, cannot offset combat log.")
        return

    building_end_tick = min(buildings_end_tick.values())

    offset = building_end_tick - combatlog_end_tick
    print(
        f"Offset to apply: {offset} (building_end: {building_end_tick} - combatlog_end: {combatlog_end_tick})"
    )

    if offset == 0:
        print("No offset needed.")
        return

    combatlog = data.get("combatLog", {})
    new_combatlog = {}

    for tick_str, events in combatlog.items():
        original_tick = int(tick_str)
        new_tick = original_tick + offset
        new_combatlog[str(new_tick)] = events

    new_data = data.copy()
    new_data["combatLog"] = new_combatlog

    try:
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(new_data, outfile, indent=1)
        print(f"Offset combatLog saved to {output_file}")
    except Exception as e:
        print(f"Failed to save new JSON: {str(e)}")


def main():
    try:
        game_id = "8182713861_1523041035"
        file_name = "_combined_log.json"
        new_file = "_updated_log.json"

        data = load_data(str(game_id) + str(file_name))
        new_data_path = str(game_id) + str(new_file)

        if data is None:
            print("Failed to load data file.")
            return

        combat_log_end_tick = get_combatlog_end(data)
        buildings_end_tick = get_buildings_end(data)

        if combat_log_end_tick is None or buildings_end_tick is None:
            print("Error: Could not find end ticks.")
            return

        offset_combatlog(data, combat_log_end_tick, buildings_end_tick, new_data_path)

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
