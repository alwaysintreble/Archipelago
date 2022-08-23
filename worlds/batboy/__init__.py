from typing import List, Dict, Optional, Callable
import worlds.AutoWorld as Auto
from BaseClasses import MultiWorld, Tutorial, ItemClassification, Region, RegionType, Entrance

from .Constants.ItemsAndLocations import ABILITY_NAMES, LOCATION_NAMES, SHOP_NAMES
from .Constants.RegionConstants import LEVEL_TO_HINT_NAMES

from .Items import BatBoyItem, item_name_to_id
from .Locations import BatBoyLocation, location_name_to_id
from .Options import batboy_options


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
    
    itempool: List[BatBoyItem]
    levels: List[str]
    shops: List[str]

    def create_item(self, name: str) -> BatBoyItem:
        return BatBoyItem(name, 
                          ItemClassification.progression if name in ABILITY_NAMES
                          else ItemClassification.useful if name == "Increase HP"
                          else ItemClassification.filler,
                          self.item_name_to_id[name], self.player)
    
    def create_items(self) -> None:
        level_count: int = len(LEVEL_TO_HINT_NAMES) # each level has 1 red, green, and gold seed
        self.itempool = []

        # we always want one of every ability so do this first
        for ability in ABILITY_NAMES:
            self.itempool.append(self.create_item(ability))
            
        # may do this differently in the future and allow custom seed distributions
        for _ in range(level_count):
            self.itempool.append(self.create_item("Red Seed"))
            self.itempool.append(self.create_item("Green Seed"))
            self.itempool.append(self.create_item("Golden Seed"))
            
        # since we only have a red seed shop currently we create the red seeds for it
        for slot in range(SHOP_NAMES):
            if slot != "Shop Consumable Item":
                self.itempool.append(self.create_item("Red Seed"))
        
        # add a single hp upgrade
        self.itempool.append(self.create_item("Increase HP"))
    
    def create_location(self, name: str, parent: Region, rule: Optional[Callable]) -> None:
        loc = BatBoyLocation(self.player, name, self.location_name_to_id[name], parent)
        parent.locations.append(loc)
        loc.access_rule = rule

    def create_levels_with_rules(self, overworld: Region) -> None:
        level_rules: Dict[str, Optional[Callable]] = {
            "Frozen Peak": self.world.state.has("Bat Spin", self.player),
            "Windy Forest": self.world.state.has("Bat Spin", self.player),
        }
        
        location_rules: Dict[str, Optional[Callable]] = {
            "Grassy Plains Golden Seed": self.world.state.has("Bat Spin", self.player) and
                                         self.world.state.has_any({"Slash Bash", "Grappling Ribbon", self.player)}),
        }
        
        self.levels: List[Region] = []
        
        for level_name in REGION_NAMES:
            level: Region = self.create_region(level_name)
            connection: Entrance = Entrance(self.player, level_name, overworld)
            if level_name in level_rules:
                connection.access_rule = level_rules[level_name]
            connection.connect(level)
            for loc_name in LOCATION_NAMES:
                new_name = level_name + " " + loc_name
                rule = None
                if new_name in location_rules:
                    rule = location_rules[new_name]
                self.create_location(new_name, level, rule)
            self.levels.append(level)
    
    def create_shops(self, overworld: Region) -> None:
        shop_rules: Dict[str, Optional[Callable]] = {
            
        }
        
        self.shops = []
        shop = self.create_region("Red Seed Shop")
        for loc in SHOP_NAMES:
            rule = None
            if loc == "Shop Consumable Item":
                rule = self.world.state.has("Red Seed", self.player, 3)
            self.create_location(loc, shop, rule)
        self.shops.append(shop)
        
    def create_region(self, name: str) -> Region:
        return Region(name, RegionType.Generic, LEVEL_TO_HINT_NAMES[name], self.player, self.world)
    
    def create_regions(self) -> None:
        # create and connect our menu and overworld regions before anything else
        menu = Region("Menu", RegionType.Generic, "Menu", self.player, self.world)
        overworld = Region("Overworld", RegionType.Generic, "Overworld", self.player, self.world)
        start = Entrance(self.player, "Game Start", menu)
        menu.exits.append(start)
        start.connect(overworld)
        
        # create a region for each level and connect it to the overworld with rules
        self.create_levels_with_rules(overworld)
        self.create_shops(overworld)
        self.world.regions += [menu, overworld, self.levels, self.shops]
    
    def set_rules(self) -> None:
        pass
        location_rules: Dict[str, Optional[Callable]] = {
            "Grassy Plains Golden Seed": self.world.state.has("Bat Spin", self.player) and 
                                         self.world.state.has_any({"Slash Bash", "Grappling Ribbon", self.player)}),
        }
        
        #for loc, rule in location_rules.items():
        #    self.world.get_location(loc).access_rule = rule
            
    
    def generate_early(self) -> None:
        loc = self.world.random.choice(self.world.get_region("Grassy Plains", self.player).locations)
        bat_spin = self.create_item("Bat Spin")
        loc.place_locked_item(self.itempool.pop(self.itempool.index(bat_spin)))
        
            
    def generate_basic(self) -> None:
        items_len: int = len(self.itempool)
        locations_len: int = 0
        for level in self.levels:
            for _ in level.locations:
                locations_len += 1
        for shop in self.shops:
            for _ in shop.locations:
                locations_len += 1
        if items_len < locations_len:
            while items_len != locations_len:
                self.itempool.append(self.create_item("Red Seed"))
                items_len += 1
        elif items_len > locations_len:
            while items_len != locations_len:
                self.itempool.remove(self.create_item("Red Seed"))
                items_len -= 1
        
        self.world.itempool += self.itempool
    