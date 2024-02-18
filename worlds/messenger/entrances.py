from typing import List, TYPE_CHECKING

from BaseClasses import Entrance
from EntranceRando import randomize_entrances
from .connections import RANDOMIZED_CONNECTIONS, TRANSITIONS
from .options import ShuffleTransitions
from .subclasses import MessengerLocation

if TYPE_CHECKING:
    from . import MessengerRegion, MessengerWorld


def shuffle_entrances(world: "MessengerWorld") -> None:
    multiworld = world.multiworld
    player = world.player
    coupled = world.options.shuffle_transitions == ShuffleTransitions.option_coupled

    def disconnect_entrance() -> None:
        child_region.entrances.remove(entrance)
        entrance.connected_region = None

        er_type = Entrance.EntranceType.ONE_WAY if child == "Glacial Peak - Left" else \
            Entrance.EntranceType.TWO_WAY if child in RANDOMIZED_CONNECTIONS else Entrance.EntranceType.ONE_WAY
        if er_type == Entrance.EntranceType.TWO_WAY:
            mock_entrance = parent_region.create_er_target(entrance.name)
        else:
            mock_entrance = child_region.create_er_target(child)

        entrance.er_type = er_type
        mock_entrance.er_type = er_type

    regions_to_shuffle: List[MessengerRegion] = []
    for parent, child in RANDOMIZED_CONNECTIONS.items():

        if child == "Corrupted Future":
            entrance = multiworld.get_entrance("Artificer's Portal", player)
        elif child == "Tower of Time - Left":
            entrance = multiworld.get_entrance("Artificer's Challenge", player)
        else:
            entrance = multiworld.get_entrance(f"{parent} -> {child}", player)
        parent_region = entrance.parent_region
        child_region = entrance.connected_region
        entrance.world = world
        disconnect_entrance()
        regions_to_shuffle += [parent_region, child_region]

    if world.options.limited_movement:
        tot_hq = world.multiworld.get_region("Tower HQ", world.player)
        event_loc = MessengerLocation(world.player, world.removed_item, None, tot_hq)
        tot_hq.locations.append(event_loc)

    result = randomize_entrances(world, set(regions_to_shuffle), coupled, lambda group: ["Default"])

    if world.options.limited_movement:
        tot_hq.locations.remove(event_loc)

    world.transitions = sorted(result.placements, key=lambda entrance: TRANSITIONS.index(entrance.parent_region.name))

    for transition in world.transitions:
        if "->" not in transition.name:
            continue
        transition.parent_region.exits.remove(transition)
        transition.name = f"{transition.parent_region} -> {transition.connected_region}"
        transition.parent_region.exits.append(transition)
