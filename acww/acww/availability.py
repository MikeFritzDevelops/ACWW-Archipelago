from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, FrozenSet

if TYPE_CHECKING:
    from BaseClasses import CollectionState


ALL_MONTHS: FrozenSet[int] = frozenset(range(1, 13))

MONTH_NAMES: tuple[str, ...] = (
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
)


FLOWER_RESOURCE_ITEMS: FrozenSet[str] = frozenset({
    "Red Roses",
    "White Roses",
    "Pink Roses",
    "Purple Roses",
    "Black Roses",
    "Blue Roses",
})

# Barren Town's guaranteed AP tree resources. Fruit is intentionally not used
# as the logical tree unlock: Sapling/Cedar Sapling are the deterministic
# habitat progression resources for ordinary tree-dependent bugs.
TREE_RESOURCE_ITEMS: FrozenSet[str] = frozenset({
    "Sapling",
    "Cedar Sapling",
})


@dataclass(frozen=True)
class Availability:
    """Logical requirements for naturally obtaining one creature."""

    months: FrozenSet[int]
    required_items: FrozenSet[str] = frozenset()
    any_item_groups: tuple[FrozenSet[str], ...] = ()
    requires_flowers: bool = False
    requires_trees: bool = False
    notes: tuple[str, ...] = ()
    high_rng: bool = False


def months(*values: int) -> FrozenSet[int]:
    return frozenset(values)


def month_range(start: int, end: int) -> FrozenSet[int]:
    """Inclusive month range, supporting ranges that cross New Year."""
    if start <= end:
        return frozenset(range(start, end + 1))

    return frozenset(
        list(range(start, 13))
        + list(range(1, end + 1))
    )


BUG_AVAILABILITY: dict[str, Availability] = {
    "Common Butterfly": Availability(
        month_range(3, 9),
        requires_flowers=True,
    ),
    "Yellow Butterfly": Availability(
        month_range(3, 9),
        requires_flowers=True,
    ),
    "Tiger Butterfly": Availability(
        month_range(3, 9),
        any_item_groups=(
            frozenset({"Red Roses", "Pink Roses"}),
        ),
        requires_flowers=True,
        notes=("Near red or pink flowers.",),
    ),
    "Peacock Butterfly": Availability(
        month_range(3, 9),
        any_item_groups=(
            frozenset({
                "Blue Roses",
                "Purple Roses",
                "Black Roses",
            }),
        ),
        requires_flowers=True,
        notes=("Near blue, purple, or black flowers.",),
    ),
    "Monarch Butterfly": Availability(
        month_range(9, 11),
        requires_flowers=True,
    ),
    "Emperor Butterfly": Availability(
        month_range(6, 9),
        requires_flowers=True,
    ),
    "Agrias Butterfly": Availability(
        month_range(6, 9),
        requires_flowers=True,
    ),
    "Birdwing Butterfly": Availability(
        month_range(3, 9),
        requires_flowers=True,
        notes=("Very rare.",),
        high_rng=True,
    ),
    "Moth": Availability(month_range(3, 9)),
    "Oak Silk Moth": Availability(
        month_range(6, 8),
        requires_trees=True,
        high_rng=True,
    ),
    "Honeybee": Availability(
        month_range(3, 9),
        requires_flowers=True,
    ),
    "Bee": Availability(
        ALL_MONTHS,
        requires_trees=True,
        notes=("Shake trees; difficult catch setup in Wild World.",),
        high_rng=True,
    ),
    "Long Locust": Availability(month_range(8, 11)),
    "Migratory Locust": Availability(month_range(8, 11)),
    "Mantis": Availability(
        month_range(8, 11),
        requires_flowers=True,
    ),
    "Orchid Mantis": Availability(
        month_range(8, 11),
        required_items=frozenset({"White Roses"}),
        requires_flowers=True,
        notes=("On white flowers.",),
    ),
    "Brown Cicada": Availability(
        month_range(7, 8),
        requires_trees=True,
    ),
    "Robust Cicada": Availability(
        month_range(7, 8),
        requires_trees=True,
    ),
    "Walker Cicada": Availability(
        month_range(7, 8),
        requires_trees=True,
    ),
    "Evening Cicada": Availability(
        month_range(7, 8),
        requires_trees=True,
    ),
    "Lantern Fly": Availability(
        month_range(6, 9),
        requires_trees=True,
    ),
    "Red Dragonfly": Availability(month_range(9, 11)),
    "Darner Dragonfly": Availability(month_range(6, 8)),
    "Banded Dragonfly": Availability(month_range(7, 8)),
    "Ant": Availability(
        ALL_MONTHS,
        required_items=frozenset({"Spoiled Turnips"}),
        notes=("On the ground beside spoiled turnips.",),
    ),
    "Pondskater": Availability(month_range(3, 9)),
    "Snail": Availability(
        month_range(4, 9),
        requires_flowers=True,
        required_items=frozenset({"Weather Control",}),
        notes=("Requires rain",),
        high_rng=True
    ),
    "Cricket": Availability(month_range(9, 11)),
    "Bell Cricket": Availability(month_range(9, 10)),
    "Grasshopper": Availability(month_range(7, 9)),
    "Mole Cricket": Availability(
        month_range(11, 3),
        notes=("Underground; dig it up before catching it.",),
        high_rng=True,
    ),
    "Walkingstick": Availability(
        month_range(7, 11),
        requires_trees=True,
    ),
    "Ladybug": Availability(
        frozenset({3, 4, 5, 6, 7, 10}),
        requires_flowers=True,
    ),
    "Fruit Beetle": Availability(
        month_range(7, 9),
        requires_trees=True,
    ),
    "Scarab Beetle": Availability(
        month_range(7, 8),
        requires_trees=True,
    ),
    "Dung Beetle": Availability(
        month_range(12, 2),
        notes=("Pushes snowballs.",),
        high_rng=True,
    ),
    "Goliath Beetle": Availability(
        month_range(6, 8),
        required_items=frozenset({"Coconut"}),
        notes=("Requires coconut trees.",),
    ),
    "Firefly": Availability(months(6)),
    "Jewel Beetle": Availability(
        month_range(7, 8),
        requires_trees=True,
    ),
    "Longhorn Beetle": Availability(
        month_range(6, 8),
        requires_trees=True,
    ),
    "Saw Stag Beetle": Availability(
        month_range(7, 8),
        requires_trees=True,
    ),
    "Stag Beetle": Availability(
        month_range(6, 8),
        requires_trees=True,
    ),
    "Giant Beetle": Availability(
        month_range(7, 8),
        requires_trees=True,
        notes=("Rare.",),
    ),
    "Rainbow Stag Beetle": Availability(
        month_range(6, 9),
        requires_trees=True,
    ),
    "Dynastid Beetle": Availability(
        month_range(6, 9),
        requires_trees=True,
    ),
    "Atlas Beetle": Availability(
        month_range(7, 8),
        required_items=frozenset({"Coconut"}),
        notes=("Requires coconut trees.",),
    ),
    "Elephant Beetle": Availability(
        month_range(7, 8),
        required_items=frozenset({"Coconut"}),
        notes=("Requires coconut trees; rare.",),
    ),
    "Hercules Beetle": Availability(
        month_range(7, 8),
        required_items=frozenset({"Coconut"}),
        notes=("Requires coconut trees.",),
    ),
    "Flea": Availability(
        month_range(3, 11),
        notes=("Appears on villagers.",),
        high_rng=True,
    ),
    "Pill Bug": Availability(
        ALL_MONTHS,
        notes=("Hit rocks with a shovel.",),
        high_rng=True,
    ),
    "Mosquito": Availability(month_range(6, 9)),
    "Fly": Availability(
        ALL_MONTHS,
        required_items=frozenset({"Spoiled Turnips"}),
        notes=(
            "Spoiled turnips provide the guaranteed logical route; "
            "trash or rafflesia can also work naturally.",
        ),
    ),
    "Cockroach": Availability(
        ALL_MONTHS,
        requires_trees=True,
    ),
    "Spider": Availability(
        month_range(3, 11),
        requires_trees=True,
        notes=("Shake trees.",),
        high_rng=True
    ),
    "Tarantula": Availability(
        month_range(6, 8),
        notes=("Rare.",),
        high_rng=True,
    ),
    "Scorpion": Availability(
        month_range(7, 9),
        notes=("Rare.",),
        high_rng=True,
    ),
}


FISH_AVAILABILITY: dict[str, Availability] = {
    "Bitterling": Availability(month_range(11, 2)),
    "Pale Chub": Availability(ALL_MONTHS),
    "Crucian Carp": Availability(ALL_MONTHS),
    "Dace": Availability(ALL_MONTHS),
    "Barbel Steed": Availability(ALL_MONTHS),
    "Carp": Availability(ALL_MONTHS),
    "Koi": Availability(ALL_MONTHS),
    "Goldfish": Availability(ALL_MONTHS),
    "Popeyed Goldfish": Availability(ALL_MONTHS),
    "Killifish": Availability(month_range(4, 8)),
    "Crawfish": Availability(month_range(4, 9)),
    "Frog": Availability(month_range(5, 8)),
    "Freshwater Goby": Availability(ALL_MONTHS),
    "Loach": Availability(month_range(3, 5)),
    "Catfish": Availability(month_range(3, 10)),
    "Eel": Availability(month_range(6, 9)),
    "Giant Snakehead": Availability(month_range(6, 8)),
    "Bluegill": Availability(ALL_MONTHS),
    "Yellow Perch": Availability(month_range(10, 3)),
    "Black Bass": Availability(ALL_MONTHS),
    "Pond Smelt": Availability(month_range(12, 2)),
    "Sweetfish": Availability(month_range(7, 8)),
    "Cherry Salmon": Availability(
        frozenset({3, 4, 5, 6, 9, 10, 11}),
    ),
    "Char": Availability(
        frozenset({3, 4, 5, 6, 9, 10, 11}),
    ),
    "Rainbow Trout": Availability(
        frozenset({3, 4, 5, 6, 9, 10, 11}),
    ),
    "Stringfish": Availability(month_range(12, 2)),
    "Salmon": Availability(months(9)),
    "King Salmon": Availability(months(9)),
    "Guppy": Availability(month_range(4, 11)),
    "Angelfish": Availability(month_range(3, 10)),
    "Piranha": Availability(month_range(6, 9)),
    "Arowana": Availability(month_range(6, 9)),
    "Dorado": Availability(month_range(6, 9)),
    "Gar": Availability(month_range(6, 9)),
    "Arapaima": Availability(month_range(7, 9)),
    "Sea Butterfly": Availability(month_range(12, 2)),
    "Jellyfish": Availability(
        months(8),
        notes=("Only available August 16-31.",),
    ),
    "Seahorse": Availability(month_range(4, 11)),
    "Clownfish": Availability(month_range(4, 9)),
    "Zebra Turkeyfish": Availability(month_range(4, 11)),
    "Pufferfish": Availability(month_range(7, 9)),
    "Horse Mackerel": Availability(ALL_MONTHS),
    "Barred Knifejaw": Availability(month_range(3, 11)),
    "Sea Bass": Availability(ALL_MONTHS),
    "Red Snapper": Availability(ALL_MONTHS),
    "Dab": Availability(month_range(10, 4)),
    "Olive Flounder": Availability(ALL_MONTHS),
    "Squid": Availability(month_range(12, 8)),
    "Octopus": Availability(
        frozenset({1, 3, 4, 5, 6, 7, 9, 10, 11, 12}),
    ),
    "Football Fish": Availability(month_range(11, 3)),
    "Tuna": Availability(
        month_range(11, 3),
        high_rng=True,
    ),
    "Blue Marlin": Availability(
        month_range(7, 9),
        high_rng=True,
    ),
    "Ocean Sunfish": Availability(
        month_range(7, 8),
        high_rng=True,
    ),
    "Hammerhead Shark": Availability(
        month_range(7, 8),
        high_rng=True,
    ),
    "Shark": Availability(
        month_range(6, 9),
        high_rng=True,
    ),
    "Coelacanth": Availability(
        ALL_MONTHS,
        required_items=frozenset({"Weather Control",}),
        notes=("Requires rain or snow",),
        high_rng=True,
    ),
}


def _validate_availability_table(
    expected_names: list[str],
    table: dict[str, Availability],
    category_name: str,
) -> None:
    expected = set(expected_names)
    actual = set(table)

    missing = expected - actual
    extra = actual - expected

    if not missing and not extra:
        return

    problems: list[str] = []

    if missing:
        problems.append("missing: " + ", ".join(sorted(missing)))

    if extra:
        problems.append("unknown: " + ", ".join(sorted(extra)))

    raise ValueError(
        f"ACWW {category_name} availability table mismatch ("
        + "; ".join(problems)
        + ")"
    )


def validate_bug_availability(bug_names: list[str]) -> None:
    _validate_availability_table(
        bug_names,
        BUG_AVAILABILITY,
        "bug",
    )


def validate_fish_availability(fish_names: list[str]) -> None:
    _validate_availability_table(
        fish_names,
        FISH_AVAILABILITY,
        "fish",
    )


def _has_valid_month(
    state: "CollectionState",
    player: int,
    availability: Availability,
) -> bool:
    if availability.months == ALL_MONTHS:
        return True

    valid_month_items = {
        month_name
        for month_number, month_name in enumerate(
            MONTH_NAMES,
            start=1,
        )
        if month_number in availability.months
    }

    return state.has_any(valid_month_items, player)


def _meets_availability_requirements(
    state: "CollectionState",
    player: int,
    availability: Availability,
) -> bool:
    if not _has_valid_month(state, player, availability):
        return False

    if not all(
        state.has(item_name, player)
        for item_name in availability.required_items
    ):
        return False

    if not all(
        state.has_any(set(item_group), player)
        for item_group in availability.any_item_groups
    ):
        return False

    return True


def can_catch_bug(
    state: "CollectionState",
    player: int,
    bug_name: str,
    *,
    barren_town: bool = False,
) -> bool:
    """Return whether AP logic considers the bug naturally catchable."""
    creature_availability = BUG_AVAILABILITY[bug_name]

    if not _meets_availability_requirements(
        state,
        player,
        creature_availability,
    ):
        return False

    if not barren_town:
        return True

    if (
        creature_availability.requires_flowers
        and not state.has_any(set(FLOWER_RESOURCE_ITEMS), player)
    ):
        return False

    if (
        creature_availability.requires_trees
        and not state.has_any(set(TREE_RESOURCE_ITEMS), player)
    ):
        return False

    return True


def can_catch_fish(
    state: "CollectionState",
    player: int,
    fish_name: str,
) -> bool:
    """Return whether AP logic considers the fish naturally catchable."""
    return _meets_availability_requirements(
        state,
        player,
        FISH_AVAILABILITY[fish_name],
    )


HIGH_RNG_BUGS: frozenset[str] = frozenset(
    name
    for name, creature_availability in BUG_AVAILABILITY.items()
    if creature_availability.high_rng
)

HIGH_RNG_FISH: frozenset[str] = frozenset(
    name
    for name, creature_availability in FISH_AVAILABILITY.items()
    if creature_availability.high_rng
)
