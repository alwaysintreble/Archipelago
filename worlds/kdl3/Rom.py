import Utils
from typing import Optional
import hashlib
import os
import struct
from worlds.Files import APDeltaPatch
from .Aesthetics import get_palette_bytes, kirby_target_palettes, get_kirby_palette, gooey_target_palettes, get_gooey_palette
from .Compression import hal_decompress

KDL3UHASH = "201e7658f6194458a3869dde36bf8ec2"
KDL3JHASH = "b2f2d004ea640c3db66df958fce122b2"

level_pointers = {
    0x770001: 0x0084,
    0x770002: 0x009C,
    0x770003: 0x00B8,
    0x770004: 0x00D8,
    0x770005: 0x0104,
    0x770006: 0x0124,
    0x770007: 0x014C,
    0x770008: 0x0170,
    0x770009: 0x0190,
    0x77000A: 0x01B0,
    0x77000B: 0x01E8,
    0x77000C: 0x0218,
    0x77000D: 0x024C,
    0x77000E: 0x0270,
    0x77000F: 0x02A0,
    0x770010: 0x02C4,
    0x770011: 0x02EC,
    0x770012: 0x0314,
    0x770013: 0x03CC,
    0x770014: 0x0404,
    0x770015: 0x042C,
    0x770016: 0x044C,
    0x770017: 0x0478,
    0x770018: 0x049C,
    0x770019: 0x04E4,
    0x77001A: 0x0504,
    0x77001B: 0x0530,
    0x77001C: 0x0554,
    0x77001D: 0x05A8,
    0x77001E: 0x0640,
    0x770200: 0x0148,
    0x770201: 0x0248,
    0x770202: 0x03C8,
    0x770203: 0x04E0,
    0x770204: 0x06A4,
}

level_sprites = {
    0x19B2C6: 1827,
    0x1A195C: 1584,
    0x19F6F3: 1679,
    0x19DC8B: 1717,
    0x197900: 1872
}

stage_tiles = {
    0: [
        0, 1, 2,
        16, 17, 18,
        32, 33, 34,
        48, 49, 50
    ],
    1: [
        3, 4, 5,
        19, 20, 21,
        35, 36, 37,
        51, 52, 53
    ],
    2: [
        6, 7, 8,
        22, 23, 24,
        38, 39, 40,
        54, 55, 56
    ],
    3: [
        9, 10, 11,
        25, 26, 27,
        41, 42, 43,
        57, 58, 59,
    ],
    4: [
        12, 13, 64,
        28, 29, 65,
        44, 45, 66,
        60, 61, 67
    ],
    5: [
        14, 15, 68,
        30, 31, 69,
        46, 47, 70,
        62, 63, 71
    ]
}

stage_palettes = [0x60964, 0x60B64, 0x60D64, 0x60F64, 0x61164]


def handle_level_sprites(stages, sprites, palettes):
    palette_by_level = list()
    for palette in palettes:
        palette_by_level.extend(palette[10:16])
    for i in range(5):
        for j in range(6):
            palettes[i][10+j] = palette_by_level[stages[i][j]-1]
        palettes[i] = [x for palette in palettes[i] for x in palette]
    tiles_by_level = list()
    for spritesheet in sprites:
        decompressed = hal_decompress(spritesheet)
        tiles = [decompressed[i:i+32] for i in range(0, 2304, 32)]
        tiles_by_level.extend([[tiles[x] for x in stage_tiles[stage]] for stage in stage_tiles])
    for world in range(5):
        levels = [stages[world][x] - 1 for x in range(6)]
        world_tiles = [None for _ in range(72)]
        for i in range(6):
            for x in range(12):
                world_tiles[stage_tiles[i][x]] = tiles_by_level[levels[i]][x]
        sprites[world] = list()
        for tile in world_tiles:
            sprites[world].extend(tile)
        # insert our fake compression
        sprites[world][0:0] = [0xe3, 0xff]
        sprites[world][1026:1026] = [0xe3, 0xff]
        sprites[world][2052:2052] = [0xe0, 0xff]
        sprites[world].append(0xff)
    return sprites, palettes


class KDL3DeltaPatch(APDeltaPatch):
    hash = [KDL3UHASH, KDL3JHASH]
    game = "Kirby's Dream Land 3"
    patch_file_ending = ".apkdl3"

    @classmethod
    def get_source_data(cls) -> bytes:
        return get_base_rom_bytes()

    def patch(self, target: str):
        super().patch(target)
        rom = RomData(target)
        if rom.read_bytes(0x3D014, 1)[0] > 0:
            stages = [struct.unpack("HHHHHHH", rom.read_bytes(0x3D020 + x*14, 14)) for x in range(5)]
            palettes = [rom.read_bytes(full_pal, 512) for full_pal in stage_palettes]
            palettes = [[palette[i:i+32] for i in range(0, 512, 32)] for palette in palettes]
            sprites = [rom.read_bytes(offset, level_sprites[offset]) for offset in level_sprites]
            sprites, palettes = handle_level_sprites(stages, sprites, palettes)
            for addr, palette in zip(stage_palettes, palettes):
                rom.write_bytes(addr, palette)
            for addr, level_sprite in zip([0x1CA000, 0x1CA920, 0x1CB230, 0x1CBB40, 0x1CC450], sprites):
                rom.write_bytes(addr, level_sprite)
            rom.write_bytes(0x460A, [0x00, 0xA0, 0x39, 0x20, 0xA9, 0x39, 0x30, 0xB2, 0x39, 0x40, 0xBB, 0x39,
                                     0x50, 0xC4, 0x39])
            rom.write_to_file(target)




class RomData:
    def __init__(self, file, name=None):
        self.file = bytearray()
        self.read_from_file(file)
        self.name = name

    def read_bytes(self, offset, length):
        return self.file[offset:offset+length]

    def write_byte(self, offset, value):
        self.file[offset] = value

    def write_bytes(self, offset, values):
        self.file[offset:offset+len(values)] = values

    def write_to_file(self, file):
        with open(file, 'wb') as outfile:
            outfile.write(self.file)

    def read_from_file(self, file):
        with open(file, 'rb') as stream:
            self.file = bytearray(stream.read())


def patch_rom(multiworld, player, rom, heart_stars_required, boss_requirements, shuffled_levels):
    # increase BWRAM by 0x8000
    rom.write_byte(0x7FD8, 0x06)

    # hook BWRAM initialization for initializing our new BWRAM
    rom.write_bytes(0x33, [0x22, 0x00, 0x9E, 0x07, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, ])

    # Initialize BWRAM with ROM parameters
    rom.write_bytes(0x39E00, [0xA0, 0x01, 0x60, 0xA9, 0xFE, 0x1F, 0x54, 0x40, 0x40, 0xA2, 0x00, 0x00, 0xA0, 0x14, 0x00,
                              0xBD, 0x00, 0x81, 0xDF, 0xC0, 0xFF, 0x00, 0xD0, 0x06, 0xE8, 0x88, 0x30, 0x2C, 0x80, 0xF1,
                              0xA9, 0x00, 0x00, 0x8D, 0x00, 0x80, 0xA2, 0x00, 0x80, 0xA0, 0x01, 0x80, 0xA9, 0xFD, 0x7F,
                              0x54, 0x40, 0x40, 0xA2, 0x00, 0xD0, 0xA0, 0x00, 0x90, 0xA9, 0x00, 0x10, 0x54, 0x40, 0x07,
                              0xA2, 0xC0, 0xFF, 0xA0, 0x00, 0x81, 0xA9, 0x15, 0x00, 0x54, 0x40, 0x00, 0x6B, ])

    # Copy Ability
    rom.write_bytes(0x399A0, [0xB9, 0xF3, 0x54,  # LDA $54F3
                              0x48,  # PHA
                              0x0A,  # ASL
                              0xAA,  # TAX
                              0x68,  # PLA
                              0xDD, 0x20, 0x80,  # CMP $7F50, X
                              0xEA, 0xEA,  # NOP NOP
                              0xF0, 0x03,  # BEQ $0799B1
                              0xA9, 0x00, 0x00,  # LDA #$0000
                              0x99, 0xA9, 0x54,  # STA $54A9, Y
                              0x6B,  # RET
                              0xEA, 0xEA, 0xEA, 0xEA,  # NOPs to fill gap
                              0x48,  # PHA
                              0x0A,  # ASL
                              0xA8,  # TAX
                              0x68,  # PLA
                              0xD9, 0x20, 0x80,  # CMP $7F50, Y
                              0xEA,  # NOP
                              0xF0, 0x03,  # BEQ $0799C6
                              0xA9, 0x00, 0x00,  # LDA #$0000
                              0x9D, 0xA9, 0x54,  # STA $54A9, X
                              0x9D, 0xDF, 0x39,  # STA $39DF, X
                              0x6B,  # RET
                              ])

    # Kirby/Gooey Copy Ability
    rom.write_bytes(0x30518, [0x22, 0xA0, 0x99, 0x07, 0xEA, 0xEA, ])

    # Animal Copy Ability
    rom.write_bytes(0x507E8, [0x22, 0xB9, 0x99, 0x07, 0xEA, 0xEA, ])

    # Entity Spawn
    rom.write_bytes(0x21CD7, [0x22, 0x00, 0x9D, 0x07, ])

    # Check Spawn Animal
    rom.write_bytes(0x39D00, [0x48, 0xE0, 0x02, 0x00, 0xD0, 0x0C, 0xEB, 0x48, 0x0A, 0xA8, 0x68, 0x1A, 0xD9, 0x00, 0x80,
                              0xF0, 0x01, 0xE8, 0x7A, 0xA9, 0x99, 0x99, 0x6B, ])

    # Allow Purification
    rom.write_bytes(0xAFC8, [0x22, 0x00, 0x9A, 0x07,
                             0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, ])

    # Check Purification and Enable Sub-games
    rom.write_bytes(0x39A00, [0x8A, 0xC9, 0x00, 0x00, 0xF0, 0x03, 0x4A, 0x4A, 0x1A, 0xAA, 0xAD, 0x70, 0x80, 0x18, 0xCF,
                              0x0A, 0xD0, 0x07, 0x90, 0x28, 0xDA, 0xA9, 0x14, 0x00, 0x8D, 0x62, 0x7F, 0xAF, 0x12, 0xD0,
                              0x07, 0xC9, 0x00, 0x00, 0xF0, 0x11, 0xA9, 0x01, 0x00, 0xAE, 0x17, 0x36, 0x9D, 0xDD, 0x53,
                              0x9D, 0xDF, 0x53, 0x9D, 0xE1, 0x53, 0x80, 0x06, 0xA9, 0x01, 0x00, 0x8D, 0x00, 0x82, 0xFA,
                              0xAD, 0x70, 0x80, 0xDF, 0x00, 0xD0, 0x07, 0xB0, 0x02, 0x18, 0x6B, 0x38, 0x6B, ])

    # Check for Sound on Main Loop
    rom.write_bytes(0x6AE4, [0x22, 0x00, 0x9B, 0x07, 0xEA])

    # Play Sound Effect at given address
    rom.write_bytes(0x39B00, [0x85, 0xD4, 0xEE, 0x24, 0x35, 0xEA, 0xAD, 0x62, 0x7F, 0xF0, 0x07, 0x22, 0x27, 0xD9,
                              0x00, 0x9C, 0x62, 0x7F, 0x6B])

    # Dedede - Remove bad ending
    rom.write_byte(0xB013, 0x38)  # Change CLC to SEC

    # Heart Star Graphics Fix
    rom.write_bytes(0x39B50, [0xDA, 0x5A, 0xAE, 0x3F, 0x36, 0xAC, 0x41, 0x36, 0xE0, 0x00, 0x00, 0xF0, 0x09, 0x1A, 0x1A,
                              0x1A, 0x1A, 0x1A, 0x1A, 0xCA, 0x80, 0xF2, 0xC0, 0x00, 0x00, 0xF0, 0x04, 0x1A, 0x88, 0x80,
                              0xF7, 0x0A, 0xAA, 0xBF, 0x80, 0xD0, 0x07, 0xC9, 0x03, 0x00, 0xF0, 0x03, 0x18, 0x80, 0x01,
                              0x38, 0x7A, 0xFA, 0x6B, ])

    # Reroute Heart Star Graphic Check
    rom.write_bytes(0x4A01F, [0x22, 0x50, 0x9B, 0x07, 0xEA, 0xEA, 0xB0, ])  # 1-Ups
    rom.write_bytes(0x4A0AE, [0x22, 0x50, 0x9B, 0x07, 0xEA, 0xEA, 0x90, ])  # Heart Stars

    # reroute 5-6 miniboss music override
    rom.write_bytes(0x93238, [0x22, 0x80, 0x9F, 0x07, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xB0,
                              ])
    rom.write_bytes(0x39F80, [0xEA, 0xDA, 0x5A, 0xA9, 0x00, 0x00, 0xAE, 0x3F, 0x36, 0xAC, 0x41, 0x36, 0xE0, 0x00, 0x00,
                              0xF0, 0x0A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0xCA, 0x80, 0xF1, 0xC0, 0x00, 0x00,
                              0xF0, 0x04, 0x1A, 0x88, 0x80, 0xF7, 0x0A, 0xAA, 0xBF, 0x20, 0xD0, 0x07, 0xC9, 0x1E, 0x00,
                              0xF0, 0x03, 0x18, 0x80, 0x01, 0x38, 0x7A, 0xFA, 0x6B, 0xEA, ])
    # reroute zero eligibility
    rom.write_bytes(0x137B1, [0x00, 0x82, 0xC9, 0x01, ])

    # set goal on non-fast goal
    rom.write_bytes(0x14463, [0x22, 0x00, 0x9F, 0x07, 0xEA, 0xEA, ])
    rom.write_bytes(0x39F00, [0xDA, 0xAF, 0x12, 0xD0, 0x07, 0xC9, 0x00, 0x00, 0xF0, 0x11, 0xA9, 0x01, 0x00, 0xAE, 0x17,
                              0x36, 0x9D, 0xDD, 0x53, 0x9D, 0xDF, 0x53, 0x9D, 0xD1, 0x53, 0x80, 0x06, 0xA9, 0x01, 0x00,
                              0x8D, 0x00, 0x82, 0xFA, 0xA9, 0x06, 0x00, 0x8D, 0xC1, 0x5A, 0x6B, ])

    # set flag for completing a stage
    rom.write_bytes(0x143C7, [0x22, 0x80, 0xA0, 0x07, 0xEA, 0xEA, ])
    rom.write_bytes(0x3A080, [0xDA, 0xA9, 0x00, 0x00, 0xAE, 0xCF, 0x53, 0xE0, 0x00, 0x00, 0xF0, 0x0A, 0xCA, 0x1A, 0x1A,
                              0x1A, 0x1A, 0x1A, 0x1A, 0x1A, 0x80, 0xF1, 0xAE, 0xD3, 0x53, 0xE0, 0x07, 0x00, 0xF0, 0x1B,
                              0xCA, 0xE0, 0x00, 0x00, 0xF0, 0x04, 0x1A, 0xCA, 0x80, 0xF7, 0x0A, 0xAA, 0xBD, 0x20, 0x90,
                              0x3A, 0x0A, 0xAA, 0xA9, 0x01, 0x00, 0x1D, 0x00, 0x82, 0x9D, 0x00, 0x82, 0xFA, 0xAD, 0xCD,
                              0x53, 0xCD, 0xC1, 0x5A, 0x6B, ])

    # base patch done, write relevant slot info

    # Write strict bosses patch
    if multiworld.strict_bosses[player]:
        rom.write_bytes(0x3A000, [0xDA, 0xAD, 0xCB, 0x53, 0xC9, 0x05, 0x00, 0xB0, 0x15, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA,
                                  0xAE, 0xCB, 0x53, 0xCA, 0x8A, 0x0A, 0xAA, 0xAD, 0x70, 0x80, 0xDF, 0x00, 0xD0, 0x07,
                                  0xB0, 0x03, 0x38, 0x80, 0x01, 0x18, 0xFA, 0xAD, 0xCD, 0x53, 0x6B, ])
        rom.write_bytes(0x143D9, [0x22, 0x00, 0xA0, 0x07, 0xEA, 0xEA, ])

    # Write open world patch
    if multiworld.open_world[player]:
        rom.write_bytes(0x14238,   [0xA9, 0x06, 0x00,  # LDA #$0006
                                    0x22, 0x80, 0x9A, 0x07,  # JSL $079A80
                                    0xEA, 0xEA, 0xEA, 0xEA, 0xEA, ])   # set starting stages to 6
        rom.write_bytes(0x39A80,   [0x8D, 0xC1, 0x5A,  # STA $5AC1 (cutscene)
                                    0x8D, 0xCD, 0x53,  # STA $53CD (unlocked stages)
                                    0x1A,              # INC
                                    0x8D, 0xB9, 0x5A,  # STA $5AB9 (currently selectable stages)
                                    0xA9, 0x01, 0x00,  # LDA #$0001
                                    0x8D, 0x9D, 0x5A,  # STA $5A9D
                                    0x8D, 0x9F, 0x5A,  # STA $5A9F
                                    0x8D, 0xA1, 0x5A,  # STA $5AA1
                                    0x8D, 0xA3, 0x5A,  # STA $5AA3
                                    0x8D, 0xA5, 0x5A,  # STA $5AA5
                                    0x6B,              # RTL
                                    ])
        rom.write_bytes(0x3A0BD, [0xCD, 0xCD, 0x53])    # changes the stage flag function to compare $53CD to $53CD,
                                                        # always running the "new stage" function
                                                        # This has further checks present for bosses already, so we just
                                                        # need to handle regular stages
        # write check for boss to be unlocked
        rom.write_bytes(0x3A100, [0xDA, 0x5A, 0xAD, 0xCD, 0x53, 0xC9, 0x06, 0x00, 0xD0, 0x4E, 0xAD, 0xCF, 0x53, 0x1A,
                                  0xCD, 0xCB, 0x53, 0xD0, 0x45, 0xA9, 0x00, 0x00, 0xAE, 0xCF, 0x53, 0xE0, 0x00, 0x00,
                                  0xF0, 0x06, 0x69, 0x06, 0x00, 0xCA, 0x80, 0xF5, 0xAA, 0xA9, 0x00, 0x00, 0xA0, 0x06,
                                  0x00, 0x5A, 0xDA, 0xFA, 0xBC, 0x20, 0x90, 0x88, 0xE8, 0xE8, 0x48, 0x98, 0x0A, 0xA8,
                                  0x68, 0x79, 0x00, 0x82, 0x7A, 0x88, 0x5A, 0xDA, 0xC0, 0x00, 0x00, 0xD0, 0xE8, 0xFA,
                                  0x7A, 0xCD, 0x16, 0x90, 0x90, 0x0C, 0xAD, 0xCD, 0x53, 0x1A, 0x8D, 0xCD, 0x53, 0x8D,
                                  0xC1, 0x5A, 0x80, 0x03, 0x9C, 0xC1, 0x5A, 0x7A, 0xFA, 0x6B, ])
        # write hook to boss check
        rom.write_bytes(0x143F0, [0x22, 0x00, 0xA1, 0x07, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, ])

    # Write checks for consumable-sanity
    if multiworld.consumables[player]:
        # Redirect Consumable Effect and write index
        rom.write_bytes(0x3001E, [0x22, 0x80, 0x9E, 0x07, 0x4A, 0xC9, 0x05, 0x00, 0xB0, 0xFE, 0x0A, 0xAA, 0x7C, 0x2D,
                                  0x00, 0x37, 0x00, 0x37, 0x00, 0x7E, 0x00, 0x94, 0x00, 0x37, 0x00, 0xA9, 0x26, 0x00,
                                  0x22, 0x27, 0xD9, 0x00, 0xA4, 0xD2, 0x6B, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA, 0xEA,
                                  0xEA, 0xEA, 0xEA, ])

        # Write Consumable Index to index array
        rom.write_bytes(0x39E80, [0x48, 0xDA, 0x5A, 0x29, 0xFF, 0x00, 0x48, 0xAE, 0xCF, 0x53, 0xAC, 0xD3, 0x53, 0xA9,
                                  0x00, 0x00, 0x88, 0xE0, 0x00, 0x00, 0xF0, 0x07, 0x18, 0x69, 0x07, 0x00, 0xCA, 0x80,
                                  0xF4, 0xC0, 0x00, 0x00, 0xF0, 0x04, 0x1A, 0x88, 0x80, 0xF7, 0x0A, 0xAA, 0xBF, 0x20,
                                  0xD0, 0x07, 0x3A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0xAA, 0x68, 0xC9, 0x00, 0x00,
                                  0xF0, 0x04, 0xE8, 0x3A, 0x80, 0xF7, 0xBD, 0x00, 0xA0, 0x09, 0x01, 0x00, 0x9D, 0x00,
                                  0xA0, 0x7A, 0xFA, 0x68, 0xEB, 0x29, 0xFF, 0x00, 0x6B, ])

    # boss requirements
    rom.write_bytes(0x3D000, struct.pack("HHHHH", boss_requirements[0], boss_requirements[1], boss_requirements[2],
                                         boss_requirements[3], boss_requirements[4]))
    rom.write_byte(0x3D010, multiworld.death_link[player].value)
    rom.write_byte(0x3D012, multiworld.goal[player].value)
    rom.write_byte(0x3D014, multiworld.stage_shuffle[player].value)
    rom.write_byte(0x3D016, multiworld.ow_boss_requirement[player].value)
    rom.write_bytes(0x3D00A, struct.pack("H", heart_stars_required if multiworld.goal_speed[player] == 1
                                         else 0xFFFF))

    for level in shuffled_levels:
        for i in range(len(shuffled_levels[level])):
            rom.write_bytes(0x3F002E + ((level - 1) * 14) + (i * 2),
                            struct.pack("H", level_pointers[shuffled_levels[level][i]]))
            rom.write_bytes(0x3D020 + (level - 1) * 14 + (i * 2),
                            struct.pack("H", shuffled_levels[level][i] & 0x00FFFF))
            if (i == 0) or (i > 0 and i % 6 != 0):
                rom.write_bytes(0x3D080 + (level - 1) * 12 + (i * 2),
                                struct.pack("H", (shuffled_levels[level][i] & 0x00FFFF) % 6))

    # write jumping goal
    rom.write_bytes(0x94F8, struct.pack("H", multiworld.jumping_target[player]))
    rom.write_bytes(0x944E, struct.pack("H", multiworld.jumping_target[player]))

    from Main import __version__
    rom.name = bytearray(f'KDL3{__version__.replace(".", "")[0:3]}_{player}_{multiworld.seed:11}\0', 'utf8')[:21]
    rom.name.extend([0] * (21 - len(rom.name)))
    rom.write_bytes(0x7FC0, rom.name)
    rom.write_byte(0x7FD9, multiworld.game_language[player].value)

    # handle palette
    if multiworld.kirby_flavor_preset[player] != 0:
        for addr in kirby_target_palettes:
            target = kirby_target_palettes[addr]
            palette = get_kirby_palette(multiworld, player)
            rom.write_bytes(addr, get_palette_bytes(palette, target[0], target[1], target[2]))

    if multiworld.gooey_flavor_preset[player] != 0:
        for addr in gooey_target_palettes:
            target = gooey_target_palettes[addr]
            palette = get_gooey_palette(multiworld,player)
            rom.write_bytes(addr, get_palette_bytes(palette, target[0], target[1], target[2]))


def get_base_rom_bytes(file_name: str = "") -> bytes:
    base_rom_bytes: Optional[bytes] = getattr(get_base_rom_bytes, "base_rom_bytes", None)
    if not base_rom_bytes:
        file_name: str = get_base_rom_path(file_name)
        base_rom_bytes = bytes(Utils.read_snes_rom(open(file_name, "rb")))

        basemd5 = hashlib.md5()
        basemd5.update(base_rom_bytes)
        if basemd5.hexdigest() not in {KDL3UHASH, KDL3JHASH}:
            raise Exception("Supplied Base Rom does not match known MD5 for US or JP release. "
                            "Get the correct game and version, then dump it")
        get_base_rom_bytes.base_rom_bytes = base_rom_bytes
    return base_rom_bytes


def get_base_rom_path(file_name: str = "") -> str:
    options: Utils.OptionsType = Utils.get_options()
    if not file_name:
        file_name = options["kdl3_options"]["rom_file"]
    if not os.path.exists(file_name):
        file_name = Utils.user_path(file_name)
    return file_name
