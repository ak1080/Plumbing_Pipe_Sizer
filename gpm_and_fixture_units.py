from math import floor

# Function below will interpolate fixture units in the table based on the type of system (valves or tank) selected by the user.
def interpolate_fixture_units(gpm_input, flush_type):
    if gpm_input < fixture_data[0][0] or gpm_input > fixture_data[-1][0]:
        return "Out of Range."

    for i in range(len(fixture_data) - 1):
        gpm1, tank1, valve1 = fixture_data[i]
        gpm2, tank2, valve2 = fixture_data[i + 1]

        if gpm1 <= gpm_input <= gpm2:
            if flush_type.lower() == "tank":
                return floor(tank1 + (tank2 - tank1) * (gpm_input - gpm1) / (gpm2 - gpm1))
            elif flush_type.lower() == "valve":
                if valve1 is None or valve2 is None:
                    return valve1 if valve1 is not None else "Out of range. Use next valid pipe size."
                return floor(valve1 + (valve2 - valve1) * (gpm_input - gpm1) / (gpm2 - gpm1))
            else:
                return "Error: Invalid flush type."

    return "Error: Unable to calculate fixture units."

# Fixture data as tuples (GPM, Tank Fixture Units, Valve Fixture Units). From 2021 UPC training manual Figure A 108.1B
fixture_data = [
    (1, 0, None), (2, 1, None), (3, 3, None), (4, 4, None), (5, 6, None), (6, 7, None), (7, 8, None), (8, 10, None),
    (9, 12, None), (10, 13, None), (11, 15, None), (12, 16, None), (13, 18, None), (14, 20, None), (15, 21, None),
    (16, 23, None), (17, 24, None), (18, 26, None), (19, 28, None), (20, 30, None), (21, 32, None), (22, 34, 5),
    (23, 36, 6), (24, 39, 7), (25, 42, 8), (26, 44, 9), (27, 46, 10), (28, 49, 11), (29, 51, 12), (30, 54, 13),
    (31, 56, 14), (32, 58, 15), (33, 60, 16), (34, 63, 18), (35, 66, 20), (36, 69, 21), (37, 74, 23), (38, 78, 25),
    (39, 83, 26), (40, 86, 28), (41, 90, 30), (42, 95, 31), (43, 99, 33), (44, 103, 35), (45, 107, 37), (46, 111, 39),
    (47, 115, 42), (48, 119, 44), (49, 123, 46), (50, 127, 48), (51, 130, 50), (52, 135, 52), (53, 141, 54),
    (54, 146, 57), (55, 151, 60), (56, 155, 63), (57, 160, 66), (58, 165, 69), (59, 170, 73), (60, 175, 76),
    (62, 185, 82), (64, 195, 88), (66, 205, 95), (68, 215, 102), (70, 225, 108), (72, 236, 116), (74, 245, 124),
    (76, 254, 132), (78, 264, 140), (80, 275, 148), (82, 284, 158), (84, 294, 168), (86, 305, 176), (88, 315, 186),
    (90, 326, 195), (92, 337, 205), (94, 348, 214), (96, 359, 223), (98, 370, 234), (100, 380, 245), (105, 405, 270),
    (110, 431, 295), (115, 455, 329), (120, 479, 365), (125, 506, 396), (130, 533, 430), (135, 559, 460),
    (140, 585, 490), (145, 611, 521), (150, 638, 559), (155, 665, 596), (160, 692, 631), (165, 719, 666),
    (170, 748, 700), (175, 778, 739), (180, 809, 775), (185, 840, 811), (190, 874, 850), (200, 945, 931),
    (210, 1018, 1009), (220, 1091, 1091), (230, 1173, 1173), (240, 1254, 1254), (250, 1335, 1335), (260, 1418, 1418),
    (270, 1500, 1500), (280, 2583, 2583), (290, 1668, 1668), (300, 1755, 1755), (310, 1845, 1845), (320, 1926, 1926),
    (330, 2018, 2018), (340, 2110, 2110), (350, 2204, 2204), (360, 2298, 2298), (370, 2388, 2388), (380, 2480, 2480),
    (390, 2575, 2575), (400, 2670, 2670), (410, 2765, 2765), (420, 2862, 2862), (430, 2960, 2960), (440, 3060, 3060),
    (450, 3150, 3150), (500, 3620, 3620)
]



