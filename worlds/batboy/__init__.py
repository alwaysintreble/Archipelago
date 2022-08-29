from typing import List, Optional, Callable, Dict, Any
import worlds.AutoWorld as Auto
from BaseClasses import Tutorial, ItemClassification, Region, RegionType, Entrance

from .Constants.ItemsAndLocations import ABILITY_NAMES, LOCATION_NAMES, SHOP_NAMES
from .Constants.RegionConstants import LEVEL_TO_HINT_NAMES, CASETTE_ONLY_REGIONS

from .Items import BatBoyItem, item_name_to_id
from .Locations import BatBoyLocation, location_name_to_id
from .Options import batboy_options
from .Rules import LocationRules


class BatBoyWeb(Auto.WebWorld):
    tut_en = Tutorial(
        "setup",
        "Tutorial on setting up the batboy client for archipelago play.",
        "English",
        "setup_en.md",
        "setup_en",
        ["alwaysintreble"],
    )
    tutorials = [tut_en]
    theme = "grassFlowers"


class BatBoyWorld(Auto.World):
    """Help Ryosuke and his fellow sports-star friends battle against the evil invading forces of Lord Vicious to
    prevent them from hosting sinister athletic events for their own amusement as Bat Boy!"""
    web = BatBoyWeb()
    
    game: str = "BatBoy"
    option_definitions = batboy_options
    
    item_name_to_id = item_name_to_id()
    location_name_to_id = location_name_to_id()
    
    data_version = 0
    
    itempool: List[str]
    levels: List[Region]
    shops: List[str]
    overworld: Region
    location_rules: LocationRules
    all_locations: List[BatBoyLocation]

    def create_item(self, name: str) -> BatBoyItem:
        return BatBoyItem(name, 
                          ItemClassification.progression if name in ABILITY_NAMES or name == "Golden Seed"
                          else ItemClassification.useful if name == "Increase HP"
                          else ItemClassification.filler,
                          self.item_name_to_id[name], self.player)
    
    def create_items(self) -> None:
        level_count: int = len(LEVEL_TO_HINT_NAMES)  # each level has 1 red, green, and gold seed
        self.itempool = []

        # we always want one of every ability so do this first
        for ability in ABILITY_NAMES:
            self.itempool.append(ability)
            
        # may do this differently in the future and allow custom seed distributions
        for _ in range(level_count):
            self.itempool.append("Red Seed")
            self.itempool.append("Green Seed")
            self.itempool.append("Golden Seed")
            
        # since we only have a red seed shop currently we create the red seeds for it
        for slot in SHOP_NAMES:
            if slot != "Shop Consumable Item":
                self.itempool.append("Red Seed")
            else:
                self.itempool.append("Increase HP")
    
    def create_location(self, name: str, parent: Region, rule: Optional[Callable] = None) -> BatBoyLocation:
        loc = BatBoyLocation(self.player, name, self.location_name_to_id[name], parent)
        parent.locations.append(loc)
        if rule:
            loc.access_rule = rule
        return loc

    def create_levels_with_rules(self) -> None:
        self.levels: List[Region] = []
        self.all_locations = []
        level_rules = self.location_rules.level_rules
        location_rules = self.location_rules.location_rules

        for level_name in LEVEL_TO_HINT_NAMES:
            level: Region = self.create_region(level_name)
            connection: Entrance = Entrance(self.player, level_name, self.overworld)
            if level_name in level_rules:
                connection.access_rule = level_rules[level_name]
            connection.connect(level)
            self.overworld.exits.append(connection)
            for loc_name in LOCATION_NAMES:
                new_name = level_name + " " + loc_name
                rule = None
                if level_name not in {"Red Seed Shop", "Groovy House"}:
                    if new_name in location_rules:
                        rule = location_rules[new_name]
                    self.all_locations.append(self.create_location(new_name, level, rule))
            self.levels.append(level)

        for level_name in CASETTE_ONLY_REGIONS:
            level: Region = self.create_region(level_name)
            connection: Entrance = Entrance(self.player, level_name, self.overworld)
            connection.connect(level)
            self.overworld.exits.append(connection)
            new_name = level_name + " Casette"
            self.all_locations.append(self.create_location(new_name, level, None))

            self.levels.append(level)
    
    def create_shops(self) -> None:
        self.shops: List[Region] = []
        shop_rules = self.location_rules.shop_rules

        shop = self.create_region("Red Seed Shop")
        connection: Entrance = Entrance(self.player, "Red Seed Shop", self.overworld)
        connection.connect(shop)
        self.overworld.exits.append(connection)

        for loc in SHOP_NAMES:
            rule = None
            if loc in shop_rules:
                rule = shop_rules[loc]
            self.all_locations.append(self.create_location(loc, shop, rule))
        self.shops.append(shop)
        
    def create_region(self, name: str) -> Region:
        if name in LEVEL_TO_HINT_NAMES:
            return Region(name, RegionType.Generic, LEVEL_TO_HINT_NAMES[name], self.player, self.world)
        return Region(name, RegionType.Generic, name, self.player, self.world)
    
    def create_regions(self) -> None:
        # create and connect our menu and overworld regions before anything else
        menu = Region("Menu", RegionType.Generic, "Menu", self.player, self.world)
        self.overworld = Region("Overworld", RegionType.Generic, "Overworld", self.player, self.world)
        start = Entrance(self.player, "Game Start", menu)
        menu.exits.append(start)
        start.connect(self.overworld)

        # instantiate my LocationRules class before creating rules so we can easily reference its rules dicts
        self.location_rules = LocationRules(self.player)
        # create a region for each level and connect it to the overworld with rules
        self.create_levels_with_rules()
        self.create_shops()
        self.world.regions += [menu, self.overworld] + self.levels + self.shops

    def generate_basic(self) -> None:
        # place bat spin in the first level and remove it from the item pool
        possible_locs = [loc for loc in self.world.get_region("Grassy Plains", self.player).locations]
        possible_locs.remove(self.world.get_location("Grassy Plains Golden Seed", self.player))
        possible_locs.append(self.world.get_location("Shop Slot 1", self.player))
        loc = self.world.random.choice(possible_locs)

        loc.place_locked_item(self.create_item(self.itempool.pop(self.itempool.index("Bat Spin"))))

        # each level has 3 seeds, casette, and the level clear
        # each shop has 3 item slots and a consumable item slot
        # subtract 1 due to above item placement
        locations_len: int = len(self.all_locations) - 1

        # check if the itempool and number of locations are equal and if not make them equal with red seeds
        if len(self.itempool) < locations_len:
            while len(self.itempool) != locations_len:
                self.itempool.append("Red Seed")
        elif len(self.itempool) > locations_len:
            while len(self.itempool) != locations_len:
                self.itempool.remove("Red Seed")

        itempool = [self.create_item(item_name) for item_name in self.itempool]
        self.world.itempool += itempool

    def set_rules(self) -> None:
        self.world.completion_condition[self.player] = lambda state: state.has_all(ABILITY_NAMES, self.player)

    def fill_slot_data(self) -> Dict[str, Any]:
        return {
            "deathlink": self.world.death_link[self.player].value,
        }
