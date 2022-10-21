﻿from typing import Dict, List
from BaseClasses import Location

from .Constants.RegionConstants import LEVEL_TO_HINT_NAMES, CASSETTE_ONLY_REGIONS
from .Constants.ItemsAndLocations import LOCATION_NAMES, SHOP_NAMES


class BatBoyLocation(Location):
    game = "BatBoy"


base_offset = 696969
cassette_offset = 100
shop_offset = 200


def location_name_to_id() -> Dict[str, int]:
    loc_names: List[str] = [f"{region_name} {loc_name}"
                            for region_name in LEVEL_TO_HINT_NAMES
                            for loc_name in LOCATION_NAMES]

    loc_map: Dict[str, int] = {loc_name: loc_id for loc_id, loc_name in enumerate(loc_names, base_offset)}

    # the demo only has a single shop so this is pseudo hard coded until i find a better way to handle shops
    shop_map: Dict[str, int] = {shop_slot: shop_id
                                for shop_id, shop_slot in enumerate(SHOP_NAMES, (base_offset + shop_offset))}
    cassette_map: Dict[str, int] = {f"{level_name} Cassette": loc_id
                                    for loc_id, level_name in
                                    enumerate(CASSETTE_ONLY_REGIONS, base_offset + cassette_offset)}
    return loc_map | shop_map | cassette_map
