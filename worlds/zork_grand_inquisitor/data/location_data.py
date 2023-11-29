from typing import Dict, NamedTuple, Optional, Tuple, Union

from ..enums import (
    ZorkGrandInquisitorEvents,
    ZorkGrandInquisitorItems,
    ZorkGrandInquisitorLocations,
    ZorkGrandInquisitorRegions,
    ZorkGrandInquisitorTags,
)


class ZorkGrandInquisitorLocationData(NamedTuple):
    game_state_trigger: Optional[
        Tuple[
            Union[
                Tuple[str, str],
                Tuple[int, int],
                Tuple[int, Tuple[int, ...]],
            ],
            ...,
        ]
    ]
    archipelago_id: Optional[int]
    region: ZorkGrandInquisitorRegions
    tags: Optional[Tuple[ZorkGrandInquisitorTags, ...]] = None
    requirements: Optional[
        Tuple[
            Union[
                ZorkGrandInquisitorItems,
                ZorkGrandInquisitorEvents,
            ],
            ...,
        ]
    ] = None
    event_item_name: Optional[str] = None


LOCATION_OFFSET = 9758067000

location_data: Dict[
    Union[ZorkGrandInquisitorLocations, ZorkGrandInquisitorEvents], ZorkGrandInquisitorLocationData
] = {
    ZorkGrandInquisitorLocations.TOTEMIZED_DAILY_BILLBOARD: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "px1h"),),
        archipelago_id=LOCATION_OFFSET + 0,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.ELSEWHERE: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "pc1e"),),
        archipelago_id=LOCATION_OFFSET + 1,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.HELP_ME_CANT_BREATHE: ZorkGrandInquisitorLocationData(
        game_state_trigger=((10421, 1),),
        archipelago_id=LOCATION_OFFSET + 2,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.PLASTIC_SIX_PACK_HOLDER,),
    ),
    ZorkGrandInquisitorLocations.THATS_THE_SPIRIT: ZorkGrandInquisitorLocationData(
        game_state_trigger=((10341, 95),),
        archipelago_id=LOCATION_OFFSET + 3,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.ARREST_THE_VANDAL: ZorkGrandInquisitorLocationData(
        game_state_trigger=((10789, 1),),
        archipelago_id=LOCATION_OFFSET + 4,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorEvents.CIGAR_ACCESSIBLE,),
    ),
    ZorkGrandInquisitorLocations.PLANETFALL: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "pp1j"),),
        archipelago_id=LOCATION_OFFSET + 5,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE_JACKS_SHOP,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.MAGIC_FOREVER: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "pc1e"), (10304, 1), (5221, 1)),
        archipelago_id=LOCATION_OFFSET + 6,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorEvents.LANTERN_DALBOZ_ACCESSIBLE,
            ZorkGrandInquisitorItems.ROPE,
        ),
    ),
    ZorkGrandInquisitorLocations.IN_CASE_OF_ADVENTURE: ZorkGrandInquisitorLocationData(
        game_state_trigger=((12931, 1),),
        archipelago_id=LOCATION_OFFSET + 7,
        region=ZorkGrandInquisitorRegions.CROSSROADS,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.HAMMER,),
    ),
    ZorkGrandInquisitorLocations.INTO_THE_FOLIAGE: ZorkGrandInquisitorLocationData(
        game_state_trigger=((13060, 1),),
        archipelago_id=LOCATION_OFFSET + 8,
        region=ZorkGrandInquisitorRegions.CROSSROADS,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SWORD,),
    ),
    ZorkGrandInquisitorLocations.IN_MAGIC_WE_TRUST: ZorkGrandInquisitorLocationData(
        game_state_trigger=((13062, 1),),
        archipelago_id=LOCATION_OFFSET + 9,
        region=ZorkGrandInquisitorRegions.CROSSROADS,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SPELL_REZROV,),
    ),
    ZorkGrandInquisitorLocations.GUE_TECH_ENTRANCE_EXAM: ZorkGrandInquisitorLocationData(
        game_state_trigger=((11082, 1), (11307, 1), (11536, 1)),
        archipelago_id=LOCATION_OFFSET + 10,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.A_SMALLWAY: ZorkGrandInquisitorLocationData(
        game_state_trigger=((11777, 1),),
        archipelago_id=LOCATION_OFFSET + 11,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SPELL_IGRAM,),
    ),
    ZorkGrandInquisitorLocations.ARTIFACTS_EXPLAINED: ZorkGrandInquisitorLocationData(
        game_state_trigger=((11787, 1), (11788, 1), (11789, 1)),
        archipelago_id=LOCATION_OFFSET + 12,
        region=ZorkGrandInquisitorRegions.GUE_TECH_HALLWAY,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.HEY_FREE_DIRT: ZorkGrandInquisitorLocationData(
        game_state_trigger=((11747, 1),),
        archipelago_id=LOCATION_OFFSET + 13,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SHOVEL,),
    ),
    ZorkGrandInquisitorLocations.THE_UNDERGROUND_UNDERGROUND: ZorkGrandInquisitorLocationData(
        game_state_trigger=((13167, 1),),
        archipelago_id=LOCATION_OFFSET + 14,
        region=ZorkGrandInquisitorRegions.CROSSROADS,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SUBWAY_TOKEN,),
    ),
    ZorkGrandInquisitorLocations.ENJOY_YOUR_TRIP: ZorkGrandInquisitorLocationData(
        game_state_trigger=((13743, 1),),
        archipelago_id=LOCATION_OFFSET + 15,
        region=ZorkGrandInquisitorRegions.SUBWAY_CROSSROADS,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SPELL_KENDALL,),
    ),
    ZorkGrandInquisitorLocations.OLD_SCRATCH_WINNER: ZorkGrandInquisitorLocationData(
        game_state_trigger=((4512, 32),),
        archipelago_id=LOCATION_OFFSET + 16,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,  # This can be done anywhere if the item requirement is met
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.OLD_SCRATCH_CARD,),
    ),
    ZorkGrandInquisitorLocations.GETTING_SOME_CHANGE: ZorkGrandInquisitorLocationData(
        game_state_trigger=((12892, 1),),
        archipelago_id=LOCATION_OFFSET + 17,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorEvents.ZORKMID_BILL_ACCESSIBLE,),
    ),
    ZorkGrandInquisitorLocations.NOOOOOOOOOOOOO: ZorkGrandInquisitorLocationData(
        game_state_trigger=((12706, 1),),
        archipelago_id=LOCATION_OFFSET + 18,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.POUCH_OF_ZORKMIDS,),
    ),
    ZorkGrandInquisitorLocations.SUCKING_ROCKS: ZorkGrandInquisitorLocationData(
        game_state_trigger=((12859, 1),),
        archipelago_id=LOCATION_OFFSET + 19,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorEvents.ZORK_ROCKS_SUCKABLE,
            ZorkGrandInquisitorItems.PERMA_SUCK_MACHINE,
        ),
    ),
    ZorkGrandInquisitorLocations.CRISIS_AVERTED: ZorkGrandInquisitorLocationData(
        game_state_trigger=((11769, 1),),
        archipelago_id=LOCATION_OFFSET + 20,
        region=ZorkGrandInquisitorRegions.GUE_TECH_HALLWAY,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorEvents.ZORK_ROCKS_ACTIVATED,),
    ),
    ZorkGrandInquisitorLocations.DUNCE_LOCKER: ZorkGrandInquisitorLocationData(
        game_state_trigger=((11851, 1),),
        archipelago_id=LOCATION_OFFSET + 21,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.POUCH_OF_ZORKMIDS,),
    ),
    ZorkGrandInquisitorLocations.BEBURTT_DEMYSTIFIED: ZorkGrandInquisitorLocationData(
        game_state_trigger=((16315, 1),),
        archipelago_id=LOCATION_OFFSET + 22,
        region=ZorkGrandInquisitorRegions.GUE_TECH_HALLWAY,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorEvents.DUNCE_LOCKER_OPENABLE,
            ZorkGrandInquisitorItems.SPELL_KENDALL,
        ),
    ),
    ZorkGrandInquisitorLocations.SOUVENIR: ZorkGrandInquisitorLocationData(
        game_state_trigger=((13408, 1),),
        archipelago_id=LOCATION_OFFSET + 23,
        region=ZorkGrandInquisitorRegions.SUBWAY_FLOOD_CONTROL_DAM,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.POUCH_OF_ZORKMIDS,),
    ),
    ZorkGrandInquisitorLocations.BEAUTIFUL_THATS_PLENTY: ZorkGrandInquisitorLocationData(
        game_state_trigger=((13278, 1),),
        archipelago_id=LOCATION_OFFSET + 24,
        region=ZorkGrandInquisitorRegions.SUBWAY_FLOOD_CONTROL_DAM,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SPELL_THROCK,),
    ),
    ZorkGrandInquisitorLocations.USELESS_BUT_FUN: ZorkGrandInquisitorLocationData(
        game_state_trigger=((14321, 1),),
        archipelago_id=LOCATION_OFFSET + 25,
        region=ZorkGrandInquisitorRegions.SUBWAY_FLOOD_CONTROL_DAM,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SPELL_GOLGATEM,),
    ),
    ZorkGrandInquisitorLocations.NATIONAL_TREASURE: ZorkGrandInquisitorLocationData(
        game_state_trigger=((14318, 1),),
        archipelago_id=LOCATION_OFFSET + 26,
        region=ZorkGrandInquisitorRegions.SUBWAY_FLOOD_CONTROL_DAM,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SPELL_REZROV,),
    ),
    ZorkGrandInquisitorLocations.YOU_GAINED_86_EXPERIENCE_POINTS: ZorkGrandInquisitorLocationData(
        game_state_trigger=((16342, 1),),
        archipelago_id=LOCATION_OFFSET + 27,
        region=ZorkGrandInquisitorRegions.SPELL_LAB_BRIDGE,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SWORD,),
    ),
    ZorkGrandInquisitorLocations.I_LIKE_YOUR_STYLE: ZorkGrandInquisitorLocationData(
        game_state_trigger=((16374, 1),),
        archipelago_id=LOCATION_OFFSET + 28,
        region=ZorkGrandInquisitorRegions.SPELL_LAB_BRIDGE,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorEvents.DAM_DESTROYED,
            ZorkGrandInquisitorItems.SPELL_GOLGATEM,
        ),
    ),
    ZorkGrandInquisitorLocations.IMBUE_BEBURTT: ZorkGrandInquisitorLocationData(
        game_state_trigger=((194, 1),),
        archipelago_id=LOCATION_OFFSET + 29,
        region=ZorkGrandInquisitorRegions.SPELL_LAB,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.UNLOCKED_BLANK_SCROLL_BOX_ACCESS,),
    ),
    ZorkGrandInquisitorLocations.UMBRELLA_FLOWERS: ZorkGrandInquisitorLocationData(
        game_state_trigger=((12926, 1),),
        archipelago_id=LOCATION_OFFSET + 30,
        region=ZorkGrandInquisitorRegions.CROSSROADS,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorEvents.KNOWS_BEBURTT,),
    ),
    ZorkGrandInquisitorLocations.PROZORKED: ZorkGrandInquisitorLocationData(
        game_state_trigger=((4115, 1),),
        archipelago_id=LOCATION_OFFSET + 31,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.PROZORK_TABLET,),
    ),
    ZorkGrandInquisitorLocations.NOTHIN_LIKE_A_GOOD_STOGIE: ZorkGrandInquisitorLocationData(
        game_state_trigger=((4237, 1),),
        archipelago_id=LOCATION_OFFSET + 32,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorEvents.CIGAR_ACCESSIBLE,),
    ),
    ZorkGrandInquisitorLocations.WANT_SOME_RYE_COURSE_YA_DO: ZorkGrandInquisitorLocationData(
        game_state_trigger=((4034, 1),),
        archipelago_id=LOCATION_OFFSET + 33,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorEvents.DOOR_SMOKED_CIGAR,
            ZorkGrandInquisitorItems.MEAD_LIGHT,
            ZorkGrandInquisitorItems.ZIMDOR_SCROLL,
        ),
    ),
    ZorkGrandInquisitorLocations.OUTSMART_THE_QUELBEES: ZorkGrandInquisitorLocationData(
        game_state_trigger=((4241, 1),),
        archipelago_id=LOCATION_OFFSET + 34,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorItems.HUNGUS_LARD,
            ZorkGrandInquisitorItems.SWORD,
        ),
    ),
    ZorkGrandInquisitorLocations.PLANTS_ARE_MANS_BEST_FRIEND: ZorkGrandInquisitorLocationData(
        game_state_trigger=((4224, 8),),
        archipelago_id=LOCATION_OFFSET + 35,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorItems.SPELL_THROCK,
            ZorkGrandInquisitorItems.SNAPDRAGON,
            ZorkGrandInquisitorItems.HAMMER,
        ),
    ),
    ZorkGrandInquisitorLocations.REASSEMBLE_SNAVIG: ZorkGrandInquisitorLocationData(
        game_state_trigger=((4512, 98),),
        archipelago_id=LOCATION_OFFSET + 36,
        region=ZorkGrandInquisitorRegions.DM_LAIR_INTERIOR,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorEvents.HAS_HALF_OF_SNAVIG,),
    ),
    ZorkGrandInquisitorLocations.WOW_IVE_NEVER_GONE_INSIDE_HIM_BEFORE: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "dc10"), (1596, 1)),
        archipelago_id=LOCATION_OFFSET + 37,
        region=ZorkGrandInquisitorRegions.WALKING_CASTLE,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.SNAVIG_REPAIRED: ZorkGrandInquisitorLocationData(
        game_state_trigger=((201, 1),),
        archipelago_id=LOCATION_OFFSET + 38,
        region=ZorkGrandInquisitorRegions.SPELL_LAB,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorEvents.HAS_REPAIRABLE_SNAVIG,),
    ),
    ZorkGrandInquisitorLocations.WHITE_HOUSE_TIME_TUNNEL: ZorkGrandInquisitorLocationData(
        game_state_trigger=((4983, 1),),
        archipelago_id=LOCATION_OFFSET + 39,
        region=ZorkGrandInquisitorRegions.DM_LAIR_INTERIOR,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SPELL_NARWILE,),
    ),
    ZorkGrandInquisitorLocations.HAVE_A_HELL_OF_A_DAY: ZorkGrandInquisitorLocationData(
        game_state_trigger=((8443, 1),),
        archipelago_id=LOCATION_OFFSET + 40,
        region=ZorkGrandInquisitorRegions.HADES_SHORE,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.I_HOPE_YOU_CAN_CLIMB_UP_THERE: ZorkGrandInquisitorLocationData(
        game_state_trigger=((9637, 1),),
        archipelago_id=LOCATION_OFFSET + 41,
        region=ZorkGrandInquisitorRegions.SUBWAY_MONASTERY,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorItems.SWORD,
            ZorkGrandInquisitorEvents.ROPE_GLORFABLE,
        ),
    ),
    ZorkGrandInquisitorLocations.PORT_FOOZLE_TIME_TUNNEL: ZorkGrandInquisitorLocationData(
        game_state_trigger=((9404, 1),),
        archipelago_id=LOCATION_OFFSET + 42,
        region=ZorkGrandInquisitorRegions.MONASTERY,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(
            ZorkGrandInquisitorItems.LARGE_TELEGRAPH_HAMMER,
            ZorkGrandInquisitorItems.SPELL_NARWILE,
        ),
    ),
    ZorkGrandInquisitorLocations.WE_GOT_A_HIGH_ROLLER: ZorkGrandInquisitorLocationData(
        game_state_trigger=((15472, 1),),
        archipelago_id=LOCATION_OFFSET + 43,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE_PAST,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.STRIP_GRUE_FIRE_WATER: ZorkGrandInquisitorLocationData(
        game_state_trigger=((14511, 1), (14524, 5)),
        archipelago_id=LOCATION_OFFSET + 44,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE_PAST,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.OPEN_THE_GATES_OF_HELL: ZorkGrandInquisitorLocationData(
        game_state_trigger=((8730, 1),),
        archipelago_id=LOCATION_OFFSET + 45,
        region=ZorkGrandInquisitorRegions.HADES,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorEvents.KNOWS_SNAVIG,),
    ),
    ZorkGrandInquisitorLocations.DRAGON_ARCHIPELAGO_TIME_TUNNEL: ZorkGrandInquisitorLocationData(
        game_state_trigger=((9216, 1),),
        archipelago_id=LOCATION_OFFSET + 46,
        region=ZorkGrandInquisitorRegions.HADES_BEYOND_GATES,
        tags=(ZorkGrandInquisitorTags.CORE,),
        requirements=(ZorkGrandInquisitorItems.SPELL_NARWILE,),
    ),
    ZorkGrandInquisitorLocations.OH_DEAR_GOD_ITS_A_DRAGON: ZorkGrandInquisitorLocationData(
        game_state_trigger=((1300, 1),),
        archipelago_id=LOCATION_OFFSET + 47,
        region=ZorkGrandInquisitorRegions.DRAGON_ARCHIPELAGO,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.THAR_SHE_BLOWS: ZorkGrandInquisitorLocationData(
        game_state_trigger=((1311, 1), (1312, 1)),
        archipelago_id=LOCATION_OFFSET + 48,
        region=ZorkGrandInquisitorRegions.DRAGON_ARCHIPELAGO,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.BROG_DO_GOOD: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "sg60"),),
        archipelago_id=LOCATION_OFFSET + 49,
        region=ZorkGrandInquisitorRegions.WHITE_HOUSE,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    ZorkGrandInquisitorLocations.BROG_MUCH_BETTER_AT_THIS_GAME: ZorkGrandInquisitorLocationData(
        game_state_trigger=((15715, 1),),
        archipelago_id=LOCATION_OFFSET + 50,
        region=ZorkGrandInquisitorRegions.WHITE_HOUSE,
        tags=(ZorkGrandInquisitorTags.CORE,),
    ),
    # Deathsanity
    ZorkGrandInquisitorLocations.DEATH_ARRESTED_WITH_JACK: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 1)),
        archipelago_id=LOCATION_OFFSET + 100 + 0,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorEvents.CIGAR_ACCESSIBLE,),
    ),
    ZorkGrandInquisitorLocations.DEATH_EATEN_BY_A_GRUE: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 18)),
        archipelago_id=LOCATION_OFFSET + 100 + 1,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorItems.ROPE,),
    ),
    ZorkGrandInquisitorLocations.DEATH_JUMPED_IN_BOTTOMLESS_PIT: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 3)),
        archipelago_id=LOCATION_OFFSET + 100 + 2,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
    ),
    ZorkGrandInquisitorLocations.DEATH_STEPPED_INTO_THE_INFINITE: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 4)),
        archipelago_id=LOCATION_OFFSET + 100 + 3,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorItems.SPELL_IGRAM,),
    ),
    ZorkGrandInquisitorLocations.DEATH_TOTEMIZED_PERMANENTLY: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, (5, 6, 7, 8, 13))),
        archipelago_id=LOCATION_OFFSET + 100 + 4,
        region=ZorkGrandInquisitorRegions.MONASTERY,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
    ),
    ZorkGrandInquisitorLocations.DEATH_TOTEMIZED: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, (9, 32, 33))),
        archipelago_id=LOCATION_OFFSET + 100 + 5,
        region=ZorkGrandInquisitorRegions.MONASTERY,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
    ),
    ZorkGrandInquisitorLocations.DEATH_YOURE_NOT_CHARON: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 10)),
        archipelago_id=LOCATION_OFFSET + 100 + 6,
        region=ZorkGrandInquisitorRegions.HADES,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorEvents.KNOWS_SNAVIG,),
    ),
    ZorkGrandInquisitorLocations.DEATH_SWALLOWED_BY_A_DRAGON: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 11)),
        archipelago_id=LOCATION_OFFSET + 100 + 7,
        region=ZorkGrandInquisitorRegions.DRAGON_ARCHIPELAGO,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
    ),
    ZorkGrandInquisitorLocations.DEATH_ZORK_ROCKS_EXPLODED: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 19)),
        archipelago_id=LOCATION_OFFSET + 100 + 9,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorEvents.ZORK_ROCKS_ACTIVATED,),
    ),
    ZorkGrandInquisitorLocations.DEATH_ATTACKED_THE_QUELBEES: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 20)),
        archipelago_id=LOCATION_OFFSET + 100 + 10,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorItems.SWORD,),
    ),
    ZorkGrandInquisitorLocations.DEATH_CLIMBED_OUT_OF_THE_WELL: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 21)),
        archipelago_id=LOCATION_OFFSET + 100 + 11,
        region=ZorkGrandInquisitorRegions.CROSSROADS,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
    ),
    ZorkGrandInquisitorLocations.DEATH_LOST_SOUL_TO_OLD_SCRATCH: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 23)),
        archipelago_id=LOCATION_OFFSET + 100 + 12,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorItems.OLD_SCRATCH_CARD,),
    ),
    ZorkGrandInquisitorLocations.DEATH_OUTSMARTED_BY_THE_QUELBEES: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 29)),
        archipelago_id=LOCATION_OFFSET + 100 + 13,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorItems.HUNGUS_LARD,),
    ),
    ZorkGrandInquisitorLocations.DEATH_SLICED_UP_BY_THE_INVISIBLE_GUARD: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 30)),
        archipelago_id=LOCATION_OFFSET + 100 + 14,
        region=ZorkGrandInquisitorRegions.SPELL_LAB_BRIDGE,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
    ),
    ZorkGrandInquisitorLocations.DEATH_THROCKED_THE_GRASS: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 34)),
        archipelago_id=LOCATION_OFFSET + 100 + 15,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
        requirements=(ZorkGrandInquisitorItems.SPELL_THROCK,),
    ),
    ZorkGrandInquisitorLocations.DEATH_LOST_GAME_OF_STRIP_GRUE_FIRE_WATER: ZorkGrandInquisitorLocationData(
        game_state_trigger=(("location", "gjde"), (2201, 37)),
        archipelago_id=LOCATION_OFFSET + 100 + 16,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE_PAST,
        tags=(ZorkGrandInquisitorTags.DEATHSANITY,),
    ),
    # Events
    ZorkGrandInquisitorEvents.CIGAR_ACCESSIBLE: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        requirements=(ZorkGrandInquisitorItems.LANTERN,),
        event_item_name=ZorkGrandInquisitorEvents.CIGAR_ACCESSIBLE.value,
    ),
    ZorkGrandInquisitorEvents.LANTERN_DALBOZ_ACCESSIBLE: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        requirements=(ZorkGrandInquisitorEvents.CIGAR_ACCESSIBLE,),
        event_item_name=ZorkGrandInquisitorEvents.LANTERN_DALBOZ_ACCESSIBLE.value,
    ),
    ZorkGrandInquisitorEvents.ZORKMID_BILL_ACCESSIBLE: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.PORT_FOOZLE,
        requirements=(ZorkGrandInquisitorItems.OLD_SCRATCH_CARD,),
        event_item_name=ZorkGrandInquisitorEvents.ZORKMID_BILL_ACCESSIBLE.value,
    ),
    ZorkGrandInquisitorEvents.ZORK_ROCKS_SUCKABLE: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        requirements=(ZorkGrandInquisitorItems.POUCH_OF_ZORKMIDS,),
        event_item_name=ZorkGrandInquisitorEvents.ZORK_ROCKS_SUCKABLE.value,
    ),
    ZorkGrandInquisitorEvents.ZORK_ROCKS_ACTIVATED: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        requirements=(
            ZorkGrandInquisitorItems.ZORK_ROCKS,
            ZorkGrandInquisitorItems.POUCH_OF_ZORKMIDS,
        ),
        event_item_name=ZorkGrandInquisitorEvents.ZORK_ROCKS_ACTIVATED.value,
    ),
    ZorkGrandInquisitorEvents.DUNCE_LOCKER_OPENABLE: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.GUE_TECH,
        requirements=(ZorkGrandInquisitorItems.POUCH_OF_ZORKMIDS,),
        event_item_name=ZorkGrandInquisitorEvents.DUNCE_LOCKER_OPENABLE.value,
    ),
    ZorkGrandInquisitorEvents.DAM_DESTROYED: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.SUBWAY_FLOOD_CONTROL_DAM,
        requirements=(ZorkGrandInquisitorItems.SPELL_REZROV,),
        event_item_name=ZorkGrandInquisitorEvents.DAM_DESTROYED.value,
    ),
    ZorkGrandInquisitorEvents.KNOWS_BEBURTT: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.SPELL_LAB,
        requirements=(ZorkGrandInquisitorItems.UNLOCKED_BLANK_SCROLL_BOX_ACCESS,),
        event_item_name=ZorkGrandInquisitorEvents.KNOWS_BEBURTT.value,
    ),
    ZorkGrandInquisitorEvents.DOOR_SMOKED_CIGAR: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        requirements=(ZorkGrandInquisitorEvents.CIGAR_ACCESSIBLE,),
        event_item_name=ZorkGrandInquisitorEvents.DOOR_SMOKED_CIGAR.value,
    ),
    ZorkGrandInquisitorEvents.DOOR_DRANK_MEAD: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        requirements=(
            ZorkGrandInquisitorEvents.DOOR_SMOKED_CIGAR,
            ZorkGrandInquisitorItems.MEAD_LIGHT,
            ZorkGrandInquisitorItems.ZIMDOR_SCROLL,
        ),
        event_item_name=ZorkGrandInquisitorEvents.DOOR_DRANK_MEAD.value,
    ),
    ZorkGrandInquisitorEvents.HAS_HALF_OF_SNAVIG: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.DM_LAIR,
        requirements=(
            ZorkGrandInquisitorItems.SPELL_THROCK,
            ZorkGrandInquisitorItems.SNAPDRAGON,
            ZorkGrandInquisitorItems.HAMMER,
        ),
        event_item_name=ZorkGrandInquisitorEvents.HAS_HALF_OF_SNAVIG.value,
    ),
    ZorkGrandInquisitorEvents.HAS_REPAIRABLE_SNAVIG: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.DM_LAIR_INTERIOR,
        requirements=(ZorkGrandInquisitorEvents.HAS_HALF_OF_SNAVIG,),
        event_item_name=ZorkGrandInquisitorEvents.HAS_REPAIRABLE_SNAVIG.value,
    ),
    ZorkGrandInquisitorEvents.KNOWS_SNAVIG: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.SPELL_LAB,
        requirements=(ZorkGrandInquisitorEvents.HAS_REPAIRABLE_SNAVIG,),
        event_item_name=ZorkGrandInquisitorEvents.KNOWS_SNAVIG.value,
    ),
    ZorkGrandInquisitorEvents.ROPE_GLORFABLE: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.CROSSROADS,
        requirements=(ZorkGrandInquisitorItems.SPELL_GLORF,),
        event_item_name=ZorkGrandInquisitorEvents.ROPE_GLORFABLE.value,
    ),
    ZorkGrandInquisitorEvents.VICTORY: ZorkGrandInquisitorLocationData(
        game_state_trigger=None,
        archipelago_id=None,
        region=ZorkGrandInquisitorRegions.ENDGAME,
        event_item_name=ZorkGrandInquisitorEvents.VICTORY.value,
    )
}