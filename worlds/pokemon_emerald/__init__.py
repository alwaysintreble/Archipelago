"""
Archipelago World definition for Pokemon Emerald Version
"""
import copy
import hashlib
import os
from typing import Set, List, Optional, Tuple

from BaseClasses import ItemClassification, MultiWorld, Tutorial, Counter
from Fill import fill_restrictive
from Options import Toggle
from worlds.AutoWorld import WebWorld, World

from .data import PokemonEmeraldData, MapData, SpeciesData, EncounterTableData, LearnsetMove, TrainerData, TrainerPartyData, TrainerPokemonData, data as emerald_data
from .items import PokemonEmeraldItem, create_item_label_to_code_map, get_item_classification, offset_item_value, create_item_groups
from .locations import PokemonEmeraldLocation, create_location_label_to_id_map, create_locations_with_tags
from .options import RandomizeWildPokemon, RandomizeBadges, RandomizeTrainerParties, RandomizeHms, RandomizeStarters, LevelUpMoves, Abilities, ItemPoolType, TmCompatibility, HmCompatibility, get_option_value, option_definitions
from .pokemon import get_random_species, get_species_by_name, get_random_move, get_random_damaging_move, get_random_type
from .regions import create_regions
from .rom import PokemonEmeraldDeltaPatch, generate_output, get_base_rom_path
from .rules import (set_default_rules, set_overworld_item_rules, set_hidden_item_rules, set_npc_gift_rules,
    set_enable_ferry_rules, add_hidden_item_itemfinder_rules, add_flash_rules)
from .sanity_check import sanity_check
from .util import int_to_bool_array, bool_array_to_int


class PokemonEmeraldWebWorld(WebWorld):
    """
    Webhost info for Pokemon Emerald
    """
    theme = "ocean"
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to playing Pokémon Emerald with Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Zunawe"]
    )

    tutorials = [setup_en]


class PokemonEmeraldWorld(World):
    """
    Pokémon Emerald is the definitive gen 3 Pokémon game and one of the most beloved in the franchise.
    Catch, train, and battle Pokémon, explore the Hoenn region, and thwart the plots
    of Team Magma and Team Aqua, challenge gyms, and become the Pokémon champion!
    """
    game = "Pokemon Emerald"
    web = PokemonEmeraldWebWorld()
    option_definitions = option_definitions
    topology_present = True

    item_name_to_id = create_item_label_to_code_map()
    location_name_to_id = create_location_label_to_id_map()
    item_name_groups = create_item_groups()

    data_version = 0

    badge_shuffle_info: Optional[List[Tuple[PokemonEmeraldLocation, PokemonEmeraldItem]]] = None
    hm_shuffle_info: Optional[List[Tuple[PokemonEmeraldLocation, PokemonEmeraldItem]]] = None
    modified_data: PokemonEmeraldData

    def _get_pokemon_emerald_data(self):
        return {
            'world_seed': self.multiworld.per_slot_randoms[self.player].getrandbits(32),
            'seed_name': self.multiworld.seed_name,
            'player_name': self.multiworld.get_player_name(self.player),
            'player_id': self.player,
            'race': self.multiworld.is_race,
        }


    @classmethod
    def stage_assert_generate(cls, multiworld: MultiWorld):
        rom_path = get_base_rom_path()
        if not os.path.exists(rom_path):
            raise FileNotFoundError(rom_path)

        with open(rom_path, "rb") as infile:
            local_hash = hashlib.md5()
            local_hash.update(bytes(infile.read()))

            if local_hash.hexdigest() != PokemonEmeraldDeltaPatch.hash:
                raise AssertionError("Base ROM for Pokemon Emerald does not match expected hash. Please get Pokemon Emerald Version (USA, Europe) and dump it.")

        if sanity_check() is False:
            raise AssertionError("Pokemon Emerald sanity check failed. See log for details.")


    def create_regions(self):
        overworld_items_option = get_option_value(self.multiworld, self.player, "overworld_items")
        hidden_items_option = get_option_value(self.multiworld, self.player, "hidden_items")
        npc_gifts_option = get_option_value(self.multiworld, self.player, "npc_gifts")
        enable_ferry_option = get_option_value(self.multiworld, self.player, "enable_ferry")

        tags = set(["Badge", "HM", "KeyItem", "Rod", "Bike"])
        if overworld_items_option == Toggle.option_true:
            tags.add("OverworldItem")
        if hidden_items_option == Toggle.option_true:
            tags.add("HiddenItem")
        if npc_gifts_option == Toggle.option_true:
            tags.add("NpcGift")
        if enable_ferry_option == Toggle.option_true:
            tags.add("Ferry")

        create_regions(self.multiworld, self.player)
        create_locations_with_tags(self.multiworld, self.player, tags)


    def create_items(self):
        badges_option = get_option_value(self.multiworld, self.player, "badges")
        hms_option = get_option_value(self.multiworld, self.player, "hms")
        key_items_option = get_option_value(self.multiworld, self.player, "key_items")
        rods_option = get_option_value(self.multiworld, self.player, "rods")
        bikes_option = get_option_value(self.multiworld, self.player, "bikes")
        item_pool_type_option = get_option_value(self.multiworld, self.player, "item_pool_type")

        item_locations: List[PokemonEmeraldLocation] = []
        for region in self.multiworld.regions:
            if region.player == self.player:
                item_locations += [location for location in region.locations]

        # Filter events
        item_locations = [location for location in item_locations if not location.is_event]

        # Filter progression items which shouldn't be shuffled into the itempool. Their locations
        # still exist, but event items will be placed and locked at their vanilla locations instead.
        filter_tags = set()

        if key_items_option == Toggle.option_false:
            filter_tags.add("KeyItem")
        if rods_option == Toggle.option_false:
            filter_tags.add("Rod")
        if bikes_option == Toggle.option_false:
            filter_tags.add("Bike")

        if badges_option in [RandomizeBadges.option_vanilla]:
            filter_tags.add("Badge")
        if hms_option in [RandomizeHms.option_vanilla]:
            filter_tags.add("HM")

        if badges_option == RandomizeBadges.option_shuffle:
            self.badge_shuffle_info = [(location, self.create_item_by_code(location.default_item_code)) for location in
                [location for location in item_locations if "Badge" in location.tags]]
        if hms_option == RandomizeHms.option_shuffle:
            self.hm_shuffle_info = [(location, self.create_item_by_code(location.default_item_code)) for location in
                [location for location in item_locations if "HM" in location.tags]]

        item_locations = [location for location in item_locations if len(filter_tags & location.tags) == 0]
        default_itempool = [self.create_item_by_code(location.default_item_code) for location in item_locations]

        if item_pool_type_option == ItemPoolType.option_shuffled:
            self.multiworld.itempool += default_itempool

        elif item_pool_type_option in [ItemPoolType.option_diverse, ItemPoolType.option_diverse_balanced]:
            item_categories = ["Ball", "Heal", "Vitamin", "EvoStone", "Money", "TM", "Held", "Misc"]

            # Count occurrences of types of vanilla items in pool
            item_category_counter = Counter()
            for item in default_itempool:
                if item.classification != ItemClassification.progression:
                    item_category_counter.update([tag for tag in item.tags if tag in item_categories])

            item_category_weights = [item_category_counter.get(category) for category in item_categories]
            item_category_weights = [weight if weight is not None else 0 for weight in item_category_weights]

            # Create lists of item codes that can be used to fill
            fill_item_candidates = [item for item in emerald_data.items.values()]

            fill_item_candidates = [item for item in fill_item_candidates if "Unique" not in item.tags]

            fill_item_candidates_by_category = {category: [] for category in item_categories}
            for item in fill_item_candidates:
                for category in item_categories:
                    if category in item.tags:
                        fill_item_candidates_by_category[category].append(offset_item_value(item.item_id))

            for category in fill_item_candidates_by_category:
                fill_item_candidates_by_category[category].sort()

            # Ignore vanilla occurrences and pick completely randomly
            if item_pool_type_option == ItemPoolType.option_diverse:
                item_category_weights = [len(category_list) for category_list in fill_item_candidates_by_category.values()]

            # TMs should not have duplicates until every TM has been used already
            all_tm_choices = fill_item_candidates_by_category["TM"].copy()
            def refresh_tm_choices():
                fill_item_candidates_by_category["TM"] = all_tm_choices.copy()
                self.multiworld.random.shuffle(fill_item_candidates_by_category["TM"])

            # Create items
            for item in default_itempool:
                if item.classification != ItemClassification.progression:
                    category = self.multiworld.random.choices(item_categories, item_category_weights)[0]
                    if category == "TM":
                        if len(fill_item_candidates_by_category["TM"]) == 0:
                            refresh_tm_choices()
                        item_code = fill_item_candidates_by_category["TM"].pop()
                    else:
                        item_code = self.multiworld.random.choice(fill_item_candidates_by_category[category])
                    item = self.create_item_by_code(item_code)

                self.multiworld.itempool.append(item)


    def set_rules(self):
        set_default_rules(self.multiworld, self.player)

        if get_option_value(self.multiworld, self.player, "overworld_items") == Toggle.option_true:
            set_overworld_item_rules(self.multiworld, self.player)
        if get_option_value(self.multiworld, self.player, "hidden_items") == Toggle.option_true:
            set_hidden_item_rules(self.multiworld, self.player)
        if get_option_value(self.multiworld, self.player, "npc_gifts") == Toggle.option_true:
            set_npc_gift_rules(self.multiworld, self.player)
        if get_option_value(self.multiworld, self.player, "enable_ferry") == Toggle.option_true:
            set_enable_ferry_rules(self.multiworld, self.player)

        if get_option_value(self.multiworld, self.player, "require_itemfinder") == Toggle.option_true:
            add_hidden_item_itemfinder_rules(self.multiworld, self.player)

        if get_option_value(self.multiworld, self.player, "require_flash") == Toggle.option_true:
            add_flash_rules(self.multiworld, self.player)


    def generate_basic(self):
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

        locations: List[PokemonEmeraldLocation] = self.multiworld.get_locations(self.player)

        # Key items which are considered in access rules but not randomized are converted to events and placed
        # in their vanilla locations so that the player can have them in their inventory for logic.
        def convert_unrandomized_items_to_events(tag: str):
            for location in locations:
                if location.tags is not None and tag in location.tags:
                    location.place_locked_item(self.create_event(self.item_id_to_name[location.default_item_code]))
                    location.address = None
                    location.is_event = True

        if get_option_value(self.multiworld, self.player, "badges") == RandomizeBadges.option_vanilla:
            convert_unrandomized_items_to_events("Badge")
        if get_option_value(self.multiworld, self.player, "hms") == RandomizeHms.option_vanilla:
            convert_unrandomized_items_to_events("HM")
        if get_option_value(self.multiworld, self.player, "rods") == Toggle.option_false:
            convert_unrandomized_items_to_events("Rod")
        if get_option_value(self.multiworld, self.player, "bikes") == Toggle.option_false:
            convert_unrandomized_items_to_events("Bike")
        if get_option_value(self.multiworld, self.player, "key_items") == Toggle.option_false:
            convert_unrandomized_items_to_events("KeyItem")


    def pre_fill(self):
        # Items which are shuffled between their own locations
        badges_option = get_option_value(self.multiworld, self.player, "badges")
        if badges_option == RandomizeBadges.option_shuffle:
            badge_locations = [location for location, item in self.badge_shuffle_info]
            badge_items = [item for location, item in self.badge_shuffle_info]

            for item in badge_items:
                self.multiworld.itempool.remove(item)

            self.multiworld.random.shuffle(badge_items)
            fill_restrictive(self.multiworld, self.multiworld.get_all_state(False), badge_locations, badge_items, True, True)

        hms_option = get_option_value(self.multiworld, self.player, "hms")
        if hms_option == RandomizeBadges.option_shuffle:
            hm_locations = [location for location, item in self.hm_shuffle_info]
            hm_items = [item for location, item in self.hm_shuffle_info]

            for item in hm_items:
                self.multiworld.itempool.remove(item)

            self.multiworld.random.shuffle(hm_items)
            fill_restrictive(self.multiworld, self.multiworld.get_all_state(False), hm_locations, hm_items, True, True)


    def post_fill(self):
        random = self.multiworld.random

        def randomize_abilities():
            # Creating list of potential abilities
            ability_label_to_value = {ability.label.lower(): ability.ability_id for ability in emerald_data.abilities}

            ability_blacklist_labels = set(["cacophony"])
            option_ability_blacklist = get_option_value(self.multiworld, self.player, "ability_blacklist")
            if option_ability_blacklist is not None:
                ability_blacklist_labels |= set([ability_label.lower() for ability_label in option_ability_blacklist])

            ability_blacklist = set([ability_label_to_value[label] for label in ability_blacklist_labels])
            ability_whitelist = [ability.ability_id for ability in emerald_data.abilities if ability.ability_id not in ability_blacklist]

            if get_option_value(self.multiworld, self.player, "abilities") == Abilities.option_follow_evolutions:
                already_modified: Set[int] = set()

                # Loops through species and only tries to modify abilities if the pokemon has no pre-evolution
                # or if the pre-evolution has already been modified. Then tries to modify all species that evolve
                # from this one which have the same abilities.
                # The outer while loop only runs three times for vanilla ordering: Once for a first pass, once for
                # Hitmonlee/Hitmonchan, and once to verify that there's nothing left to do.
                while True:
                    had_clean_pass = True
                    for species in self.modified_data.species:
                        if species is None:
                            continue
                        if species.species_id in already_modified:
                            continue
                        if species.pre_evolution is not None and species.pre_evolution not in already_modified:
                            continue

                        had_clean_pass = False

                        old_abilities = species.abilities
                        new_abilities = (
                            0 if old_abilities[0] == 0 else random.choice(ability_whitelist),
                            0 if old_abilities[1] == 0 else random.choice(ability_whitelist)
                        )

                        evolutions = [species]
                        while len(evolutions) > 0:
                            evolution = evolutions.pop()
                            if evolution.abilities == old_abilities:
                                evolution.abilities = new_abilities
                                already_modified.add(evolution.species_id)
                                evolutions += [self.modified_data.species[evolution.species_id] for evolution in evolution.evolutions]

                    if had_clean_pass:
                        break
            else: # Not following evolutions
                for species in self.modified_data.species:
                    if species is None:
                        continue

                    old_abilities = species.abilities
                    new_abilities = (
                        0 if old_abilities[0] == 0 else random.choice(ability_whitelist),
                        0 if old_abilities[1] == 0 else random.choice(ability_whitelist)
                    )

                    species.abilities = new_abilities


        def randomize_types():
            for species in self.modified_data.species:
                if species is None:
                    continue

                type_1 = get_random_type(random)
                if species.types[0] == species.types[1]:
                    type_2 = type_1
                else:
                    type_2 = get_random_type(random)
                    while type_2 == type_1:
                        type_2 = get_random_type(random)

                species.types = (type_1, type_2)

        def randomize_learnsets():
            should_start_with_four_moves = get_option_value(self.multiworld, self.player, "level_up_moves") == LevelUpMoves.option_start_with_four_moves

            for species in self.modified_data.species:
                if species is None:
                    continue

                old_learnset = species.learnset
                new_learnset = []

                i = 0
                # Replace filler MOVE_NONEs at start of list
                while old_learnset[i].move_id == 0:
                    if should_start_with_four_moves:
                        new_move = get_random_move(random, set(new_learnset))
                    else:
                        new_move = 0
                    new_learnset.append(LearnsetMove(old_learnset[i].level, new_move))
                    i += 1

                while i < len(old_learnset):
                    # Guarantees the starter has a good damaging move
                    if i == 3:
                        new_move = get_random_damaging_move(random, set(new_learnset))
                    else:
                        new_move = get_random_move(random, set(new_learnset))
                    new_learnset.append(LearnsetMove(old_learnset[i].level, new_move))
                    i += 1

                species.learnset = new_learnset

        def randomize_tm_hm_compatibility():
            tm_compatibility = get_option_value(self.multiworld, self.player, "tm_compatibility")
            hm_compatibility = get_option_value(self.multiworld, self.player, "hm_compatibility")

            for species in self.modified_data.species:
                if species is None:
                    continue

                combatibility_array = int_to_bool_array(species.tm_hm_compatibility)

                # TMs
                for i in range(0, 50):
                    if tm_compatibility == TmCompatibility.option_fully_compatible:
                        combatibility_array[i] = True
                    elif tm_compatibility == TmCompatibility.option_completely_random:
                        combatibility_array[i] = random.choice([True, False])

                # HMs
                for i in range(50, 58):
                    if hm_compatibility == HmCompatibility.option_fully_compatible:
                        combatibility_array[i] = True
                    elif hm_compatibility == HmCompatibility.option_completely_random:
                        combatibility_array[i] = random.choice([True, False])

                species.tm_hm_compatibility = bool_array_to_int(combatibility_array)

        def randomize_tm_moves():
            new_moves = set()

            for i in range(50):
                new_move = get_random_move(random, new_moves)
                new_moves.add(new_move)
                self.modified_data.tmhm_moves[i] = new_move

        def randomize_wild_encounters():
            should_match_bst = get_option_value(self.multiworld, self.player, "wild_pokemon") in [RandomizeWildPokemon.option_match_base_stats, RandomizeWildPokemon.option_match_base_stats_and_type]
            should_match_type = get_option_value(self.multiworld, self.player, "wild_pokemon") in [RandomizeWildPokemon.option_match_type, RandomizeWildPokemon.option_match_base_stats_and_type]
            should_allow_legendaries = get_option_value(self.multiworld, self.player, "allow_wild_legendaries") == Toggle.option_true

            for map_data in self.modified_data.maps:
                new_encounters = [None, None, None]
                old_encounters = [map_data.land_encounters, map_data.water_encounters, map_data.fishing_encounters]

                for i, table in enumerate(old_encounters):
                    if table is not None:
                        new_species = []
                        for species_id in table.slots:
                            original_species = emerald_data.species[species_id]
                            target_bst = sum(original_species.base_stats) if should_match_bst else None
                            target_type = random.choice(original_species.types) if should_match_type else None

                            new_species.append(get_random_species(random, self.modified_data.species, target_bst, target_type, should_allow_legendaries).species_id)

                        new_encounters[i] = EncounterTableData(new_species, table.rom_address)

                map_data.land_encounters = new_encounters[0]
                map_data.water_encounters = new_encounters[1]
                map_data.fishing_encounters = new_encounters[2]

        def randomize_opponent_parties():
            should_match_bst = get_option_value(self.multiworld, self.player, "trainer_parties") in [RandomizeTrainerParties.option_match_base_stats, RandomizeTrainerParties.option_match_base_stats_and_type]
            should_match_type = get_option_value(self.multiworld, self.player, "trainer_parties") in [RandomizeTrainerParties.option_match_type, RandomizeTrainerParties.option_match_base_stats_and_type]
            should_allow_legendaries = get_option_value(self.multiworld, self.player, "allow_trainer_legendaries") == Toggle.option_true

            for trainer in self.modified_data.trainers:
                new_party = []
                for pokemon in trainer.party.pokemon:
                    original_species = emerald_data.species[pokemon.species_id]
                    target_bst = sum(original_species.base_stats) if should_match_bst else None
                    target_type = random.choice(original_species.types) if should_match_type else None

                    new_species = get_random_species(random, self.modified_data.species, target_bst, target_type, should_allow_legendaries)

                    # Could cache this per species
                    tm_hm_movepool = list(set([self.modified_data.tmhm_moves[i] for i, is_compatible in enumerate(int_to_bool_array(new_species.tm_hm_compatibility)) if is_compatible]))
                    level_up_movepool = list(set([move.move_id for move in new_species.learnset if move.level <= pokemon.level]))

                    new_moves = (
                        random.choice(tm_hm_movepool if random.random() < 0.25 else level_up_movepool),
                        random.choice(tm_hm_movepool if random.random() < 0.25 else level_up_movepool),
                        random.choice(tm_hm_movepool if random.random() < 0.25 else level_up_movepool),
                        random.choice(tm_hm_movepool if random.random() < 0.25 else level_up_movepool)
                    )

                    new_party.append(TrainerPokemonData(new_species.species_id, pokemon.level, new_moves))

                trainer.party.pokemon = new_party

        def randomize_starters():
            should_match_bst = get_option_value(self.multiworld, self.player, "starters") in [RandomizeStarters.option_match_base_stats, RandomizeStarters.option_match_base_stats_and_type]
            should_match_type = get_option_value(self.multiworld, self.player, "starters") in [RandomizeStarters.option_match_type, RandomizeStarters.option_match_base_stats_and_type]
            should_allow_legendaries = get_option_value(self.multiworld, self.player, "allow_starter_legendaries") == Toggle.option_true

            starter_1_bst = sum(get_species_by_name("Treecko").base_stats) if should_match_bst else None
            starter_2_bst = sum(get_species_by_name("Torchic").base_stats) if should_match_bst else None
            starter_3_bst = sum(get_species_by_name("Mudkip").base_stats)  if should_match_bst else None

            starter_1_type = random.choice(get_species_by_name("Treecko").types) if should_match_type else None
            starter_2_type = random.choice(get_species_by_name("Torchic").types) if should_match_type else None
            starter_3_type = random.choice(get_species_by_name("Mudkip").types)  if should_match_type else None

            starter_1 = get_random_species(random, self.modified_data.species, starter_1_bst, starter_1_type, should_allow_legendaries)
            starter_2 = get_random_species(random, self.modified_data.species, starter_2_bst, starter_2_type, should_allow_legendaries)
            starter_3 = get_random_species(random, self.modified_data.species, starter_3_bst, starter_3_type, should_allow_legendaries)

            egg_code = get_option_value(self.multiworld, self.player, "easter_egg")
            egg_check_1 = 0
            egg_check_2 = 0

            for i in egg_code:
                egg_check_1 += ord(i)
                egg_check_2 += egg_check_1 * egg_check_1

            if egg_check_2 == 0x14E03A:
                egg = 96 + egg_check_2 - (egg_check_1 * 0x077C)
                self.modified_data.starters = (egg, egg, egg)
            else:
                self.modified_data.starters = (starter_1.species_id, starter_2.species_id, starter_3.species_id)

            # Putting the unchosen starter onto the rival's team
            rival_teams = [
                [
                    ("TRAINER_BRENDAN_ROUTE_103_TREECKO", 0, False),
                    ("TRAINER_BRENDAN_RUSTBORO_TREECKO",  1, False),
                    ("TRAINER_BRENDAN_ROUTE_110_TREECKO", 2, True ),
                    ("TRAINER_BRENDAN_ROUTE_119_TREECKO", 2, True ),
                    ("TRAINER_BRENDAN_LILYCOVE_TREECKO",  3, True ),
                    ("TRAINER_MAY_ROUTE_103_TREECKO",     0, False),
                    ("TRAINER_MAY_RUSTBORO_TREECKO",      1, False),
                    ("TRAINER_MAY_ROUTE_110_TREECKO",     2, True ),
                    ("TRAINER_MAY_ROUTE_119_TREECKO",     2, True ),
                    ("TRAINER_MAY_LILYCOVE_TREECKO",      3, True )
                ],
                [
                    ("TRAINER_BRENDAN_ROUTE_103_TORCHIC", 0, False),
                    ("TRAINER_BRENDAN_RUSTBORO_TORCHIC",  1, False),
                    ("TRAINER_BRENDAN_ROUTE_110_TORCHIC", 2, True ),
                    ("TRAINER_BRENDAN_ROUTE_119_TORCHIC", 2, True ),
                    ("TRAINER_BRENDAN_LILYCOVE_TORCHIC",  3, True ),
                    ("TRAINER_MAY_ROUTE_103_TORCHIC",     0, False),
                    ("TRAINER_MAY_RUSTBORO_TORCHIC",      1, False),
                    ("TRAINER_MAY_ROUTE_110_TORCHIC",     2, True ),
                    ("TRAINER_MAY_ROUTE_119_TORCHIC",     2, True ),
                    ("TRAINER_MAY_LILYCOVE_TORCHIC",      3, True )
                ],
                [
                    ("TRAINER_BRENDAN_ROUTE_103_MUDKIP", 0, False),
                    ("TRAINER_BRENDAN_RUSTBORO_MUDKIP",  1, False),
                    ("TRAINER_BRENDAN_ROUTE_110_MUDKIP", 2, True ),
                    ("TRAINER_BRENDAN_ROUTE_119_MUDKIP", 2, True ),
                    ("TRAINER_BRENDAN_LILYCOVE_MUDKIP",  3, True ),
                    ("TRAINER_MAY_ROUTE_103_MUDKIP",     0, False),
                    ("TRAINER_MAY_RUSTBORO_MUDKIP",      1, False),
                    ("TRAINER_MAY_ROUTE_110_MUDKIP",     2, True ),
                    ("TRAINER_MAY_ROUTE_119_MUDKIP",     2, True ),
                    ("TRAINER_MAY_LILYCOVE_MUDKIP",      3, True )
                ]
            ]

            for i, starter in enumerate([starter_2, starter_3, starter_1]):
                potential_evolutions = [evolution.species_id for evolution in starter.evolutions]
                picked_evolution = starter.species_id
                if len(potential_evolutions) > 0:
                    picked_evolution = random.choice(potential_evolutions)

                for trainer_name, starter_position, is_evolved in rival_teams[i]:
                    trainer_data = self.modified_data.trainers[emerald_data.constants[trainer_name]]
                    trainer_data.party.pokemon[starter_position].species_id = picked_evolution if is_evolved else starter.species_id

        self.modified_data = copy.deepcopy(emerald_data)

        # Randomize species data
        if get_option_value(self.multiworld, self.player, "abilities") != Abilities.option_vanilla:
            randomize_abilities()

        if get_option_value(self.multiworld, self.player, "types") == Toggle.option_true:
            randomize_types()

        if get_option_value(self.multiworld, self.player, "level_up_moves") != LevelUpMoves.option_vanilla:
            randomize_learnsets()

        randomize_tm_hm_compatibility()

        min_catch_rate = min(get_option_value(self.multiworld, self.player, "min_catch_rate"), 255)
        for species in self.modified_data.species:
            if species is not None:
                species.catch_rate = max(species.catch_rate, min_catch_rate)

        if get_option_value(self.multiworld, self.player, "tm_moves") == Toggle.option_true:
            randomize_tm_moves()

        # Randomize wild encounters
        if get_option_value(self.multiworld, self.player, "wild_pokemon") != RandomizeWildPokemon.option_vanilla:
            randomize_wild_encounters()

        # Randomize opponents
        if get_option_value(self.multiworld, self.player, "trainer_parties") != RandomizeTrainerParties.option_vanilla:
            randomize_opponent_parties()

        # Randomize starters
        if get_option_value(self.multiworld, self.player, "starters") != RandomizeStarters.option_vanilla:
            randomize_starters()


    def generate_output(self, output_directory: str):
        generate_output(self.modified_data, self.multiworld, self.player, output_directory)


    def fill_slot_data(self):
        slot_data = self._get_pokemon_emerald_data()
        for option_name in option_definitions:
            option = getattr(self.multiworld, option_name)[self.player]
            if slot_data.get(option_name, None) is None and type(option.value) in {str, int}:
                slot_data[option_name] = int(option.value)
        return slot_data

    def create_item(self, name: str) -> PokemonEmeraldItem:
        item_code = self.item_name_to_id[name]
        return PokemonEmeraldItem(
            name,
            get_item_classification(item_code),
            item_code,
            self.player
        )

    def create_item_by_code(self, item_code: int) -> PokemonEmeraldItem:
        return PokemonEmeraldItem(
            self.item_id_to_name[item_code],
            get_item_classification(item_code),
            item_code,
            self.player
        )

    def create_event(self, name: str) -> PokemonEmeraldItem:
        return PokemonEmeraldItem(
            name,
            ItemClassification.progression,
            None,
            self.player
        )