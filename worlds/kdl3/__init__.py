import logging

from BaseClasses import Tutorial, ItemClassification, MultiWorld
from worlds.AutoWorld import World, WebWorld
from .Items import item_table, item_names, copy_ability_table, animal_friend_table, filler_item_weights, KDL3Item
from .Locations import location_table, KDL3Location, level_consumables, consumable_locations
from .Regions import create_levels
from .Options import kdl3_options
from .Names import LocationName
from .Rules import set_rules
from .Rom import KDL3DeltaPatch, get_base_rom_path, RomData, patch_rom
from .Client import KDL3SNIClient

from typing import Dict
import os
import math
import threading
import base64

logger = logging.getLogger("Kirby's Dream Land 3")

class KDL3WebWorld(WebWorld):
    theme = "partyTime"
    tutorials = [

        # Tutorial(
        #    "Multiworld Setup Guide",
        #    "A guide to setting up the Kirby's Dream Land 3 randomizer connected to an Archipelago Multiworld.",
        #    "English",
        #    "setup_en.md",
        #    "setup/en",
        #    ["Silvris"]
        # )
    ]


class KDL3World(World):
    """
    Join Kirby and his Animal Friends on an adventure to collect Heart Stars and drive Dark Matter away from Dream Land!
    """

    game: str = "Kirby's Dream Land 3"
    option_definitions = kdl3_options
    item_name_to_id = {item: item_table[item].code for item in item_table}
    location_name_to_id = {location_table[location]: location for location in location_table}
    item_name_groups = item_names
    data_version = 0
    web = KDL3WebWorld()
    required_heart_stars = dict()
    boss_requirements = dict()
    player_levels = dict()
    topology_present = False

    def __init__(self, world: MultiWorld, player: int):
        self.rom_name_available_event = threading.Event()
        super().__init__(world, player)

    @classmethod
    def stage_assert_generate(cls, multiworld: MultiWorld) -> None:
        rom_file: str = get_base_rom_path()
        if not os.path.exists(rom_file):
            raise FileNotFoundError(f"Could not find base ROM for {cls.game}: {rom_file}")

    create_regions = create_levels

    def create_item(self, name: str, force_non_progression=False) -> KDL3Item:
        item = item_table[name]
        classification = ItemClassification.filler
        if item.progression and not force_non_progression:
            classification = ItemClassification.progression_skip_balancing \
                if item.skip_balancing else ItemClassification.progression
        return KDL3Item(name, classification, item.code, self.player)

    def get_filler_item_name(self) -> str:
        return self.multiworld.random.choices(list(filler_item_weights.keys()),
                                              weights=list(filler_item_weights.values()))[0]

    def generate_early(self) -> None:
        # just check for invalid option combos here
        if self.multiworld.strict_bosses[self.player] and self.multiworld.boss_requirement_random[self.player]:
            logger.warning(f"boss_requirement_random forced to false for player {self.player}" +
                           f" because of strict_bosses set to true")
            self.multiworld.boss_requirement_random[self.player].value = False

    def create_items(self) -> None:
        itempool = []
        itempool.extend([self.create_item(name) for name in copy_ability_table])
        itempool.extend([self.create_item(name) for name in animal_friend_table])
        required_percentage = self.multiworld.heart_stars_required[self.player].value / 100.0
        remaining_items = (len(location_table) if self.multiworld.consumables[self.player]
                           else len(location_table) - len(consumable_locations)) - len(itempool)
        total_heart_stars = self.multiworld.total_heart_stars[self.player].value
        required_heart_stars = max(math.floor(total_heart_stars * required_percentage),
                                   1)  # ensure at least 1 heart star required
        filler_items = total_heart_stars - required_heart_stars
        filler_amount = math.floor(filler_items * (self.multiworld.filler_percentage[self.player].value / 100.0))
        nonrequired_heart_stars = filler_items - filler_amount
        self.required_heart_stars[self.player] = required_heart_stars
        # handle boss requirements here
        requirements = [required_heart_stars]
        if self.multiworld.boss_requirement_random[self.player].value:
            for i in range(4):
                requirements.append(self.multiworld.per_slot_randoms[self.player].randint(
                    min(3, required_heart_stars), required_heart_stars))
            if self.multiworld.strict_bosses[self.player]:
                requirements.sort()
            else:
                self.multiworld.per_slot_randoms[self.player].shuffle(requirements)
        else:
            quotient = required_heart_stars // 5  # since we set the last manually, we can afford imperfect rounding
            for i in range(1, 5):
                requirements.insert(i - 1, quotient * i)
        self.boss_requirements[self.player] = requirements
        itempool.extend([self.create_item("Heart Star") for _ in range(required_heart_stars)])
        itempool.extend([self.create_item(self.get_filler_item_name())
                         for _ in range(filler_amount + (remaining_items - total_heart_stars))])
        itempool.extend([self.create_item("Heart Star", True) for _ in range(nonrequired_heart_stars)])
        self.multiworld.itempool += itempool

    set_rules = set_rules

    def generate_basic(self) -> None:
        self.topology_present = self.multiworld.stage_shuffle[self.player].value > 0
        goal = self.multiworld.goal[self.player].value
        goal_location = self.multiworld.get_location(LocationName.goals[goal], self.player)
        goal_location.place_locked_item(KDL3Item("Love-Love Rod", ItemClassification.progression, None, self.player))
        self.multiworld.get_location("Level 1 Boss", self.player) \
            .place_locked_item(KDL3Item("Level 1 Boss Purified", ItemClassification.progression, None, self.player))
        self.multiworld.get_location("Level 2 Boss", self.player) \
            .place_locked_item(KDL3Item("Level 2 Boss Purified", ItemClassification.progression, None, self.player))
        self.multiworld.get_location("Level 3 Boss", self.player) \
            .place_locked_item(KDL3Item("Level 3 Boss Purified", ItemClassification.progression, None, self.player))
        self.multiworld.get_location("Level 4 Boss", self.player) \
            .place_locked_item(KDL3Item("Level 4 Boss Purified", ItemClassification.progression, None, self.player))
        self.multiworld.get_location("Level 5 Boss", self.player) \
            .place_locked_item(KDL3Item("Level 5 Boss Purified", ItemClassification.progression, None, self.player))
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Love-Love Rod", self.player)

    def generate_output(self, output_directory: str):
        rompath = ""
        try:
            world = self.multiworld
            player = self.player

            rom = RomData(get_base_rom_path())
            patch_rom(self.multiworld, self.player, rom, self.required_heart_stars[self.player],
                      self.boss_requirements[self.player],
                      self.player_levels[self.player])

            rompath = os.path.join(output_directory, f"{self.multiworld.get_out_file_name_base(self.player)}.sfc")
            rom.write_to_file(rompath)
            self.rom_name = rom.name

            patch = KDL3DeltaPatch(os.path.splitext(rompath)[0] + KDL3DeltaPatch.patch_file_ending, player=player,
                                   player_name=world.player_name[player], patched_path=rompath)
            patch.write()
        except Exception:
            raise
        finally:
            self.rom_name_available_event.set()  # make sure threading continues and errors are collected
            if os.path.exists(rompath):
                os.unlink(rompath)

    def modify_multidata(self, multidata: dict):
        # wait for self.rom_name to be available.
        self.rom_name_available_event.wait()
        rom_name = getattr(self, "rom_name", None)
        # we skip in case of error, so that the original error in the output thread is the one that gets raised
        if rom_name:
            new_name = base64.b64encode(bytes(self.rom_name)).decode()
            multidata["connect_names"][new_name] = multidata["connect_names"][self.multiworld.player_name[self.player]]

    def extend_hint_information(self, hint_data: Dict[int, Dict[int, str]]):
        if self.topology_present:
            regions = {LocationName.level_names[level]: level for level in LocationName.level_names}
            level_hint_data = {}
            for level in self.player_levels[self.player]:
                for i in range(len(self.player_levels[self.player][level]) - 1):
                    stage = self.player_levels[self.player][level][i]
                    level_hint_data[stage] = regions[level] + f" {i + 1}"
                    if stage & 0x200 == 0:
                        level_hint_data[stage + 0x100] = regions[level] + f" {i + 1}"
                    if self.multiworld.consumables[self.player] and stage & 0xFF in level_consumables:
                        for consumable in level_consumables[stage & 0xFF]:
                            level_hint_data[consumable + 0x770300] = regions[level] + f" {i + 1}"
            for i in range(5):
                level_hint_data[0x770200 + i] = regions[i + 1] + " Boss"
            hint_data[self.player] = level_hint_data
