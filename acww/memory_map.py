from __future__ import annotations


# BizHawk memory domain used by the ACWW client.
MEMORY_DOMAIN = "Main RAM"


# ---------------------------------------------------------------------------
# Player inventory
# ---------------------------------------------------------------------------

INVENTORY_BASE_ADDRESS = 0x1D8E7E
INVENTORY_SLOT_COUNT = 15
INVENTORY_SLOT_SIZE = 2
EMPTY_INVENTORY_ITEM_ID = 0xFFF1


# ---------------------------------------------------------------------------
# Catch journal
# ---------------------------------------------------------------------------

# One unrelated bit appears before the first bug flag.
# Bugs occupy the next 56 bits, followed by 56 fish bits.
JOURNAL_BASE_ADDRESS = 0x1D8F39
JOURNAL_READ_SIZE = 15
JOURNAL_START_BIT = 1

BUG_COUNT = 56
FISH_COUNT = 56


# ---------------------------------------------------------------------------
# Museum donations
# ---------------------------------------------------------------------------

# Donation records use one 4-bit nibble per entry.
# A nibble of zero means the entry has not been donated.
MUSEUM_BASE_ADDRESS = 0x1ED0A0
MUSEUM_READ_SIZE = 0x60

FOSSIL_MUSEUM_ADDRESS = 0x1ED0A0
FISH_MUSEUM_ADDRESS = 0x1ED0B8
BUG_MUSEUM_ADDRESS = 0x1ED0D8
PAINTING_MUSEUM_ADDRESS = 0x1ED0F4

FOSSIL_COUNT = 52
PAINTING_COUNT = 20

# Bitterling begins at nibble index 6 in its first four-byte group.
FISH_MUSEUM_START_INDEX = 6

# Two unused nibbles appear before the first painting.
PAINTING_MUSEUM_START_INDEX = 2


# ---------------------------------------------------------------------------
# House progression
# ---------------------------------------------------------------------------

# Confirmed as a 2-byte unsigned little-endian value.
HOUSE_DEBT_ADDRESS = 0x1E6E38

INITIAL_HOUSE_DEBT = 19800
POST_TUTORIAL_HOUSE_DEBT = 18400