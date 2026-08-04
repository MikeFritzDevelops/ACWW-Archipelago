from __future__ import annotations

STARTER_FISHING_ROD_LOCATION_ID = 2400
STARTER_NET_LOCATION_ID = 2401
STARTER_SHOVEL_LOCATION_ID = 2402
FOUR_LEAF_CLOVER_LOCATION_ID = 2403

PAINTING_MILESTONE_FIRST_LOCATION_ID = 2404
PAINTING_MILESTONE_FIVE_LOCATION_ID = 2405
PAINTING_MILESTONE_TEN_LOCATION_ID = 2406

BUG_JOURNAL_MILESTONE_BASE_ID = 2407
FISH_JOURNAL_MILESTONE_BASE_ID = 2412
FOSSIL_EXHIBIT_COMPLETION_BASE_ID = 2417
MUSEUM_PERCENTAGE_MILESTONE_BASE_ID = 2431

starter_kit_locations = {
    "Complete Tutorial - Fishing Rod": STARTER_FISHING_ROD_LOCATION_ID,
    "Complete Tutorial - Net": STARTER_NET_LOCATION_ID,
    "Complete Tutorial - Shovel": STARTER_SHOVEL_LOCATION_ID,
}

four_leaf_clover_locations = {
    "Find a Four-Leaf Clover": FOUR_LEAF_CLOVER_LOCATION_ID,
}

painting_milestone_locations = {
    "Donate Your First Painting": PAINTING_MILESTONE_FIRST_LOCATION_ID,
    "Donate 5 Paintings": PAINTING_MILESTONE_FIVE_LOCATION_ID,
    "Donate 10 Paintings": PAINTING_MILESTONE_TEN_LOCATION_ID,
}

JOURNAL_MILESTONE_COUNTS = (1, 5, 10, 15, 20)

bug_journal_milestone_locations = {
    f"Register {count} Unique Bug{'s' if count != 1 else ''} in the Journal":
        BUG_JOURNAL_MILESTONE_BASE_ID + index
    for index, count in enumerate(JOURNAL_MILESTONE_COUNTS)
}

fish_journal_milestone_locations = {
    f"Register {count} Unique Fish in the Journal":
        FISH_JOURNAL_MILESTONE_BASE_ID + index
    for index, count in enumerate(JOURNAL_MILESTONE_COUNTS)
}

MUSEUM_PERCENTAGE_VALUES = tuple(range(5, 101, 5))

museum_percentage_milestone_locations = {
    f"Complete {percentage}% of the Museum":
        MUSEUM_PERCENTAGE_MILESTONE_BASE_ID + index
    for index, percentage in enumerate(MUSEUM_PERCENTAGE_VALUES)
}


BUGS = [
    "Common Butterfly",
    "Yellow Butterfly",
    "Tiger Butterfly",
    "Peacock Butterfly",
    "Monarch Butterfly",
    "Emperor Butterfly",
    "Agrias Butterfly",
    "Birdwing Butterfly",
    "Moth",
    "Oak Silk Moth",
    "Honeybee",
    "Bee",
    "Long Locust",
    "Migratory Locust",
    "Mantis",
    "Orchid Mantis",
    "Brown Cicada",
    "Robust Cicada",
    "Walker Cicada",
    "Evening Cicada",
    "Lantern Fly",
    "Red Dragonfly",
    "Darner Dragonfly",
    "Banded Dragonfly",
    "Ant",
    "Pondskater",
    "Snail",
    "Cricket",
    "Bell Cricket",
    "Grasshopper",
    "Mole Cricket",
    "Walkingstick",
    "Ladybug",
    "Fruit Beetle",
    "Scarab Beetle",
    "Dung Beetle",
    "Goliath Beetle",
    "Firefly",
    "Jewel Beetle",
    "Longhorn Beetle",
    "Saw Stag Beetle",
    "Stag Beetle",
    "Giant Beetle",
    "Rainbow Stag Beetle",
    "Dynastid Beetle",
    "Atlas Beetle",
    "Elephant Beetle",
    "Hercules Beetle",
    "Flea",
    "Pill Bug",
    "Mosquito",
    "Fly",
    "Cockroach",
    "Spider",
    "Tarantula",
    "Scorpion",
]


FISH = [
    "Bitterling",
    "Pale Chub",
    "Crucian Carp",
    "Dace",
    "Barbel Steed",
    "Carp",
    "Koi",
    "Goldfish",
    "Popeyed Goldfish",
    "Killifish",
    "Crawfish",
    "Frog",
    "Freshwater Goby",
    "Loach",
    "Catfish",
    "Eel",
    "Giant Snakehead",
    "Bluegill",
    "Yellow Perch",
    "Black Bass",
    "Pond Smelt",
    "Sweetfish",
    "Cherry Salmon",
    "Char",
    "Rainbow Trout",
    "Stringfish",
    "Salmon",
    "King Salmon",
    "Guppy",
    "Angelfish",
    "Piranha",
    "Arowana",
    "Dorado",
    "Gar",
    "Arapaima",
    "Sea Butterfly",
    "Jellyfish",
    "Seahorse",
    "Clownfish",
    "Zebra Turkeyfish",
    "Pufferfish",
    "Horse Mackerel",
    "Barred Knifejaw",
    "Sea Bass",
    "Red Snapper",
    "Dab",
    "Olive Flounder",
    "Squid",
    "Octopus",
    "Football Fish",
    "Tuna",
    "Blue Marlin",
    "Ocean Sunfish",
    "Hammerhead Shark",
    "Shark",
    "Coelacanth",
]


FOSSILS = [
    "Amber",
    "Ammonite",
    "Dino Droppings",
    "Dinosaur Egg",
    "Fern Fossil",
    "Dinosaur Track",
    "Archaeopteryx",
    "Peking Man",
    "Shark Tooth",
    "Trilobite",
    "T-rex Skull",
    "T-rex Torso",
    "T-rex Tail",
    "Tricera Skull",
    "Tricera Torso",
    "Tricera Tail",
    "Mammoth Skull",
    "Mammoth Torso",
    "Ankylo Skull",
    "Ankylo Torso",
    "Ankylo Tail",
    "Apato Skull",
    "Apato Torso",
    "Apato Tail",
    "Dimetrodon Skull",
    "Dimetrodon Torso",
    "Dimetrodon Tail",
    "Iguanodon Skull",
    "Iguanodon Torso",
    "Iguanodon Tail",
    "Sabertooth Skull",
    "Sabertooth Torso",
    "Pachy Skull",
    "Pachy Torso",
    "Pachy Tail",
    "Parasaur Skull",
    "Parasaur Torso",
    "Parasaur Tail",
    "Seismo Skull",
    "Seismo Chest",
    "Seismo Hip",
    "Seismo Tail",
    "Plesio Skull",
    "Plesio Neck",
    "Plesio Torso",
    "Stego Skull",
    "Stego Torso",
    "Stego Tail",
    "Ptera Skull",
    "Ptera Torso",
    "Ptera Left Wing",
    "Ptera Right Wing",
]


FOSSIL_EXHIBIT_GROUPS: dict[str, tuple[str, ...]] = {
    "T-rex": (
        "T-rex Skull",
        "T-rex Torso",
        "T-rex Tail",
    ),
    "Tricera": (
        "Tricera Skull",
        "Tricera Torso",
        "Tricera Tail",
    ),
    "Mammoth": (
        "Mammoth Skull",
        "Mammoth Torso",
    ),
    "Ankylo": (
        "Ankylo Skull",
        "Ankylo Torso",
        "Ankylo Tail",
    ),
    "Apato": (
        "Apato Skull",
        "Apato Torso",
        "Apato Tail",
    ),
    "Dimetrodon": (
        "Dimetrodon Skull",
        "Dimetrodon Torso",
        "Dimetrodon Tail",
    ),
    "Iguanodon": (
        "Iguanodon Skull",
        "Iguanodon Torso",
        "Iguanodon Tail",
    ),
    "Sabertooth": (
        "Sabertooth Skull",
        "Sabertooth Torso",
    ),
    "Pachy": (
        "Pachy Skull",
        "Pachy Torso",
        "Pachy Tail",
    ),
    "Parasaur": (
        "Parasaur Skull",
        "Parasaur Torso",
        "Parasaur Tail",
    ),
    "Seismo": (
        "Seismo Skull",
        "Seismo Chest",
        "Seismo Hip",
        "Seismo Tail",
    ),
    "Plesio": (
        "Plesio Skull",
        "Plesio Neck",
        "Plesio Torso",
    ),
    "Stego": (
        "Stego Skull",
        "Stego Torso",
        "Stego Tail",
    ),
    "Ptera": (
        "Ptera Skull",
        "Ptera Torso",
        "Ptera Left Wing",
        "Ptera Right Wing",
    ),
}

fossil_exhibit_completion_locations = {
    f"Complete the {exhibit_name} Exhibit":
        FOSSIL_EXHIBIT_COMPLETION_BASE_ID + index
    for index, exhibit_name in enumerate(FOSSIL_EXHIBIT_GROUPS)
}


PAINTINGS = [
    "Dainty Painting",
    "Solemn Painting",
    "Quaint Painting",
    "Basic Painting",
    "Famous Painting",
    "Perfect Painting",
    "Amazing Painting",
    "Nice Painting",
    "Moving Painting",
    "Common Painting",
    "Flowery Painting",
    "Warm Painting",
    "Rare Painting",
    "Fine Painting",
    "Scary Painting",
    "Lovely Painting",
    "Strange Painting",
    "Worthy Painting",
    "Calm Painting",
    "Opulent Painting",
]


BUG_CATCH_BASE_ID = 1000
FISH_CATCH_BASE_ID = 1100

BUG_MUSEUM_BASE_ID = 2000
FISH_MUSEUM_BASE_ID = 2100
FOSSIL_MUSEUM_BASE_ID = 2200
PAINTING_MUSEUM_BASE_ID = 2300


bug_catch_locations = {
    f"Catch {name}": BUG_CATCH_BASE_ID + index
    for index, name in enumerate(BUGS)
}

fish_catch_locations = {
    f"Catch {name}": FISH_CATCH_BASE_ID + index
    for index, name in enumerate(FISH)
}

bug_museum_locations = {
    f"Donate {name}": BUG_MUSEUM_BASE_ID + index
    for index, name in enumerate(BUGS)
}

fish_museum_locations = {
    f"Donate {name}": FISH_MUSEUM_BASE_ID + index
    for index, name in enumerate(FISH)
}

fossil_museum_locations = {
    f"Donate {name}": FOSSIL_MUSEUM_BASE_ID + index
    for index, name in enumerate(FOSSILS)
}

painting_museum_locations = {
    f"Donate {name}": PAINTING_MUSEUM_BASE_ID + index
    for index, name in enumerate(PAINTINGS)
}


location_name_to_id = {
    **bug_catch_locations,
    **fish_catch_locations,
    **bug_museum_locations,
    **fish_museum_locations,
    **fossil_museum_locations,
    **painting_museum_locations,
    **starter_kit_locations,
    **four_leaf_clover_locations,
    **painting_milestone_locations,
    **bug_journal_milestone_locations,
    **fish_journal_milestone_locations,
    **fossil_exhibit_completion_locations,
    **museum_percentage_milestone_locations,
}


location_id_to_name = {
    location_id: name
    for name, location_id in location_name_to_id.items()
}