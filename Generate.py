from __future__ import annotations

import argparse
import logging
import os
import random
import string
import sys
import typing
import urllib.parse
import urllib.request
from collections import Counter, ChainMap
from typing import Dict, Tuple, Callable, Any, Union

import ModuleUpdate

ModuleUpdate.update()

import Utils
from worlds.alttp import Options as LttPOptions
from worlds.generic import PlandoConnection
from Utils import parse_yamls, version_tuple, __version__, tuplize_version, get_options, user_path
from worlds.alttp.EntranceRandomizer import parse_arguments
from Main import main as ERmain
from BaseClasses import seeddigits, get_seed, PlandoOptions
import Options
from worlds.alttp.Text import TextTable
from worlds.AutoWorld import AutoWorldRegister
import copy





def mystery_argparse():
    options = get_options()
    defaults = options["generator"]

    def resolve_path(path: str, resolver: Callable[[str], str]) -> str:
        return path if os.path.isabs(path) else resolver(path)

    parser = argparse.ArgumentParser(description="CMD Generation Interface, defaults come from host.yaml.")
    parser.add_argument('--weights_file_path', default=defaults["weights_file_path"],
                        help='Path to the weights file to use for rolling game settings, urls are also valid')
    parser.add_argument('--samesettings', help='Rolls settings per weights file rather than per player',
                        action='store_true')
    parser.add_argument('--player_files_path', default=resolve_path(defaults["player_files_path"], user_path),
                        help="Input directory for player files.")
    parser.add_argument('--seed', help='Define seed number to generate.', type=int)
    parser.add_argument('--multi', default=defaults["players"], type=lambda value: max(int(value), 1))
    parser.add_argument('--spoiler', type=int, default=defaults["spoiler"])
    parser.add_argument('--outputpath', default=resolve_path(options["general_options"]["output_path"], user_path),
                        help="Path to output folder. Absolute or relative to cwd.")  # absolute or relative to cwd
    parser.add_argument('--race', action='store_true', default=defaults["race"])
    parser.add_argument('--meta_file_path', default=defaults["meta_file_path"])
    parser.add_argument('--log_level', default='info', help='Sets log level')
    parser.add_argument('--yaml_output', default=0, type=lambda value: max(int(value), 0),
                        help='Output rolled mystery results to yaml up to specified number (made for async multiworld)')
    parser.add_argument('--plando', default=defaults["plando_options"],
                        help='List of options that can be set manually. Can be combined, for example "bosses, items"')
    args = parser.parse_args()
    if not os.path.isabs(args.weights_file_path):
        args.weights_file_path = os.path.join(args.player_files_path, args.weights_file_path)
    if not os.path.isabs(args.meta_file_path):
        args.meta_file_path = os.path.join(args.player_files_path, args.meta_file_path)
    args.plando: PlandoOptions = PlandoOptions.from_option_string(args.plando)
    return args, options


def get_seed_name(random_source) -> str:
    return f"{random_source.randint(0, pow(10, seeddigits) - 1)}".zfill(seeddigits)


def main(args=None, callback=ERmain):
    if not args:
        args, options = mystery_argparse()

    seed = get_seed(args.seed)
    random.seed(seed)
    seed_name = get_seed_name(random)

    if args.race:
        random.seed()  # reset to time-based random source

    weights_cache: Dict[str, Tuple[Any, ...]] = {}
    if args.weights_file_path and os.path.exists(args.weights_file_path):
        try:
            weights_cache[args.weights_file_path] = read_weights_yamls(args.weights_file_path)
        except Exception as e:
            raise ValueError(f"File {args.weights_file_path} is destroyed. Please fix your yaml.") from e
        print(f"Weights: {args.weights_file_path} >> "
              f"{get_choice('description', weights_cache[args.weights_file_path][-1], 'No description specified')}")

    if args.meta_file_path and os.path.exists(args.meta_file_path):
        try:
            meta_weights = read_weights_yamls(args.meta_file_path)[-1]
        except Exception as e:
            raise ValueError(f"File {args.meta_file_path} is destroyed. Please fix your yaml.") from e
        print(f"Meta: {args.meta_file_path} >> {get_choice('meta_description', meta_weights)}")
        try:  # meta description allows us to verify that the file named meta.yaml is intentionally a meta file
            del(meta_weights["meta_description"])
        except Exception as e:
            raise ValueError("No meta description found for meta.yaml. Unable to verify.") from e
        if args.samesettings:
            raise Exception("Cannot mix --samesettings with --meta")
    else:
        meta_weights = None
    player_id = 1
    player_files = {}
    for file in os.scandir(args.player_files_path):
        fname = file.name
        if file.is_file() and not fname.startswith(".") and \
                os.path.join(args.player_files_path, fname) not in {args.meta_file_path, args.weights_file_path}:
            path = os.path.join(args.player_files_path, fname)
            try:
                weights_cache[fname] = read_weights_yamls(path)
            except Exception as e:
                raise ValueError(f"File {fname} is destroyed. Please fix your yaml.") from e

    # sort dict for consistent results across platforms:
    weights_cache = {key: value for key, value in sorted(weights_cache.items())}
    for filename, yaml_data in weights_cache.items():
        if filename not in {args.meta_file_path, args.weights_file_path}:
            for yaml in yaml_data:
                print(f"P{player_id} Weights: {filename} >> "
                      f"{get_choice('description', yaml, 'No description specified')}")
                player_files[player_id] = filename
                player_id += 1

    args.multi = max(player_id - 1, args.multi)
    print(f"Generating for {args.multi} player{'s' if args.multi > 1 else ''}, {seed_name} Seed {seed} with plando: "
          f"{args.plando}")

    if not weights_cache:
        raise Exception(f"No weights found. Provide a general weights file ({args.weights_file_path}) or individual player files. "
                        f"A mix is also permitted.")
    erargs = parse_arguments(['--multi', str(args.multi)])
    erargs.seed = seed
    erargs.plando_options = args.plando
    erargs.glitch_triforce = options["generator"]["glitch_triforce_room"]
    erargs.spoiler = args.spoiler
    erargs.race = args.race
    erargs.outputname = seed_name
    erargs.outputpath = args.outputpath

    Utils.init_logging(f"Generate_{seed}", loglevel=args.log_level)

    settings_cache: Dict[str, Tuple[argparse.Namespace, ...]] = \
        {fname: (tuple(roll_settings(yaml, args.plando) for yaml in yamls) if args.samesettings else None)
         for fname, yamls in weights_cache.items()}

    if meta_weights:
        for category_name, category_dict in meta_weights.items():
            for key in category_dict:
                option = roll_meta_option(key, category_name, category_dict)
                if option is not None:
                    for path in weights_cache:
                        for yaml in weights_cache[path]:
                            if category_name is None:
                                for category in yaml:
                                    if category in AutoWorldRegister.world_types and key in Options.common_options:
                                        yaml[category][key] = option
                            elif category_name not in yaml:
                                logging.warning(f"Meta: Category {category_name} is not present in {path}.")
                            else:
                                yaml[category_name][key] = option

    player_path_cache = {}
    for player in range(1, args.multi + 1):
        player_path_cache[player] = player_files.get(player, args.weights_file_path)
    name_counter = Counter()
    erargs.player_settings = {}

    player = 1
    while player <= args.multi:
        path = player_path_cache[player]
        if path:
            try:
                settings: Tuple[argparse.Namespace, ...] = settings_cache[path] if settings_cache[path] else \
                    tuple(roll_settings(yaml, args.plando) for yaml in weights_cache[path])
                for settingsObject in settings:
                    for k, v in vars(settingsObject).items():
                        if v is not None:
                            try:
                                getattr(erargs, k)[player] = v
                            except AttributeError:
                                setattr(erargs, k, {player: v})
                            except Exception as e:
                                raise Exception(f"Error setting {k} to {v} for player {player}") from e

                    if path == args.weights_file_path:  # if name came from the weights file, just use base player name
                        erargs.name[player] = f"Player{player}"
                    elif not erargs.name[player]:  # if name was not specified, generate it from filename
                        erargs.name[player] = os.path.splitext(os.path.split(path)[-1])[0]
                    erargs.name[player] = handle_name(erargs.name[player], player, name_counter)

                    player += 1
            except Exception as e:
                raise ValueError(f"File {path} is destroyed. Please fix your yaml.") from e
        else:
            raise RuntimeError(f'No weights specified for player {player}')

    if len(set(name.lower() for name in erargs.name.values())) != len(erargs.name):
        raise Exception(f"Names have to be unique. Names: {Counter(name.lower() for name in erargs.name.values())}")

    if args.yaml_output:
        import yaml
        important = {}
        for option, player_settings in vars(erargs).items():
            if type(player_settings) == dict:
                if all(type(value) != list for value in player_settings.values()):
                    if len(player_settings.values()) > 1:
                        important[option] = {player: value for player, value in player_settings.items() if
                                             player <= args.yaml_output}
                    else:
                        logging.debug(f"No player settings defined for option '{option}'")

            else:
                if player_settings != "":  # is not empty name
                    important[option] = player_settings
                else:
                    logging.debug(f"No player settings defined for option '{option}'")
        if args.outputpath:
            os.makedirs(args.outputpath, exist_ok=True)
        with open(os.path.join(args.outputpath if args.outputpath else ".", f"generate_{seed_name}.yaml"), "wt") as f:
            yaml.dump(important, f)

    callback(erargs, seed)


def read_weights_yamls(path) -> Tuple[Any, ...]:
    try:
        if urllib.parse.urlparse(path).scheme in ('https', 'file'):
            yaml = str(urllib.request.urlopen(path).read(), "utf-8-sig")
        else:
            with open(path, 'rb') as f:
                yaml = str(f.read(), "utf-8-sig")
    except Exception as e:
        raise Exception(f"Failed to read weights ({path})") from e

    return tuple(parse_yamls(yaml))


def interpret_on_off(value) -> bool:
    return {"on": True, "off": False}.get(value, value)


def convert_to_on_off(value) -> str:
    return {True: "on", False: "off"}.get(value, value)


def get_choice_legacy(option, root, value=None) -> Any:
    if option not in root:
        return value
    if type(root[option]) is list:
        return interpret_on_off(random.choices(root[option])[0])
    if type(root[option]) is not dict:
        return interpret_on_off(root[option])
    if not root[option]:
        return value
    if any(root[option].values()):
        return interpret_on_off(
            random.choices(list(root[option].keys()), weights=list(map(int, root[option].values())))[0])
    raise RuntimeError(f"All options specified in \"{option}\" are weighted as zero.")


def get_choice(option, root, value=None) -> Any:
    if option not in root:
        return value
    if type(root[option]) is list:
        return random.choices(root[option])[0]
    if type(root[option]) is not dict:
        return root[option]
    if not root[option]:
        return value
    if any(root[option].values()):
        return random.choices(list(root[option].keys()), weights=list(map(int, root[option].values())))[0]
    raise RuntimeError(f"All options specified in \"{option}\" are weighted as zero.")


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def handle_name(name: str, player: int, name_counter: Counter):
    name_counter[name.lower()] += 1
    number = name_counter[name.lower()]
    new_name = "%".join([x.replace("%number%", "{number}").replace("%player%", "{player}") for x in name.split("%%")])
    new_name = string.Formatter().vformat(new_name, (), SafeDict(number=number,
                                                                 NUMBER=(number if number > 1 else ''),
                                                                 player=player,
                                                                 PLAYER=(player if player > 1 else '')))
    new_name = new_name.strip()[:16]
    if new_name == "Archipelago":
        raise Exception(f"You cannot name yourself \"{new_name}\"")
    return new_name


def prefer_int(input_data: str) -> Union[str, int]:
    try:
        return int(input_data)
    except:
        return input_data


goals = {
    'ganon': 'ganon',
    'crystals': 'crystals',
    'bosses': 'bosses',
    'pedestal': 'pedestal',
    'ganon_pedestal': 'ganonpedestal',
    'triforce_hunt': 'triforcehunt',
    'local_triforce_hunt': 'localtriforcehunt',
    'ganon_triforce_hunt': 'ganontriforcehunt',
    'local_ganon_triforce_hunt': 'localganontriforcehunt',
    'ice_rod_hunt': 'icerodhunt',
}


def roll_percentage(percentage: Union[int, float]) -> bool:
    """Roll a percentage chance.
    percentage is expected to be in range [0, 100]"""
    return random.random() < (float(percentage) / 100)


def update_weights(weights: dict, new_weights: dict, type: str, name: str) -> dict:
    logging.debug(f'Applying {new_weights}')
    new_options = set(new_weights) - set(weights)
    weights.update(new_weights)
    if new_options:
        for new_option in new_options:
            logging.warning(f'{type} Suboption "{new_option}" of "{name}" did not '
                            f'overwrite a root option. '
                            f'This is probably in error.')
    return weights


def roll_meta_option(option_key, game: str, category_dict: Dict) -> Any:
    if not game:
        return get_choice(option_key, category_dict)
    if game in AutoWorldRegister.world_types:
        game_world = AutoWorldRegister.world_types[game]
        options = ChainMap(game_world.option_definitions, Options.per_game_common_options)
        if option_key in options:
            if options[option_key].supports_weighting:
                return get_choice(option_key, category_dict)
            return category_dict[option_key]
    if game == "A Link to the Past":  # TODO wow i hate this
        if option_key in {"glitches_required", "dark_room_logic", "entrance_shuffle", "goals", "triforce_pieces_mode",
                          "triforce_pieces_percentage", "triforce_pieces_available", "triforce_pieces_extra",
                          "triforce_pieces_required", "shop_shuffle", "mode", "item_pool", "item_functionality",
                          "boss_shuffle", "enemy_damage", "enemy_health", "timer", "countdown_start_time",
                          "red_clock_time", "blue_clock_time", "green_clock_time", "dungeon_counters", "shuffle_prizes",
                          "misery_mire_medallion", "turtle_rock_medallion", "sprite_pool", "sprite",
                          "random_sprite_on_event"}:
            return get_choice(option_key, category_dict)
    raise Exception(f"Error generating meta option {option_key} for {game}.")


def roll_linked_options(weights: dict) -> dict:
    weights = copy.deepcopy(weights)  # make sure we don't write back to other weights sets in same_settings
    for option_set in weights["linked_options"]:
        if "name" not in option_set:
            raise ValueError("One of your linked options does not have a name.")
        try:
            if roll_percentage(option_set["percentage"]):
                logging.debug(f"Linked option {option_set['name']} triggered.")
                new_options = option_set["options"]
                for category_name, category_options in new_options.items():
                    currently_targeted_weights = weights
                    if category_name:
                        currently_targeted_weights = currently_targeted_weights[category_name]
                    update_weights(currently_targeted_weights, category_options, "Linked", option_set["name"])
            else:
                logging.debug(f"linked option {option_set['name']} skipped.")
        except Exception as e:
            raise ValueError(f"Linked option {option_set['name']} is destroyed. "
                             f"Please fix your linked option.") from e
    return weights


def roll_triggers(weights: dict, triggers: list) -> dict:
    weights = copy.deepcopy(weights)  # make sure we don't write back to other weights sets in same_settings
    weights["_Generator_Version"] = Utils.__version__
    for i, option_set in enumerate(triggers):
        try:
            currently_targeted_weights = weights
            category = option_set.get("option_category", None)
            if category:
                currently_targeted_weights = currently_targeted_weights[category]
            key = get_choice("option_name", option_set)
            if key not in currently_targeted_weights:
                logging.warning(f'Specified option name {option_set["option_name"]} did not '
                                f'match with a root option. '
                                f'This is probably in error.')
            trigger_result = get_choice("option_result", option_set)
            result = get_choice(key, currently_targeted_weights)
            currently_targeted_weights[key] = result
            if result == trigger_result and roll_percentage(get_choice("percentage", option_set, 100)):
                for category_name, category_options in option_set["options"].items():
                    currently_targeted_weights = weights
                    if category_name:
                        currently_targeted_weights = currently_targeted_weights[category_name]
                    update_weights(currently_targeted_weights, category_options, "Triggered", option_set["option_name"])

        except Exception as e:
            raise ValueError(f"Your trigger number {i + 1} is destroyed. "
                             f"Please fix your triggers.") from e
    return weights


def handle_option(ret: argparse.Namespace, game_weights: dict, option_key: str, option: type(Options.Option), plando_options: PlandoOptions):
    if option_key in game_weights:
        try:
            if not option.supports_weighting:
                player_option = option.from_any(game_weights[option_key])
            else:
                player_option = option.from_any(get_choice(option_key, game_weights))
            setattr(ret, option_key, player_option)
        except Exception as e:
            raise Exception(f"Error generating option {option_key} in {ret.game}") from e
        else:
            player_option.verify(AutoWorldRegister.world_types[ret.game], ret.name, plando_options)
    else:
        setattr(ret, option_key, option.from_any(option.default))  # call the from_any here to support default "random"


def roll_settings(weights: dict, plando_options: PlandoOptions = PlandoOptions.bosses):
    if "linked_options" in weights:
        weights = roll_linked_options(weights)

    if "triggers" in weights:
        weights = roll_triggers(weights, weights["triggers"])

    requirements = weights.get("requires", {})
    if requirements:
        version = requirements.get("version", __version__)
        if tuplize_version(version) > version_tuple:
            raise Exception(f"Settings reports required version of generator is at least {version}, "
                            f"however generator is of version {__version__}")
        required_plando_options = PlandoOptions.from_option_string(requirements.get("plando", ""))
        if required_plando_options not in plando_options:
            if required_plando_options:
                raise Exception(f"Settings reports required plando module {str(required_plando_options)}, "
                                f"which is not enabled.")

    ret = argparse.Namespace()
    for option_key in Options.per_game_common_options:
        if option_key in weights and option_key not in Options.common_options:
            raise Exception(f"Option {option_key} has to be in a game's section, not on its own.")

    ret.game = get_choice("game", weights)
    if ret.game not in weights:
        raise Exception(f"No game options for selected game \"{ret.game}\" found.")

    world_type = AutoWorldRegister.world_types[ret.game]
    game_weights = weights[ret.game]

    if "triggers" in game_weights:
        weights = roll_triggers(weights, game_weights["triggers"])
        game_weights = weights[ret.game]

    ret.name = get_choice('name', weights)
    for option_key, option in Options.common_options.items():
        setattr(ret, option_key, option.from_any(get_choice(option_key, weights, option.default)))

    if ret.game in AutoWorldRegister.world_types:
        for option_key, option in world_type.option_definitions.items():
            handle_option(ret, game_weights, option_key, option, plando_options)
        for option_key, option in Options.per_game_common_options.items():
            # skip setting this option if already set from common_options, defaulting to root option
            if option_key not in world_type.option_definitions and \
                    (option_key not in Options.common_options or option_key in game_weights):
                handle_option(ret, game_weights, option_key, option, plando_options)
        if PlandoOptions.items in plando_options:
            ret.plando_items = game_weights.get("plando_items", [])
        if ret.game == "Minecraft" or ret.game == "Ocarina of Time":
            # bad hardcoded behavior to make this work for now
            ret.plando_connections = []
            if PlandoOptions.connections in plando_options:
                options = game_weights.get("plando_connections", [])
                for placement in options:
                    if roll_percentage(get_choice("percentage", placement, 100)):
                        ret.plando_connections.append(PlandoConnection(
                            get_choice("entrance", placement),
                            get_choice("exit", placement),
                            get_choice("direction", placement)
                        ))
        elif ret.game == "A Link to the Past":
            roll_alttp_settings(ret, game_weights, plando_options)
    else:
        raise Exception(f"Unsupported game {ret.game}")

    return ret


def roll_alttp_settings(ret: argparse.Namespace, weights, plando_options):
    if "dungeon_items" in weights and get_choice_legacy('dungeon_items', weights, "none") != "none":
        raise Exception(f"dungeon_items key in A Link to the Past was removed, but is present in these weights as {get_choice_legacy('dungeon_items', weights, False)}.")
    glitches_required = get_choice_legacy('glitches_required', weights)
    if glitches_required not in [None, 'none', 'no_logic', 'overworld_glitches', 'hybrid_major_glitches', 'minor_glitches']:
        logging.warning("Only NMG, OWG, HMG and No Logic supported")
        glitches_required = 'none'
    ret.logic = {None: 'noglitches', 'none': 'noglitches', 'no_logic': 'nologic', 'overworld_glitches': 'owglitches',
                 'minor_glitches': 'minorglitches', 'hybrid_major_glitches': 'hybridglitches'}[
        glitches_required]

    ret.dark_room_logic = get_choice_legacy("dark_room_logic", weights, "lamp")
    if not ret.dark_room_logic:  # None/False
        ret.dark_room_logic = "none"
    if ret.dark_room_logic == "sconces":
        ret.dark_room_logic = "torches"
    if ret.dark_room_logic not in {"lamp", "torches", "none"}:
        raise ValueError(f"Unknown Dark Room Logic: \"{ret.dark_room_logic}\"")

    entrance_shuffle = get_choice_legacy('entrance_shuffle', weights, 'vanilla')
    if entrance_shuffle.startswith('none-'):
        ret.shuffle = 'vanilla'
    else:
        ret.shuffle = entrance_shuffle if entrance_shuffle != 'none' else 'vanilla'

    goal = get_choice_legacy('goals', weights, 'ganon')

    ret.goal = goals[goal]


    extra_pieces = get_choice_legacy('triforce_pieces_mode', weights, 'available')

    ret.triforce_pieces_required = LttPOptions.TriforcePieces.from_any(get_choice_legacy('triforce_pieces_required', weights, 20))

    # sum a percentage to required
    if extra_pieces == 'percentage':
        percentage = max(100, float(get_choice_legacy('triforce_pieces_percentage', weights, 150))) / 100
        ret.triforce_pieces_available = int(round(ret.triforce_pieces_required * percentage, 0))
    # vanilla mode (specify how many pieces are)
    elif extra_pieces == 'available':
        ret.triforce_pieces_available = LttPOptions.TriforcePieces.from_any(
            get_choice_legacy('triforce_pieces_available', weights, 30))
    # required pieces + fixed extra
    elif extra_pieces == 'extra':
        extra_pieces = max(0, int(get_choice_legacy('triforce_pieces_extra', weights, 10)))
        ret.triforce_pieces_available = ret.triforce_pieces_required + extra_pieces

    # change minimum to required pieces to avoid problems
    ret.triforce_pieces_available = min(max(ret.triforce_pieces_required, int(ret.triforce_pieces_available)), 90)

    ret.shop_shuffle = get_choice_legacy('shop_shuffle', weights, '')
    if not ret.shop_shuffle:
        ret.shop_shuffle = ''

    ret.mode = get_choice_legacy("mode", weights)

    ret.difficulty = get_choice_legacy('item_pool', weights)

    ret.item_functionality = get_choice_legacy('item_functionality', weights)


    ret.enemy_damage = {None: 'default',
                        'default': 'default',
                        'shuffled': 'shuffled',
                        'random': 'chaos', # to be removed
                        'chaos': 'chaos',
                        }[get_choice_legacy('enemy_damage', weights)]

    ret.enemy_health = get_choice_legacy('enemy_health', weights)

    ret.timer = {'none': False,
                 None: False,
                 False: False,
                 'timed': 'timed',
                 'timed_ohko': 'timed-ohko',
                 'ohko': 'ohko',
                 'timed_countdown': 'timed-countdown',
                 'display': 'display'}[get_choice_legacy('timer', weights, False)]

    ret.countdown_start_time = int(get_choice_legacy('countdown_start_time', weights, 10))
    ret.red_clock_time = int(get_choice_legacy('red_clock_time', weights, -2))
    ret.blue_clock_time = int(get_choice_legacy('blue_clock_time', weights, 2))
    ret.green_clock_time = int(get_choice_legacy('green_clock_time', weights, 4))

    ret.dungeon_counters = get_choice_legacy('dungeon_counters', weights, 'default')

    ret.shuffle_prizes = get_choice_legacy('shuffle_prizes', weights, "g")

    ret.required_medallions = [get_choice_legacy("misery_mire_medallion", weights, "random"),
                               get_choice_legacy("turtle_rock_medallion", weights, "random")]

    for index, medallion in enumerate(ret.required_medallions):
        ret.required_medallions[index] = {"ether": "Ether", "quake": "Quake", "bombos": "Bombos", "random": "random"} \
            .get(medallion.lower(), None)
        if not ret.required_medallions[index]:
            raise Exception(f"unknown Medallion {medallion} for {'misery mire' if index == 0 else 'turtle rock'}")

    ret.plando_texts = {}
    if PlandoOptions.texts in plando_options:
        tt = TextTable()
        tt.removeUnwantedText()
        options = weights.get("plando_texts", [])
        for placement in options:
            if roll_percentage(get_choice_legacy("percentage", placement, 100)):
                at = str(get_choice_legacy("at", placement))
                if at not in tt:
                    raise Exception(f"No text target \"{at}\" found.")
                ret.plando_texts[at] = str(get_choice_legacy("text", placement))

    ret.plando_connections = []
    if PlandoOptions.connections in plando_options:
        options = weights.get("plando_connections", [])
        for placement in options:
            if roll_percentage(get_choice_legacy("percentage", placement, 100)):
                ret.plando_connections.append(PlandoConnection(
                    get_choice_legacy("entrance", placement),
                    get_choice_legacy("exit", placement),
                    get_choice_legacy("direction", placement, "both")
                ))

    ret.sprite_pool = weights.get('sprite_pool', [])
    ret.sprite = get_choice_legacy('sprite', weights, "Link")
    if 'random_sprite_on_event' in weights:
        randomoneventweights = weights['random_sprite_on_event']
        if get_choice_legacy('enabled', randomoneventweights, False):
            ret.sprite = 'randomon'
            ret.sprite += '-hit' if get_choice_legacy('on_hit', randomoneventweights, True) else ''
            ret.sprite += '-enter' if get_choice_legacy('on_enter', randomoneventweights, False) else ''
            ret.sprite += '-exit' if get_choice_legacy('on_exit', randomoneventweights, False) else ''
            ret.sprite += '-slash' if get_choice_legacy('on_slash', randomoneventweights, False) else ''
            ret.sprite += '-item' if get_choice_legacy('on_item', randomoneventweights, False) else ''
            ret.sprite += '-bonk' if get_choice_legacy('on_bonk', randomoneventweights, False) else ''
            ret.sprite = 'randomonall' if get_choice_legacy('on_everything', randomoneventweights, False) else ret.sprite
            ret.sprite = 'randomonnone' if ret.sprite == 'randomon' else ret.sprite

            if (not ret.sprite_pool or get_choice_legacy('use_weighted_sprite_pool', randomoneventweights, False)) \
                    and 'sprite' in weights:  # Use sprite as a weighted sprite pool, if a sprite pool is not already defined.
                for key, value in weights['sprite'].items():
                    if key.startswith('random'):
                        ret.sprite_pool += ['random'] * int(value)
                    else:
                        ret.sprite_pool += [key] * int(value)


def run_gui():
    from kvui import App, ContainerLayout, MainLayout, BoxLayout, ProgressBar, TextInput, Button, Label, DropDown, Widget, escape_markup

    class TextColors(Widget):
        color_codes = {
            "black": "000000",
            "red": "EE0000",
            "green": "00FF7F",
            "yellow": "FAFAD2",
            "blue": "6495ED",
            "magenta": "EE00EE",
            "cyan": "00EEEE",
            "slateblue": "6D8BE8",
            "plum": "AF99EF",
            "salmon": "FA8072",
            "white": "FFFFFF",
        }

    class InputLabel(Label):
        def __init__(self, **kwargs):
            if "size" not in kwargs:
                kwargs["size"] = (100, 30)
            super().__init__(**kwargs)

    class NumericTextInput(TextInput):
        def __init__(self, **kwargs):
            if "size_hint_x" not in kwargs:
                kwargs["size_hint_x"] = None
            super().__init__(**kwargs)

    class Generate(App):
        base_title: str = "Archipelago Generate"
        container: ContainerLayout
        grid: MainLayout
        start_layout: BoxLayout
        seed_entry: str
        seed_entry_bar: NumericTextInput
        progress_bar: ProgressBar
        config_options: MainLayout

        args: Dict
        hint_cost: str
        hint_cost_entry: NumericTextInput
        race_mode: Button

        def __init__(self):
            self.title = self.base_title
            self.icon = r"data/icon.png"
            self.seed_entry = ""
            self.hint_cost = f"{Utils.get_options()['server_options']['hint_cost']}"
            self.players = "0"
            self.args = {}
            colors = TextColors()
            self.color_codes = {name: getattr(colors, name, code) for name, code in colors.color_codes.items()}
            super().__init__()

        def get_new_button(self, text: str, callback: typing.Optional[typing.Callable] = None) -> Button:
            new_button = Button(text=text, size=(100, 30), size_hint_y=None, size_hint_x=None)
            new_button.orig_text = text
            if callback:
                new_button.component = callback
            new_button.bind(on_release=self.component_action)
            return new_button

        def set_dropdown_text(self, instance, data):
            setattr(instance, "selection", data)
            new_text = f"{instance.attach_to.orig_text}\n{data}"
            setattr(instance.attach_to, "text", new_text)

        def get_new_dropdown(self, text: str, buttons: typing.List[str], default: typing.Optional[str] = None) -> Button:
            new_dropdown = DropDown()
            for button in buttons:
                dropdown_button = self.get_new_button(button)
                dropdown_button.bind(on_release=lambda btn: new_dropdown.select(btn.text))
                new_dropdown.add_widget(dropdown_button)
            main_button = self.get_new_button(text=text)
            if default:
                main_button.text = f"{text}\n{default}"
                main_button.selection = default
            main_button.size = (100, 50)
            main_button.bind(on_release=new_dropdown.open)
            main_button.add_widget(new_dropdown)
            new_dropdown.bind(on_select=self.set_dropdown_text)
            return main_button

        def build(self):
            self.container = ContainerLayout()
            self.grid = MainLayout(cols=1)
            self.container.add_widget(self.grid)

            # header
            self.start_layout = BoxLayout(size_hint_y=None, height=30)
            self.start_layout.add_widget(InputLabel(text="Seed:"))

            self.seed_entry_bar = NumericTextInput(text=self.seed_entry, size_hint_x=1)
            self.seed_entry_bar.bind(on_text_validate=self.generate_button_action)
            self.start_layout.add_widget(self.seed_entry_bar)

            self.start_layout.add_widget(self.get_new_button("Generate", main))
            self.grid.add_widget(self.start_layout)

            self.progress_bar = ProgressBar(size_hint_y=None, height=3)
            self.grid.add_widget(self.progress_bar)

            # middle section
            self.config_options = MainLayout(cols=3, rows=2, size_hint_y=None)
            self.dropdown_options_1 = BoxLayout()

            self.config_options.add_widget(InputLabel(text="Hint Cost %:"))
            self.hint_cost_entry = NumericTextInput(text=self.hint_cost)
            self.config_options.add_widget(self.hint_cost_entry)
            self.config_options.add_widget(self.dropdown_options_1)

            self.config_options.add_widget(InputLabel(text="Players:"))
            self.players_entry = NumericTextInput(text=self.players)
            self.config_options.add_widget(self.players_entry)

            # config options
            self.race_mode = self.get_new_dropdown("Race Mode", ["Yes", "No"], "Yes" if Utils.get_options()["generator"]["race"] else "No")
            self.dropdown_options_1.add_widget(self.race_mode)
            self.release_mode = self.get_new_dropdown("Release Mode", ["disabled", "enabled", "auto", "auto-enabled", "goal"], Utils.get_options()["server_options"]["release_mode"])
            self.dropdown_options_1.add_widget(self.release_mode)
            self.collect_mode = self.get_new_dropdown("Collect Mode", ["disabled", "enabled", "auto", "auto-enabled", "goal"], Utils.get_options()["server_options"]["collect_mode"])
            self.dropdown_options_1.add_widget(self.collect_mode)
            self.remaining_mode = self.get_new_dropdown("Remaining Mode", ["disabled", "enabled", "goal"], Utils.get_options()["server_options"]["remaining_mode"])
            self.dropdown_options_1.add_widget(self.remaining_mode)
            spoiler_options = {
                0: "None",
                1: "no playthrough",
                2: "playthrough",
                3: "paths",
            }
            self.spoiler = self.get_new_dropdown("Spoiler", ["None", "no playthrough", "playthrough", "paths"], spoiler_options[Utils.get_options()["generator"]["spoiler"]])
            self.dropdown_options_1.add_widget(self.spoiler)

            self.grid.add_widget(self.config_options)

            return self.container

        @staticmethod
        def component_action(button):
            button.component()

        def generate_button_action(self, button):
            self.seed_entry = button.text
            if self.seed_entry:
                if self.seed_entry.isdigit():
                    main()
            else:
                main()

    Generate().run()


if __name__ == '__main__':
    import atexit
    confirmation = atexit.register(input, "Press enter to close.")
    run_gui()
    # main()
    # in case of error-free exit should not need confirmation
    atexit.unregister(confirmation)
