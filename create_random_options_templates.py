import os
import typing

from jinja2 import Template

import Options
from Utils import __version__, local_path
from worlds.AutoWorld import AutoWorldRegister


def output_files(file_path: str=os.path.join(local_path("output"), "random_templates")):
    os.makedirs(file_path, exist_ok=True)

    for file in os.listdir(file_path):
        full_path = os.path.join(file_path, file)
        if os.path.isfile(full_path):
            os.unlink(full_path)

    for game_name, world_type in AutoWorldRegister.world_types.items():
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


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate basic YAML files for every game with 'random' for the options")
    parser.add_argument("--path", help="Full file path to output the YAML files to")
    args = parser.parse_args()
    path = args.path
    if path:
        output_files(path)
    else:
        output_files()
