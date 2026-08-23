from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from BaseClasses import ItemClassification

from .locations import BUGS, FISH, FOSSILS, PAINTINGS


ItemData = dict[str, Any]
NamedGameItem = tuple[str, int]


# ---------------------------------------------------------------------------
# Archipelago item-ID ranges
# ---------------------------------------------------------------------------

STARTING_TOOL_AP_BASE = 3000
GOLDEN_TOOL_AP_BASE = 3100

BUG_ITEM_AP_BASE = 4000
FISH_ITEM_AP_BASE = 4100
FOSSIL_ITEM_AP_BASE = 4200
PAINTING_ITEM_AP_BASE = 4300
MONTH_ITEM_AP_BASE = 4400

BELL_AP_BASE = 5000
FRUIT_AP_BASE = 5100
ENVIRONMENT_AP_BASE = 5200
CONTROLLER_UNLOCK_AP_BASE = 5300
CLOTHING_AP_BASE = 6000
TRAP_AP_BASE = 7000


item_table: dict[str, ItemData] = {}


def add_named_items(
    entries: Sequence[NamedGameItem],
    *,
    ap_id_base: int,
    classification: ItemClassification,
    category: str,
) -> None:
    """Add explicitly named inventory items with consecutive AP IDs."""
    for index, (name, game_id) in enumerate(entries):
        if name in item_table:
            raise ValueError(f"Duplicate ACWW item name: {name}")

        item_table[name] = {
            "id": ap_id_base + index,
            "game_id": game_id,
            "classification": classification,
            "category": category,
        }


def add_generated_items(
    names: Iterable[str],
    *,
    name_prefix: str,
    ap_id_base: int,
    game_id_base: int,
    game_id_step: int,
    classification: ItemClassification,
    category: str,
) -> None:
    """Generate inventory items whose Wild World IDs follow a sequence."""
    entries = [
        (
            f"{name_prefix}{name}",
            game_id_base + (index * game_id_step),
        )
        for index, name in enumerate(names)
    ]

    add_named_items(
        entries,
        ap_id_base=ap_id_base,
        classification=classification,
        category=category,
    )


def add_virtual_items(
    names: Sequence[str],
    *,
    ap_id_base: int,
    classification: ItemClassification,
    category: str,
) -> None:
    """Add client-handled AP items that do not enter the inventory."""
    for index, name in enumerate(names):
        if name in item_table:
            raise ValueError(f"Duplicate ACWW item name: {name}")

        item_table[name] = {
            "id": ap_id_base + index,
            "classification": classification,
            "category": category,
        }


# ---------------------------------------------------------------------------
# Optional starting tools
# ---------------------------------------------------------------------------

# These physical items are precollected only when Start with Tools is enabled.
# They never enter the randomized item pool and are not used by AP logic.
STARTING_TOOLS: list[NamedGameItem] = [
    ("Shovel", 0x1369),
    ("Fishing Rod", 0x1374),
    ("Net", 0x1376),
]

add_named_items(
    STARTING_TOOLS,
    ap_id_base=STARTING_TOOL_AP_BASE,
    classification=ItemClassification.useful,
    category="starting_tool",
)


# ---------------------------------------------------------------------------
# Golden tools
# ---------------------------------------------------------------------------

# Golden tools are useful randomized rewards. Unlike the old progressive-tool
# model, every golden tool is represented by its own independent AP item.
GOLDEN_TOOLS: list[NamedGameItem] = [
    ("Golden Shovel", 0x136A),
    ("Golden Axe", 0x1373),
    ("Golden Fishing Rod", 0x1375),
    ("Golden Net", 0x1377),
    ("Golden Watering Can", 0x1379),
    ("Golden Slingshot", 0x137B),
]

add_named_items(
    GOLDEN_TOOLS,
    ap_id_base=GOLDEN_TOOL_AP_BASE,
    classification=ItemClassification.useful,
    category="golden_tool",
)


# ---------------------------------------------------------------------------
# Month unlocks
# ---------------------------------------------------------------------------

# These are virtual AP items. The client will eventually use them to change
# the in-game month after the date/month memory fields are identified.
MONTHS: list[str] = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

add_virtual_items(
    MONTHS,
    ap_id_base=MONTH_ITEM_AP_BASE,
    classification=ItemClassification.progression,
    category="month",
)


# ---------------------------------------------------------------------------
# Master Controller unlocks
# ---------------------------------------------------------------------------

# Virtual utility unlocks handled by the client/Lua Master Controller.
# Keeping these in their own category makes future controller abilities easy
# to add without special-casing their AP delivery behavior.
CONTROLLER_UNLOCKS: list[str] = [
    "Weather Control",
]

add_virtual_items(
    CONTROLLER_UNLOCKS,
    ap_id_base=CONTROLLER_UNLOCK_AP_BASE,
    classification=ItemClassification.useful,
    category="controller_unlock",
)


# ---------------------------------------------------------------------------
# Museum specimens
# ---------------------------------------------------------------------------

# These are progression items because each one can unlock its matching
# museum-donation location. Receiving a specimen does not satisfy Catchsanity.
add_generated_items(
    BUGS,
    name_prefix="Bug: ",
    ap_id_base=BUG_ITEM_AP_BASE,
    game_id_base=0x12B0,
    game_id_step=1,
    classification=ItemClassification.progression,
    category="bug",
)

add_generated_items(
    FISH,
    name_prefix="Fish: ",
    ap_id_base=FISH_ITEM_AP_BASE,
    game_id_base=0x12E8,
    game_id_step=1,
    classification=ItemClassification.progression,
    category="fish",
)

add_generated_items(
    FOSSILS,
    name_prefix="Fossil: ",
    ap_id_base=FOSSIL_ITEM_AP_BASE,
    game_id_base=0x450C,
    game_id_step=4,
    classification=ItemClassification.progression,
    category="fossil",
)

add_generated_items(
    PAINTINGS,
    name_prefix="Painting: ",
    ap_id_base=PAINTING_ITEM_AP_BASE,
    game_id_base=0x3894,
    game_id_step=4,
    classification=ItemClassification.progression,
    category="painting",
)


# ---------------------------------------------------------------------------
# Repeatable Bell filler
# ---------------------------------------------------------------------------

BELL_ITEMS: list[NamedGameItem] = [
    ("1,000 Bells", 0x149B),
    ("5,000 Bells", 0x149F),
    ("10,000 Bells", 0x14A4),
    ("30,000 Bells", 0x14B8),
]

add_named_items(
    BELL_ITEMS,
    ap_id_base=BELL_AP_BASE,
    classification=ItemClassification.filler,
    category="bells",
)


# ---------------------------------------------------------------------------
# Fruit filler
# ---------------------------------------------------------------------------

FRUIT_ITEMS: list[NamedGameItem] = [
    ("Apple", 0x1518),
    ("Orange", 0x1519),
    ("Pear", 0x151A),
    ("Peach", 0x151B),
    ("Cherry", 0x151C),
]

add_named_items(
    FRUIT_ITEMS,
    ap_id_base=FRUIT_AP_BASE,
    classification=ItemClassification.filler,
    category="fruit",
)


# ---------------------------------------------------------------------------
# Guaranteed bug-environment items
# ---------------------------------------------------------------------------

# These are progression because specific Catchsanity checks rely on them.
# Multiple copies are added by the world generator where appropriate.
ENVIRONMENT_ITEMS: list[NamedGameItem] = [
    ("Red Roses", 0x1483),
    ("White Roses", 0x1484),
    ("Pink Roses", 0x1486),
    ("Purple Roses", 0x1488),
    ("Black Roses", 0x1489),
    ("Blue Roses", 0x148A),
    ("Coconut", 0x1548),
    ("Spoiled Turnips", 0x154A),
    # Appended so existing environment-item AP IDs remain stable.
    ("Sapling", 0x151D),
    ("Cedar Sapling", 0x151E),
]

add_named_items(
    ENVIRONMENT_ITEMS,
    ap_id_base=ENVIRONMENT_AP_BASE,
    classification=ItemClassification.progression,
    category="environment",
)


# ---------------------------------------------------------------------------
# Cosmetic clothing filler
# ---------------------------------------------------------------------------

CLOTHING_ITEMS: list[NamedGameItem] = [
    ("Work Uniform", 0x11A8),
    ("One-Ball Shirt", 0x11A9),
    ("Two-Ball Shirt", 0x11AA),
    ("Three-Ball Shirt", 0x11AB),
    ("Four-Ball Shirt", 0x11AC),
    ("Five-Ball Shirt", 0x11AD),
    ("Six-Ball Shirt", 0x11AE),
    ("Seven-Ball Shirt", 0x11AF),
    ("Eight-Ball Shirt", 0x11B0),
    ("Nine-Ball Shirt", 0x11B1),
    ("Paw Shirt", 0x11B2),
    ("Daisy Shirt", 0x11B3),
    ("Tulip Shirt", 0x11B4),
    ("Cherry Shirt", 0x11B5),
    ("Skull Shirt", 0x11B6),
    ("U R Here Shirt", 0x11B7),
    ("Lightning Shirt", 0x11B8),
    ("MVP Shirt", 0x11B9),
    ("BB Shirt", 0x11BA),
    ("Frog Shirt", 0x11BB),
    ("Bear Shirt", 0x11BC),
    ("Bunny Shirt", 0x11BD),
    ("Elephant Shirt", 0x11BE),
    ("Spade Shirt", 0x11BF),
    ("Diamond Shirt", 0x11C0),
    ("Club Shirt", 0x11C1),
    ("Heart Shirt", 0x11C2),
    ("Big Star Shirt", 0x11C3),
    ("Bright Shirt", 0x11C4),
    ("A Shirt", 0x11C5),
    ("No. 1 Shirt", 0x11C6),
    ("No. 2 Shirt", 0x11C7),
    ("No. 3 Shirt", 0x11C8),
    ("No. 4 Shirt", 0x11C9),
    ("No. 5 Shirt", 0x11CA),
    ("No. 23 Shirt", 0x11CB),
    ("No. 67 Shirt", 0x11CC),
    ("Big Bro's Shirt", 0x11CD),
    ("Li'l Bro's Shirt", 0x11CE),
    ("Cloudy Shirt", 0x11CF),
    ("Fresh Shirt", 0x11D0),
    ("Dawn Shirt", 0x11D1),
    ("Misty Shirt", 0x11D2),
    ("Sunset Top", 0x11D3),
    ("Deep Blue Tee", 0x11D4),
    ("Peachy Shirt", 0x11D5),
    ("Rainbow Shirt", 0x11D6),
    ("Snowcone Shirt", 0x11D7),
    ("Orange Tie-Dye", 0x11D8),
    ("Purple Tie-Dye", 0x11D9),
    ("Green Tie-Dye", 0x11DA),
    ("Blue Tie-Dye", 0x11DB),
    ("Red Tie-Dye", 0x11DC),
    ("Bold Check Shirt", 0x11DD),
    ("Cafe Shirt", 0x11DE),
    ("Checkered Shirt", 0x11DF),
    ("Blue Check Shirt", 0x11E0),
    ("Red Check Shirt", 0x11E1),
    ("Rugby Shirt", 0x11E2),
    ("Green Bar Shirt", 0x11E3),
    ("Yellow Bar Shirt", 0x11E4),
    ("Grape Stripe Tee", 0x11E5),
    ("Beatnik Shirt", 0x11E6),
    ("Red Bar Shirt", 0x11E7),
    ("Blue Stripe Knit", 0x11E8),
    ("Gelato Shirt", 0x11E9),
    ("Chain-Gang Shirt", 0x11EA),
    ("Yellow Tartan", 0x11EB),
    ("Fall Plaid Shirt", 0x11EC),
    ("Blue Tartan", 0x11ED),
    ("Dapper Shirt", 0x11EE),
    ("Natty Shirt", 0x11EF),
    ("Blue Grid Shirt", 0x11F0),
    ("Red Grid Shirt", 0x11F1),
    ("Dazed Shirt", 0x11F2),
    ("Checkerboard Tee", 0x11F3),
    ("Toad Shirt", 0x11F4),
    ("Dark Polka Shirt", 0x11F5),
    ("Lite Polka Shirt", 0x11F6),
    ("Bubble Gum Shirt", 0x11F7),
    ("Funky Dot Shirt", 0x11F8),
    ("Gumdrop Shirt", 0x11F9),
    ("Big Dot Shirt", 0x11FA),
    ("Aqua Polka Shirt", 0x11FB),
    ("Blue Pinstripe", 0x11FC),
    ("Yellow Pinstripe", 0x11FD),
    ("Orange Pinstripe", 0x11FE),
    ("Vegetarian Shirt", 0x11FF),
    ("Racer Shirt", 0x1200),
    ("Vertigo Shirt", 0x1201),
    ("Barber Shirt", 0x1202),
    ("Jade Check Print", 0x1203),
    ("Blue Check Print", 0x1204),
    ("Mint Gingham Top", 0x1205),
    ("Picnic Shirt", 0x1206),
    ("Candy Gingham", 0x1207),
    ("Lemon Gingham", 0x1208),
    ("Melon Gingham", 0x1209),
    ("Bad Plaid Shirt", 0x120A),
    ("Pink Tartan", 0x120B),
    ("Waffle Shirt", 0x120C),
    ("Gray Tartan", 0x120D),
    ("Chevron Shirt", 0x120E),
    ("Icy Shirt", 0x120F),
    ("Aurora Knit", 0x1210),
    ("Winter Sweater", 0x1211),
    ("Folk Shirt", 0x1212),
    ("Argyle Knit", 0x1213),
    ("Uncommon Shirt", 0x1214),
    ("Comfy Sweater", 0x1215),
    ("Beige Knit", 0x1216),
    ("Earthy Knit", 0x1217),
    ("Spring Shirt", 0x1218),
    ("Vogue Top", 0x1219),
    ("Citrus Gingham", 0x121A),
    ("Floral Knit", 0x121B),
    ("Dreamy Shirt", 0x121C),
    ("Flowery Shirt", 0x121D),
    ("Silk Bloom Shirt", 0x121E),
    ("Pop Bloom Shirt", 0x121F),
    ("Blossom Shirt", 0x1220),
    ("Loud Bloom Shirt", 0x1221),
    ("Rose Shirt", 0x1222),
    ("Rose Sky Shirt", 0x1223),
    ("Lotus Shirt", 0x1224),
    ("Chocomint Shirt", 0x1225),
    ("Fern Shirt", 0x1226),
    ("Blue Retro Shirt", 0x1227),
    ("Orange Check Tee", 0x1228),
    ("Leaf Shirt", 0x1229),
    ("Fall Leaf Shirt", 0x122A),
    ("Grass Shirt", 0x122B),
    ("Snow Shirt", 0x122C),
    ("Lovely Shirt", 0x122D),
    ("Bubble Shirt", 0x122E),
    ("Chichi Print", 0x122F),
    ("Coral Shirt", 0x1230),
    ("Groovy Shirt", 0x1231),
    ("Cool Shirt", 0x1232),
    ("Swell Shirt", 0x1233),
    ("Blue Diamond Top", 0x1234),
    ("Prism Shirt", 0x1235),
    ("Go-Go Shirt", 0x1236),
    ("Flame Shirt", 0x1237),
    ("Danger Shirt", 0x1238),
    ("Gracie's Top", 0x1239),
    ("Future Shirt", 0x123A),
    ("Optical Shirt", 0x123B),
    ("Twinkle Shirt", 0x123C),
    ("Star Shirt", 0x123D),
    ("Night Sky Tee", 0x123E),
    ("Amethyst Shirt", 0x123F),
    ("Nebula Shirt", 0x1240),
    ("Dice Shirt", 0x1241),
    ("Kiddie Shirt", 0x1242),
    ("Airy Shirt", 0x1243),
    ("Polar Fleece", 0x1244),
    ("Crossing Shirt", 0x1245),
    ("Splendid Shirt", 0x1246),
    ("Jagged Shirt", 0x1247),
    ("Subdued Print", 0x1248),
    ("Sharp Outfit", 0x1249),
    ("Jungle Camo", 0x124A),
    ("Arctic Camo", 0x124B),
    ("Desert Camo", 0x124C),
    ("Zebra Shirt", 0x124D),
    ("Tiger Shirt", 0x124E),
    ("Cow Shirt", 0x124F),
    ("Leopard Shirt", 0x1250),
    ("Giraffe Shirt", 0x1251),
    ("Ladybug Shirt", 0x1252),
    ("Butterfly Shirt", 0x1253),
    ("Spiderweb Shirt", 0x1254),
    ("Caterpillar Tee", 0x1255),
    ("Fiendish Shirt", 0x1256),
    ("Citrus Shirt", 0x1257),
    ("Kiwi Shirt", 0x1258),
    ("Watermelon Shirt", 0x1259),
    ("Strawberry Shirt", 0x125A),
    ("Grape Shirt", 0x125B),
    ("Melon Shirt", 0x125C),
    ("Pink Wave Shirt", 0x125D),
    ("Flan Shirt", 0x125E),
    ("Hot Dog Shirt", 0x125F),
    ("Sandwich Shirt", 0x1260),
    ("Dragon Suit", 0x1261),
    ("Asian Shirt", 0x1262),
    ("Hot Spring Shirt", 0x1263),
    ("New Spring Shirt", 0x1264),
    ("Crewel Shirt", 0x1265),
    ("Tropical Shirt", 0x1266),
    ("Ribbon Shirt", 0x1267),
    ("Bodice", 0x1268),
    ("Laced Shirt", 0x1269),
    ("Circus Shirt", 0x126A),
    ("Green Vest", 0x126B),
    ("Yellow Bolero", 0x126C),
    ("Noble Shirt", 0x126D),
    ("Turnip Top", 0x126E),
    ("Yodel Shirt", 0x126F),
    ("Gaudy Sweater", 0x1270),
    ("Western Shirt", 0x1271),
    ("Red Riding Hoody", 0x1272),
    ("Royal Shirt", 0x1273),
    ("Witch Shirt", 0x1274),
    ("Firefighter Tee", 0x1275),
    ("Graduation Gown", 0x1276),
    ("Sky Shirt", 0x1277),
    ("Captain's Shirt", 0x1278),
    ("Burglar's Shirt", 0x1279),
    ("Jester Shirt", 0x127A),
    ("Nurse's Uniform", 0x127B),
    ("Bone Shirt", 0x127C),
    ("Zipper Shirt", 0x127D),
    ("Mummy Shirt", 0x127E),
    ("Military Uniform", 0x127F),
    ("Sailor's Uniform", 0x1280),
    ("Reggae Shirt", 0x1281),
    ("Camel Shirt", 0x1282),
    ("Molecule Tee", 0x1283),
    ("Concierge Shirt", 0x1284),
    ("Kimono", 0x1285),
    ("Tuxedo", 0x1286),
    ("Explorer Shirt", 0x1287),
    ("Dutch Shirt", 0x1288),
    ("Toga", 0x1289),
    ("Cake Shirt", 0x128A),
    ("Waitress Shirt", 0x128B),
    ("Princess Shirt", 0x128C),
    ("Fairy Tale Shirt", 0x128D),
    ("Spanish Shirt", 0x128E),
    ("Latin Uniform", 0x128F),
    ("Red Down Vest", 0x1290),
    ("One-Way Tee", 0x1291),
    ("Beaded Shirt", 0x1292),
    ("Nile Shirt", 0x1293),
    ("Wrap Shirt", 0x1294),
    ("Wrestler Shirt", 0x1295),
    ("Security Shirt", 0x1296),
    ("Poncho", 0x1297),
    ("Fluffy Shirt", 0x1298),
    ("Chinese Shirt", 0x1299),
    ("Pep Squad Shirt", 0x129A),
    ("Racing Shirt", 0x129B),
    ("Orange Jumpsuit", 0x129C),
    ("Tin Shirt", 0x129D),
    ("Scale Armor Suit", 0x129E),
    ("Armor Suit", 0x129F),
    ("Gold Armor Suit", 0x12A0),
    ("Red Warmup Suit", 0x12A1),
    ("Baseball Shirt", 0x12A2),
    ("Leather Jerkin", 0x12A3),
    ("Frock Coat", 0x12A4),
    ("Space Suit", 0x12A5),
    ("Caveman Tunic", 0x12A6),
    ("Moldy Shirt", 0x12A7),
]

add_named_items(
    CLOTHING_ITEMS,
    ap_id_base=CLOTHING_AP_BASE,
    classification=ItemClassification.filler,
    category="clothing",
)


# ---------------------------------------------------------------------------
# Trap items
# ---------------------------------------------------------------------------

# Trap items are virtual client-handled items.  The generator may add repeated
# copies according to the Trap Count option.  Keep this list as the canonical
# pool so future trap types can be added without changing generation logic.
TRAPS: list[str] = [
    "Bee Trap",
    "Invisible Bee Trap",
]

add_virtual_items(
    TRAPS,
    ap_id_base=TRAP_AP_BASE,
    classification=ItemClassification.trap,
    category="trap",
)


# ---------------------------------------------------------------------------
# Lookup tables
# ---------------------------------------------------------------------------

item_name_to_id = {
    name: data["id"]
    for name, data in item_table.items()
}

item_id_to_name = {
    data["id"]: name
    for name, data in item_table.items()
}

received_item_data_by_ap_id = {
    data["id"]: {
        "name": name,
        "game_id": data.get("game_id"),
        "category": data["category"],
    }
    for name, data in item_table.items()
}


starting_tool_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "starting_tool"
]

golden_tool_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "golden_tool"
]

month_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "month"
]

controller_unlock_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "controller_unlock"
]

bell_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "bells"
]

fruit_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "fruit"
]

environment_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "environment"
]

clothing_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "clothing"
]


trap_item_names = [
    name
    for name, data in item_table.items()
    if data["category"] == "trap"
]
