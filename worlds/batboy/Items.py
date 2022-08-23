from typing import Dict

from BaseClasses import Item

from .Constants.ItemsAndLocations import ITEM_NAMES, ABILITY_NAMES


class BatBoyItem(Item):
    game = "BatBoy"


base_offset = 696969
ability_offset = 20


def item_name_to_id() -> Dict[str, int]:
    items = {item_name: item_id for item_id, item_name in enumerate(ITEM_NAMES, base_offset)}
    abilities = {ability_name: ability_id
                 for ability_id, ability_name in enumerate(ABILITY_NAMES, (base_offset + ability_offset))}
    print(items | abilities)
    return items | abilities
