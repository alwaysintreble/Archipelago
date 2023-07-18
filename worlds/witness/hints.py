from BaseClasses import MultiWorld
from .Options import is_option_enabled, get_option_value

joke_hints = [
    "Quaternions break my brain",
    "Eclipse has nothing, but you should do it anyway.",
    "Beep",
    "Putting in custom subtitles shouldn't have been as hard as it was...",
    "BK mode is right around the corner.",
    "You can do it!",
    "I believe in you!",
    "The person playing is cute. <3",
    "dash dot, dash dash dash, dash, dot dot dot dot, dot dot, dash dot, dash dash dot",
    "When you think about it, there are actually a lot of bubbles in a stream.",
    "Never gonna give you up\nNever gonna let you down\nNever gonna run around and desert you",
    "Thanks to the Archipelago developers for making this possible.",
    "Have you tried ChecksFinder?\nIf you like puzzles, you might enjoy it!",
    "Have you tried Dark Souls III?\nA tough game like this feels better when friends are helping you!",
    "Have you tried Donkey Kong Country 3?\nA legendary game from a golden age of platformers!",
    "Have you tried Factorio?\nAlone in an unknown multiworld. Sound familiar?",
    "Have you tried Final Fantasy?\nExperience a classic game improved to fit modern standards!",
    "Have you tried Hollow Knight?\nAnother independent hit revolutionising a genre!",
    "Have you tried A Link to the Past?\nThe Archipelago game that started it all!",
    "Have you tried Meritous?\nYou should know that obscure games are often groundbreaking!",
    "Have you tried Ocarina of Time?\nOne of the biggest randomizers, big inspiration for this one's features!",
    "Have you tried Raft?\nHaven't you always wanted to explore the ocean surrounding this island?",
    "Have you tried Risk of Rain 2?\nI haven't either. But I hear it's incredible!",
    "Have you tried Rogue Legacy?\nAfter solving so many puzzles it's the perfect way to rest your brain.",
    "Have you tried Secret of Evermore?\nI haven't either But I hear it's great!",
    "Have you tried Slay the Spire?\nExperience the thrill of combat without needing fast fingers!",
    "Have you tried SMZ3?\nWhy play one incredible game when you can play 2 at once?",
    "Have you tried Starcraft 2?\nUse strategy and management to crush your enemies!",
    "Have you tried Super Mario 64?\n3-dimensional games like this owe everything to that game.",
    "Have you tried Super Metroid?\nA classic game, yet still one of the best in the genre.",
    "Have you tried Timespinner?\nEveryone who plays it ends up loving it!",
    "Have you tried VVVVVV?\nExperience the essence of gaming distilled into its purest form!",
    "Have you tried The Witness?\nOh. I guess you already have. Thanks for playing!",
    "Have you tried Super Mario World?\nI don't think I need to tell you that it is beloved by many.",
    "Have you tried Overcooked 2?\nWhen you're done relaxing with puzzles, use your energy to yell at your friends.",
    "Have you tried Zillion?\nMe neither. But it looks fun. So, let's try something new together?",
    "Have you tried Hylics 2?\nStop motion might just be the epitome of unique art styles.",
    "Have you tried Pokemon Red&Blue?\nA cute pet collecting game that fascinated an entire generation.",
    "Have you tried Lufia II?\nRoguelites are not just a 2010s phenomenon, turns out.",
    "Have you tried Minecraft?\nI have recently learned this is a question that needs to be asked.",
    "Have you tried Subnautica?\nIf you like this game's lonely atmosphere, I would suggest you try it.",

    "Have you tried Sonic Adventure 2?\nIf the silence on this island is getting to you, "
    "there aren't many games more energetic.",

    "Waiting to get your items?\nTry BK Sudoku! Make progress even while stuck.",
    "One day I was fascinated by the subject of generation of waves by wind.",
    "I don't like sandwiches. Why would you think I like sandwiches? Have you ever seen me with a sandwich?",
    "Where are you right now?\nI'm at soup!\nWhat do you mean you're at soup?",
    "Remember to ask in the Archipelago Discord what the Functioning Brain does.",
    "Don't use your puzzle skips, you might need them later.",
    "For an extra challenge, try playing blindfolded.",
    "Go to the top of the mountain and see if you can see your house.",
    "Yellow = Red + Green\nCyan = Green + Blue\nMagenta = Red + Blue",
    "Maybe that panel really is unsolvable.",
    "Did you make sure it was plugged in?",
    "Do not look into laser with remaining eye.",
    "Try pressing Space to jump.",
    "The Witness is a Doom clone.\nJust replace the demons with puzzles",
    "Test Hint please ignore",
    "Shapers can never be placed outside the panel boundaries, even if subtracted.",
    "The Keep laser panels use the same trick on both sides!",
    "Can't get past a door? Try going around. Can't go around? Try building a nether portal.",
    "We've been trying to reach you about your car's extended warranty.",
    "I hate this game. I hate this game. I hate this game.\n- Chess player Bobby Fischer",
    "Dear Mario,\nPlease come to the castle. I've baked a cake for you!",
    "Have you tried waking up?\nYeah, me neither.",
    "Why do they call it The Witness, when wit game the player view play of with the game.",
    "THE WIND FISH IN NAME ONLY, FOR IT IS NEITHER",
    "Like this game?\nTry The Wit.nes, Understand, INSIGHT, Taiji What the Witness?, and Tametsi.",
    "In a race, It's survival of the Witnesst.",
    "This hint has been removed. We apologize for your inconvenience.",
    "O-----------",
    "Circle is draw\nSquare is separate\nLine is win",
    "Circle is draw\nStar is pair\nLine is win",
    "Circle is draw\nCircle is copy\nLine is win",
    "Circle is draw\nDot is eat\nLine is win",
    "Circle is start\nWalk is draw\nLine is win",
    "Circle is start\nLine is win\nWitness is you",
    "Can't find any items?\nConsider a relaxing boat trip around the island!",
    "Don't forget to like, comment, and subscribe.",
    "Ah crap, gimme a second.\n[papers rustling]\nSorry, nothing.",
    "Trying to get a hint? Too bad.",
    "Here's a hint: Get good at the game.",
    "I'm still not entirely sure what we're witnessing here.",
    "Have you found a red page yet? No? Then have you found a blue page?",
    "And here we see the Witness player, seeking answers where there are none-\nDid someone turn on the loudspeaker?",

    "Hints suggested by:\nIHNN, Beaker, MrPokemon11, Ember, TheM8, NewSoupVi,"
    "KF, Yoshi348, Berserker, BowlinJim, oddGarrett, Pink Switch.",
]


def get_always_hint_items(multiworld: MultiWorld, player: int):
    always = [
        "Boat",
        "Caves Exits to Main Island",
        "Progressive Dots",
    ]

    difficulty = get_option_value(multiworld, player, "puzzle_randomization")
    discards = is_option_enabled(multiworld, player, "shuffle_discarded_panels")
    wincon = get_option_value(multiworld, player, "victory_condition")

    if discards:
        if difficulty == 1:
            always.append("Arrows")
        else:
            always.append("Triangles")

    if wincon == 0:
        always.append("Mountain Bottom Floor Final Room Entry (Door)")

    return always


def get_always_hint_locations(multiworld: MultiWorld, player: int):
    return {
        "Challenge Vault Box",
        "Mountain Bottom Floor Discard",
        "Theater Eclipse EP",
        "Shipwreck Couch EP",
        "Mountainside Cloud Cycle EP",
    }


def get_priority_hint_items(multiworld: MultiWorld, player: int):
    priority = {
        "Caves Mountain Shortcut (Door)",
        "Caves Swamp Shortcut (Door)",
        "Negative Shapers",
        "Sound Dots",
        "Colored Dots",
        "Stars + Same Colored Symbol",
        "Swamp Entry (Panel)",
        "Swamp Laser Shortcut (Door)",
    }

    if is_option_enabled(multiworld, player, "shuffle_lasers"):
        lasers = [
            "Symmetry Laser",
            "Town Laser",
            "Keep Laser",
            "Swamp Laser",
            "Treehouse Laser",
            "Monastery Laser",
            "Jungle Laser",
            "Quarry Laser",
            "Bunker Laser",
            "Shadows Laser",
        ]

        if get_option_value(multiworld, player, "shuffle_doors") >= 2:
            priority.add("Desert Laser")
            priority.update(multiworld.per_slot_randoms[player].sample(lasers, 5))

        else:
            lasers.append("Desert Laser")
            priority.update(multiworld.per_slot_randoms[player].sample(lasers, 6))

    return priority


def get_priority_hint_locations(multiworld: MultiWorld, player: int):
    return {
        "Swamp Purple Underwater",
        "Shipwreck Vault Box",
        "Town RGB Room Left",
        "Town RGB Room Right",
        "Treehouse Green Bridge 7",
        "Treehouse Green Bridge Discard",
        "Shipwreck Discard",
        "Desert Vault Box",
        "Mountainside Vault Box",
        "Mountainside Discard",
        "Tunnels Theater Flowers EP",
        "Boat Shipwreck Green EP",
        "Quarry Stoneworks Control Room Left",
    }


def make_hint_from_item(multiworld: MultiWorld, player: int, item: str):
    location_obj = multiworld.find_item(item, player).item.location
    location_name = location_obj.name
    if location_obj.player != player:
        location_name += " (" + multiworld.get_player_name(location_obj.player) + ")"

    return location_name, item, location_obj.address if (location_obj.player == player) else -1


def make_hint_from_location(multiworld: MultiWorld, player: int, location: str):
    location_obj = multiworld.get_location(location, player)
    item_obj = multiworld.get_location(location, player).item
    item_name = item_obj.name
    if item_obj.player != player:
        item_name += " (" + multiworld.get_player_name(item_obj.player) + ")"

    return location, item_name, location_obj.address if (location_obj.player == player) else -1


def make_hints(multiworld: MultiWorld, player: int, hint_amount: int):
    hints = list()

    prog_items_in_this_world = {
        item.name for item in multiworld.get_items()
        if item.player == player and item.code and item.advancement
    }
    loc_in_this_world = {
        location.name for location in multiworld.get_locations()
        if location.player == player and location.address
    }

    always_locations = [
        location for location in get_always_hint_locations(multiworld, player)
        if location in loc_in_this_world
    ]
    always_items = [
        item for item in get_always_hint_items(multiworld, player)
        if item in prog_items_in_this_world
    ]
    priority_locations = [
        location for location in get_priority_hint_locations(multiworld, player)
        if location in loc_in_this_world
    ]
    priority_items = [
        item for item in get_priority_hint_items(multiworld, player)
        if item in prog_items_in_this_world
    ]

    always_hint_pairs = dict()

    for item in always_items:
        hint_pair = make_hint_from_item(multiworld, player, item)

        if hint_pair[2] == 158007:  # Tutorial Gate Open
            continue

        always_hint_pairs[hint_pair[0]] = (hint_pair[1], True, hint_pair[2])

    for location in always_locations:
        hint_pair = make_hint_from_location(multiworld, player, location)
        always_hint_pairs[hint_pair[0]] = (hint_pair[1], False, hint_pair[2])

    priority_hint_pairs = dict()

    for item in priority_items:
        hint_pair = make_hint_from_item(multiworld, player, item)

        if hint_pair[2] == 158007:  # Tutorial Gate Open
            continue

        priority_hint_pairs[hint_pair[0]] = (hint_pair[1], True, hint_pair[2])

    for location in priority_locations:
        hint_pair = make_hint_from_location(multiworld, player, location)
        priority_hint_pairs[hint_pair[0]] = (hint_pair[1], False, hint_pair[2])

    for loc, item in always_hint_pairs.items():
        if item[1]:
            hints.append((f"{item[0]} can be found at {loc}.", item[2]))
        else:
            hints.append((f"{loc} contains {item[0]}.", item[2]))

    multiworld.per_slot_randoms[player].shuffle(hints)  # shuffle always hint order in case of low hint amount

    remaining_hints = hint_amount - len(hints)
    priority_hint_amount = int(max(0.0, min(len(priority_hint_pairs) / 2, remaining_hints / 2)))

    prog_items_in_this_world = sorted(list(prog_items_in_this_world))
    locations_in_this_world = sorted(list(loc_in_this_world))

    multiworld.per_slot_randoms[player].shuffle(prog_items_in_this_world)
    multiworld.per_slot_randoms[player].shuffle(locations_in_this_world)

    priority_hint_list = list(priority_hint_pairs.items())
    multiworld.per_slot_randoms[player].shuffle(priority_hint_list)
    for _ in range(0, priority_hint_amount):
        next_priority_hint = priority_hint_list.pop()
        loc = next_priority_hint[0]
        item = next_priority_hint[1]

        if item[1]:
            hints.append((f"{item[0]} can be found at {loc}.", item[2]))
        else:
            hints.append((f"{loc} contains {item[0]}.", item[2]))

    next_random_hint_is_item = multiworld.per_slot_randoms[player].randint(0, 2)

    while len(hints) < hint_amount:
        if next_random_hint_is_item:
            if not prog_items_in_this_world:
                next_random_hint_is_item = not next_random_hint_is_item
                continue

            hint = make_hint_from_item(multiworld, player, prog_items_in_this_world.pop())
            hints.append((f"{hint[1]} can be found at {hint[0]}.", hint[2]))
        else:
            hint = make_hint_from_location(multiworld, player, locations_in_this_world.pop())
            hints.append((f"{hint[0]} contains {hint[1]}.", hint[2]))

        next_random_hint_is_item = not next_random_hint_is_item

    return hints


def generate_joke_hints(multiworld: MultiWorld, player: int, amount: int):
    return [(x, -1) for x in multiworld.per_slot_randoms[player].sample(joke_hints, amount)]
