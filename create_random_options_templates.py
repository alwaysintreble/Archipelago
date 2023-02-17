import os
import typing

from jinja2 import Template

import Options
from Utils import __version__, local_path
from worlds.AutoWorld import AutoWorldRegister


def output_files(exclude: typing.Iterable[str], file_path: str=os.path.join(local_path("output"), "random_templates")):
    os.makedirs(file_path, exist_ok=True)

    for file in os.listdir(file_path):
        full_path = os.path.join(file_path, file)
        if os.path.isfile(full_path):
            os.unlink(full_path)

    for game_name, world_type in AutoWorldRegister.world_types.items():
        if game_name in exclude:
            continue
        all_options: typing.Dict[str, Options.AssembleOptions] = {
            **Options.per_game_common_options,
            **world_type.option_definitions
        }

        with open(local_path("WebHostLib", "templates", "random_options.yaml")) as f:
            file_data = f.read()
        res = Template(file_data).render(
            options=all_options, __version__=__version__, game=game_name
        )
        del file_data
        with open(os.path.join(file_path, game_name + ".yaml"), "w", encoding="utf-8") as f:
            f.write(res)
        with open(os.path.join(file_path, game_name + "2.yaml"), "w", encoding="utf-8") as f:
            f.write(res)

        with open(local_path("WebHostLib", "templates", "minimal_random_options.yaml")) as f:
            file_data = f.read()
        res = Template(file_data).render(
            options=all_options, __version__=__version__, game=game_name
        )
        del file_data
        with open(os.path.join(file_path, game_name + "_minimal.yaml"), "w", encoding="utf-8") as f:
            f.write(res)
        with open(os.path.join(file_path, game_name + "_minimal2.yaml"), "w", encoding="utf-8") as f:
            f.write(res)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate basic YAML files for every game with 'random' for the options")
    parser.add_argument("--path", help="Full file path to output the YAML files to")
    parser.add_argument("--exclude", action="append",
                        help="Comma separated list of games to exclude, using game names. "
                             "Default: {'Archipelago', 'Final Fantasy', 'Sudoku', 'Ori and the Blind Forest'}")
    args = parser.parse_args()
    exclude_list = {"Archipelago", "Final Fantasy", "Sudoku", "Ori and the Blind Forest"}
    if args.exclude:
        exclude_list = exclude_list | set(args.exclude)
    if args.path:
        output_files(exclude_list, args.path)
    else:
        output_files(exclude_list)
