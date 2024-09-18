import pkgutil
import typing

import Utils
from typing import Optional, Dict, List, Tuple, Union
import hashlib
import os
import struct

import settings
from worlds.Files import APProcedurePatch, APTokenMixin, APTokenTypes, APPatchExtension
import bsdiff4

from .aesthetics import kirby_target_palettes, get_palette_bytes, get_kirby_palette
from .regions import default_levels

if typing.TYPE_CHECKING:
    from . import K64World

K64UHASH = "d33e4254336383a17ff4728360562ada"

stage_locations: Dict[int, Tuple[int, int]] = {
    0x640001: (0, 0),
    0x640002: (0, 1),
    0x640003: (0, 2),
    0x640004: (1, 0),
    0x640005: (1, 1),
    0x640006: (1, 2),
    0x640007: (1, 3),
    0x640008: (2, 0),
    0x640009: (2, 1),
    0x64000A: (2, 2),
    0x64000B: (2, 3),
    0x64000C: (3, 0),
    0x64000D: (3, 1),
    0x64000E: (3, 2),
    0x64000F: (3, 3),
    0x640010: (4, 0),
    0x640011: (4, 1),
    0x640012: (4, 2),
    0x640013: (4, 3),
    0x640014: (5, 0),
    0x640015: (5, 1),
    0x640016: (5, 2),
    0x640200: (0, 3),
    0x640201: (1, 4),
    0x640202: (2, 4),
    0x640203: (3, 4),
    0x640204: (4, 4),
    0x640205: (5, 3),
}

stage_select_ptrs: Dict[int, Tuple[int, int, int, int]] = {  # un-cleared pal, uncleared, cleared pal, cleared
    0x640001: (0x99135C, 0x99138C, 0x9915F4, 0x991634),
    0x640002: (0x9918CC, 0x9918FC, 0x991AEC, 0x991B1C),
    0x640003: (0x991D0C, 0x991D3C, 0x991F2C, 0x991F5C),
    0x640004: (0x994AF4, 0x994B24, 0x994DB4, 0x994DE4),
    0x640005: (0x995074, 0x9950A4, 0x995334, 0x995364),
    0x640006: (0x9955F4, 0x995624, 0x9958B4, 0x9958E4),
    0x640007: (0x995B74, 0x995BA4, 0x995E34, 0x995E64),
    0x640008: (0x998F14, 0x998F44, 0x9991D4, 0x999204),
    0x640009: (0x999494, 0x9994C4, 0x999754, 0x999784),
    0x64000A: (0x999A14, 0x999A44, 0x999CD4, 0x999D04),
    0x64000B: (0x999F94, 0x999FC4, 0x99A254, 0x99A284),
    0x64000C: (0x99C494, 0x99C4C4, 0x99C754, 0x99C784),
    0x64000D: (0x99CA14, 0x99CA44, 0x99CCD4, 0x99CD04),
    0x64000E: (0x99CF94, 0x99CFC4, 0x99D254, 0x99D284),
    0x64000F: (0x99D514, 0x99D544, 0x99D7D4, 0x99D804),
    0x640010: (0x99FEC4, 0x99FEF4, 0x9A0184, 0x9A01B4),
    0x640011: (0x9A0444, 0x9A0474, 0x9A0704, 0x9A0734),
    0x640012: (0x9A09C4, 0x9A09F4, 0x9A0C84, 0x9A0CB4),
    0x640013: (0x9A0F44, 0x9A0F74, 0x9A1204, 0x9A1234),
    0x640014: (0x9A3804, 0x9A3834, 0x9A3B3C, 0x9A3B7C),
    0x640015: (0x9A3EC4, 0x9A3EF4, 0x9A4184, 0x9A41B4),
    0x640016: (0x9A4444, 0x9A4474, 0x9A477C, 0x9A47BC),
    0x640200: (0x99214C, 0x99217C, 0x99236C, 0x99239C),
    0x640201: (0x9960F4, 0x996124, 0x9963B4, 0x9963E4),
    0x640202: (0x99A514, 0x99A544, 0x99A7D4, 0x99A804),
    0x640203: (0x99DA94, 0x99DAC4, 0x99DD54, 0x99DD84),
    0x640204: (0x9A14C4, 0x9A14F4, 0x9A1784, 0x9A17B4),
    0x640205: (0x9A4B04, 0x9A4B34, 0x9A4DC4, 0x9A4DF4),
}

stage_select_vals: Dict[int, Tuple[int, int, int, int]] = {
    0x640001: (0x030221, 0x030220, 0x030223, 0x030222),
    0x640002: (0x030225, 0x030224, 0x030227, 0x030226),
    0x640003: (0x030229, 0x030228, 0x03022B, 0x03022A),
    0x640004: (0x03024F, 0x03024E, 0x030251, 0x030250),
    0x640005: (0x030253, 0x030252, 0x030255, 0x030254),
    0x640006: (0x030257, 0x030256, 0x030259, 0x030258),
    0x640007: (0x03025B, 0x03025A, 0x03025D, 0x03025C),
    0x640008: (0x03026C, 0x03026B, 0x03026E, 0x03026D),
    0x640009: (0x030270, 0x03026F, 0x030272, 0x030271),
    0x64000A: (0x030274, 0x030273, 0x030276, 0x030275),
    0x64000B: (0x030278, 0x030277, 0x03027A, 0x030279),
    0x64000C: (0x030284, 0x030283, 0x030286, 0x030285),
    0x64000D: (0x030288, 0x030287, 0x03028A, 0x030289),
    0x64000E: (0x03028C, 0x03028B, 0x03028E, 0x03028D),
    0x64000F: (0x030290, 0x03028F, 0x030292, 0x030291),
    0x640010: (0x0302A5, 0x0302A4, 0x0302A7, 0x0302A6),
    0x640011: (0x0302A9, 0x0302A8, 0x0302AB, 0x0302AA),
    0x640012: (0x0302AD, 0x0302AC, 0x0302AF, 0x0302AE),
    0x640013: (0x0302B1, 0x0302B0, 0x0302B3, 0x0302B2),
    0x640014: (0x0302C0, 0x0302BF, 0x0302C2, 0x0302C1),
    0x640015: (0x0302C4, 0x0302C3, 0x0302C6, 0x0302C5),
    0x640016: (0x0302C8, 0x0302C7, 0x0302CA, 0x0302C9),
    0x640200: (0x03022D, 0x03022C, 0x03022F, 0x03022E),
    0x640201: (0x03025F, 0x03025E, 0x030260, 0x030261),
    0x640202: (0x03027C, 0x03027B, 0x03027E, 0x03027D),
    0x640203: (0x030294, 0x030293, 0x030296, 0x030295),
    0x640204: (0x0302B5, 0x0302B4, 0x0302B7, 0x0302B6),
    0x640205: (0x0302CC, 0x0302CB, 0x0302CE, 0x0302CD),
}

stage_select_param_ptrs = {
    0x640001: [0x991388, 0x9913A8, 0x991630, 0x991638],
    0x640002: [0x9918F8, 0x991918, 0x991B18, 0x991B38],
    0x640003: [0x991D38, 0x991D58, 0x991F58, 0x991F78],
    0x640004: [0x994B20, 0x994B40, 0x994DE0, 0x994E00],
    0x640005: [0x9950A0, 0x9950C0, 0x995360, 0x995380],
    0x640006: [0x995620, 0x995640, 0x9958E0, 0x995900],
    0x640007: [0x995BA0, 0x995BC0, 0x995E60, 0x995E80],
    0x640008: [0x998F40, 0x998F60, 0x999200, 0x999220],
    0x640009: [0x9994C0, 0x9994E0, 0x999780, 0x9997A0],
    0x64000A: [0x999A40, 0x999A60, 0x999D00, 0x999D20],
    0x64000B: [0x999FC0, 0x999FE0, 0x99A280, 0x99A2A0],
    0x64000C: [0x99C4C0, 0x99C4E0, 0x99C780, 0x99C7A0],
    0x64000D: [0x99CA40, 0x99CA60, 0x99CD00, 0x99CD20],
    0x64000E: [0x99CFC0, 0x99CFE0, 0x99D280, 0x99D2A0],
    0x64000F: [0x99D540, 0x99D560, 0x99D800, 0x99D820],
    0x640010: [0x99FEF0, 0x99FF10, 0x9A01B0, 0x9A01D0],
    0x640011: [0x9A0470, 0x9A0490, 0x9A0730, 0x9A0750],
    0x640012: [0x9A09F0, 0x9A0A10, 0x9A0CB0, 0x9A0CD0],
    0x640013: [0x9A0F70, 0x9A0F90, 0x9A1230, 0x9A1250],
    0x640014: [0x9A3830, 0x9A3850, 0x9A3B78, 0x9A3B80],
    0x640015: [0x9A3EF0, 0x9A3F10, 0x9A41B0, 0x9A41D0],
    0x640016: [0x9A4470, 0x9A4490, 0x9A47B8, 0x9A47C0],
    0x640200: [0x992178, 0x992198, 0x992398, 0x9923B8],
    0x640201: [0x996120, 0x996140, 0x9963E0, 0x996400],
    0x640202: [0x99A540, 0x99A560, 0x99A800, 0x99A820],
    0x640203: [0x99DAC0, 0x99DAE0, 0x99DD80, 0x99DDA0],
    0x640204: [0x9A14F0, 0x9A1510, 0x9A17B0, 0x9A17D0],
    0x640205: [0x9A4B30, 0x9A4B50, 0x9A4DF0, 0x9A4E10],
}

stage_select_param_vals = {
    0x640001: [0xFD500000, 0xF5400800, 0xFD48003F, 0xF5481000],
    0x640002: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640003: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640004: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640005: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640006: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640007: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640008: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640009: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x64000A: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x64000B: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x64000C: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x64000D: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x64000E: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x64000F: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640010: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640011: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640012: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640013: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640014: [0xFD500000, 0xF5400800, 0xFD48003F, 0xF5481000],
    0x640015: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640016: [0xFD500000, 0xF5400800, 0xFD48003F, 0xF5481000],
    0x640200: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640201: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640202: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640203: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640204: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
    0x640205: [0xFD500000, 0xF5400800, 0xFD500000, 0xF5400800],
}


class RomData:
    def __init__(self, file: str, name: typing.Optional[str] = None):
        self.file = bytearray()
        self.read_from_file(file)
        self.name = name

    def read_byte(self, offset: int):
        return self.file[offset]

    def read_bytes(self, offset: int, length: int):
        return self.file[offset:offset + length]

    def write_byte(self, offset: int, value: int):
        self.file[offset] = value

    def write_bytes(self, offset: int, values):
        self.file[offset:offset + len(values)] = values

    def write_to_file(self, file: str):
        with open(file, 'wb') as outfile:
            outfile.write(self.file)

    def read_from_file(self, file: str):
        with open(file, 'rb') as stream:
            self.file = bytearray(stream.read())


class K64PatchExtension(APPatchExtension):
    game = "Kirby 64 - The Crystal Shards"
    @staticmethod
    def apply_basepatch(_: APProcedurePatch, rom: bytes):
        return bsdiff4.patch(rom, pkgutil.get_data(__name__, os.path.join("data", "k64_basepatch.bsdiff4")))


class K64ProcedurePatch(APProcedurePatch, APTokenMixin):
    hash = [K64UHASH]
    game = "Kirby 64 - The Crystal Shards"
    patch_file_ending = ".apk64cs"
    result_file_ending = ".z64"
    procedure = [
        ("apply_basepatch", []),
        ("apply_tokens", ["token_data.bin"])
    ]
    name: str = ""

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()

    def write_byte(self, offset: int, value: int):
        self.write_token(APTokenTypes.WRITE, offset, bytes([value]))

    def write_bytes(self, offset: int, values: Union[List[int], bytes]):
        self.write_token(APTokenTypes.WRITE, offset, bytes(values))


def patch_rom(world: "K64World", player: int, patch: K64ProcedurePatch):
    # now just apply slot data
    # first stage shuffle
    if world.stage_shuffle_enabled:
        for i in range(1, 7):
            stages = [stage_locations[world.player_levels[i][stage]] if stage < len(world.player_levels[i])
                      else (-1, -1) for stage in range(8)]
            patch.write_bytes(0x1FFF300 + ((i - 1) * 32), struct.pack(">iiiiiiii", *[stage[0] for stage in stages]))
            patch.write_bytes(0x1FFF450 + ((i - 1) * 32), struct.pack(">iiiiiiii", *[stage[1] for stage in stages]))
            for j in range(len(world.player_levels[i])):
                for value, addr in zip(stage_select_vals[world.player_levels[i][j]],
                                       stage_select_ptrs[default_levels[i][j]]):
                    patch.write_bytes(addr, struct.pack(">I", value))
                for k in range(4):
                    addr = stage_select_param_ptrs[world.player_levels[i][j]][k]
                    value = stage_select_param_vals[default_levels[i][j]][k]
                    if default_levels[i][j] in (0x640001, 0x640014, 0x640016):
                        if k == 2:
                            value = value | 0xF
                        elif k == 3:
                            patch.write_bytes(addr + 0x20, struct.pack(">I", value))
                    patch.write_bytes(addr, struct.pack(">I", value))

    patch.write_bytes(0x1FFF100, world.boss_requirements)

    if world.options.kirby_flavor_preset != world.options.kirby_flavor_preset.default:
        palette = get_palette_bytes(get_kirby_palette(world), [f"{i}" for i in range(1, 16)])
        for target in kirby_target_palettes:
            patch.write_bytes(target, palette)

    from Utils import __version__
    patch.name = bytearray(f'K64{__version__.replace(".", "")[0:3]}_{player}_{world.multiworld.seed:11}\0', 'utf8')[:21]
    patch.name.extend([0] * (21 - len(patch.name)))
    patch.write_bytes(0x1FFF200, patch.name)

    patch.write_byte(0x1FFF220, world.options.split_power_combos.value)
    patch.write_byte(0x1FFF221, world.options.death_link.value)
    patch.write_byte(0x1FFF222, world.options.goal_speed.value)
    level_counter = 0
    for level in world.player_levels:
        for stage in world.player_levels[level]:
            patch.write_bytes(0x1FFF230 + level_counter, struct.pack(">H", stage & 0xFFFF))
            level_counter += 2

    patch.write_file("token_data.bin", patch.get_token_binary())


def get_base_rom_bytes() -> bytes:
    rom_file: str = get_base_rom_path()
    base_rom_bytes: Optional[bytes] = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        base_rom_bytes = bytes(Utils.read_snes_rom(open(rom_file, "rb")))

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if basemd5.hexdigest() not in {K64UHASH}:
            raise Exception("Supplied Base Rom does not match known MD5 for US or JP release. "
                            "Get the correct game and version, then dump it")
        get_base_rom_bytes.base_rom_bytes = base_rom_bytes
    return base_rom_bytes


def get_base_rom_path(file_name: str = "") -> str:
    options = settings.get_settings()
    if not file_name:
        file_name = options["k64_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name
