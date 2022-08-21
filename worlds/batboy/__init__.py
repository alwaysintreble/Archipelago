from ..AutoWorld import WebWorld, World
from BaseClasses import MultiWorld, Tutorial


class BatBoyWeb(WebWorld):
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


class BatBoyWorld(World):
    web = BatBoyWeb()


