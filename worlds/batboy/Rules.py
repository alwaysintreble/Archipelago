from typing import Dict, Optional, Callable, TYPE_CHECKING
from worlds.AutoWorld import LogicMixin
if TYPE_CHECKING:
    from worlds.batboy import BatBoyWorld
else:
    BatBoyWorld = object


class BatBoyLogic(LogicMixin):
    pass


class LocationRules:
    player: int

    def __init__(self, world: BatBoyWorld):
        self.player = world.player

        self.level_rules: Dict[str, Optional[Callable]] = {
            "Frozen Peak": lambda state: state.has("Bat Spin", self.player),
            "Windy Forest": lambda state: state.has("Bat Spin", self.player),
        }

        self.location_rules: Dict[str, Optional[Callable]] = {
            "Grassy Plains Golden Seed": lambda state: state.has_all({"Bat Spin", "Slash Bash"}, self.player) or
                                                       state.has("Grappling Ribbon", self.player),
            "Windy Forest Golden Seed": lambda state: state.has_all({"Slash Bash", "Grappling Ribbon"}, self.player),
        }

        self.shop_rules: Dict[str, Optional[Callable]] = {}
