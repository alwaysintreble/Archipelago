from typing import TYPE_CHECKING, Any, Dict, Set

from Utils import int16_as_bytes
from NetUtils import ClientStatus
from worlds.AutoBizHawkClient import BizHawkClient

from .data import data, config
from .options import Goal

if TYPE_CHECKING:
    from BizHawkClient import BizHawkClientContext
else:
    BizHawkClientContext = Any


IS_CHAMPION_FLAG = data.constants["FLAG_IS_CHAMPION"]
DEFEATED_STEVEN_FLAG = data.constants["TRAINER_FLAGS_START"] + data.constants["TRAINER_STEVEN"]
DEFEATED_NORMAN_FLAG = data.constants["TRAINER_FLAGS_START"] + data.constants["TRAINER_NORMAN_1"]

TRACKER_EVENT_FLAGS = [
    "FLAG_DEFEATED_RUSTBORO_GYM",
    "FLAG_DEFEATED_DEWFORD_GYM",
    "FLAG_DEFEATED_MAUVILLE_GYM",
    "FLAG_DEFEATED_LAVARIDGE_GYM",
    "FLAG_DEFEATED_PETALBURG_GYM",
    "FLAG_DEFEATED_FORTREE_GYM",
    "FLAG_DEFEATED_MOSSDEEP_GYM",
    "FLAG_DEFEATED_SOOTOPOLIS_GYM",
    "FLAG_RECEIVED_POKENAV",                            # Talk to Mr. Stone
    "FLAG_DELIVERED_STEVEN_LETTER",
    "FLAG_DELIVERED_DEVON_GOODS",
    "FLAG_HIDE_ROUTE_119_TEAM_AQUA",                    # Clear Weather Institute
    "FLAG_MET_ARCHIE_METEOR_FALLS",                     # Magma steals meteorite
    "FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT",              # Clear Magma Hideout
    "FLAG_MET_TEAM_AQUA_HARBOR",                        # Aqua steals submarine
    "FLAG_TEAM_AQUA_ESCAPED_IN_SUBMARINE",              # Clear Aqua Hideout
    "FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_MAGMA_NOTE",  # Clear Space Center
    "FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN",
    "FLAG_HIDE_SKY_PILLAR_TOP_RAYQUAZA",                # Rayquaza departs for Sootopolis
    "FLAG_OMIT_DIVE_FROM_STEVEN_LETTER",                # Steven gives Dive HM (clears seafloor cavern grunt)
    "FLAG_IS_CHAMPION",
]


class PokemonEmeraldClient(BizHawkClient):
    game = "Pokemon Emerald"
    system = "GBA"
    local_checked_locations: Set[int]
    local_set_events: Dict[str, bool]
    goal_flag: int

    def __init__(self) -> None:
        super().__init__()
        self.local_checked_locations = set()
        self.local_set_events = {}
        self.goal_flag = IS_CHAMPION_FLAG

    async def validate_rom(self, ctx: BizHawkClientContext) -> bool:
        from BizHawkClient import bizhawk_read

        try:
            game_name = bytes(await bizhawk_read(ctx, 0x108, 23, "ROM")).decode('ascii')
            if game_name != "pokemon emerald version":
                return False
        except UnicodeDecodeError:
            return False

        ctx.game = self.game
        ctx.items_handling = 0b001
        ctx.want_slot_data = True
        return True

    async def game_watcher(self, ctx: BizHawkClientContext) -> None:
        from BizHawkClient import RequestFailedError, bizhawk_read, bizhawk_read_multiple, bizhawk_write_multiple, bizhawk_lock, bizhawk_unlock
        from CommonClient import logger

        if ctx.slot_data is not None:
            if ctx.slot_data["goal"] == Goal.option_champion:
                self.goal_flag = IS_CHAMPION_FLAG
            elif ctx.slot_data["goal"] == Goal.option_steven:
                self.goal_flag = DEFEATED_STEVEN_FLAG
            elif ctx.slot_data["goal"] == Goal.option_norman:
                self.goal_flag = DEFEATED_NORMAN_FLAG

        try:
            # Read slot name and send Connect if connected to server
            if ctx.server is not None and ctx.auth is None:
                slot_name_raw = await bizhawk_read(ctx, data.rom_addresses["gArchipelagoInfo"], 64, "ROM")
                try:
                    ctx.auth = bytes([byte for byte in slot_name_raw if byte != 0]).decode("utf-8")
                except UnicodeDecodeError:
                    logger.info("Could not read slot name from ROM. Are you sure this ROM matches this client version?")
                    return
                await ctx.send_connect()

            await bizhawk_lock(ctx)  # Lock to check if in the overworld, get save data address, and read save data

            # Check if in overworld
            cb2_value = int.from_bytes(await bizhawk_read(ctx, data.ram_addresses["gMain"] + 4, 4, "System Bus"), "little")
            if cb2_value == (data.ram_addresses["CB2_Overworld"] + 1):
                save_block_address = int.from_bytes(await bizhawk_read(ctx, data.ram_addresses["gSaveBlock1Ptr"], 4, "System Bus"), "little")

                flag_bytes, num_received_items_bytes = await bizhawk_read_multiple(ctx, [
                    [save_block_address + 0x1450, 0x12C, "System Bus"]
                    [save_block_address + 0x3778, 2, "System Bus"]
                ])
                num_received_items = int.from_bytes(num_received_items_bytes, "little")

                # Try to fill the received item struct with the next item
                if num_received_items < len(ctx.items_received):
                    is_filled = (await bizhawk_read(ctx, data.ram_addresses["gArchipelagoReceivedItem"] + 4, 1, "System Bus"))[0] == 0

                    await bizhawk_unlock(ctx)

                    # If the item struct is still full, do nothing
                    if is_filled:
                        next_item = ctx.items_received[num_received_items]
                        await bizhawk_write_multiple(ctx, [
                            [data.ram_addresses["gArchipelagoReceivedItem"] + 0, int16_as_bytes(next_item.item - config["ap_offset"]), "System Bus"],
                            [data.ram_addresses["gArchipelagoReceivedItem"] + 2, int16_as_bytes(num_received_items + 1), "System Bus"],
                            [data.ram_addresses["gArchipelagoReceivedItem"] + 4, [1], "System Bus"],
                            [data.ram_addresses["gArchipelagoReceivedItem"] + 5, [next_item.flags & 1], "System Bus"],
                        ])
                else:
                    await bizhawk_unlock(ctx)

                game_clear = False
                local_checked_locations = set()
                event_flag_map = {data.constants[flag_name]: flag_name for flag_name in TRACKER_EVENT_FLAGS}
                local_set_events = {flag_name: False for flag_name in TRACKER_EVENT_FLAGS}

                # Check set flags
                for byte_i, byte in enumerate(flag_bytes):
                    for i in range(8):
                        if byte & (1 << i) != 0:
                            flag_id = byte_i * 8 + i

                            location_id = flag_id + config["ap_offset"]
                            if location_id in ctx.server_locations:
                                local_checked_locations.add(location_id)

                            if flag_id == self.goal_flag:
                                game_clear = True

                            if flag_id in event_flag_map:
                                local_set_events[event_flag_map[flag_id]] = True

                # Send locations
                if local_checked_locations != self.local_checked_locations:
                    self.local_checked_locations = local_checked_locations

                    if local_checked_locations is not None:
                        await ctx.send_msgs([{
                            "cmd": "LocationChecks",
                            "locations": list(local_checked_locations)
                        }])

                # Send game clear
                if not ctx.finished_game and game_clear:
                    await ctx.send_msgs([{
                        "cmd": "StatusUpdate",
                        "status": ClientStatus.CLIENT_GOAL
                    }])

                # Send tracker event flags
                if local_set_events != self.local_set_events and ctx.slot is not None:
                    event_bitfield = 0
                    for i, flag_name in enumerate(TRACKER_EVENT_FLAGS):
                        if local_set_events[flag_name]:
                            event_bitfield |= 1 << i

                    await ctx.send_msgs([{
                        "cmd": "Set",
                        "key": f"pokemon_emerald_events_{ctx.team}_{ctx.slot}",
                        "default": 0,
                        "want_reply": False,
                        "operations": [{"operation": "replace", "value": event_bitfield}]
                    }])
                    self.local_set_events = local_set_events
            else:
                await bizhawk_unlock(ctx)
        except RequestFailedError:
            # Exit handler and return to main loop to reconnect
            pass
