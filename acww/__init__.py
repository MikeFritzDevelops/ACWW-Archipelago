from __future__ import annotations

from BaseClasses import (
    Entrance,
    Item,
    ItemClassification,
    Location,
    LocationProgressType,
    Region,
)
from worlds.AutoWorld import World
from . import client
from .availability import HIGH_RNG_BUGS, HIGH_RNG_FISH
from .rules import set_acww_rules
from .items import (
    bell_item_names,
    clothing_item_names,
    environment_item_names,
    fruit_item_names,
    golden_tool_item_names,
    item_name_to_id,
    item_table,
    month_item_names,
    progressive_tool_item_names,
)
from .locations import (
    BUGS,
    FISH,
    FOSSILS,
    PAINTINGS,
    bug_catch_locations,
    bug_journal_milestone_locations,
    bug_museum_locations,
    fish_catch_locations,
    fish_journal_milestone_locations,
    fish_museum_locations,
    fossil_exhibit_completion_locations,
    fossil_museum_locations,
    four_leaf_clover_locations,
    location_name_to_id,
    museum_percentage_milestone_locations,
    painting_milestone_locations,
    painting_museum_locations,
    starter_kit_locations,
)
from .options import ACWWOptions


class ACWWItem(Item):
    game = "Animal Crossing: Wild World"


class ACWWLocation(Location):
    game = "Animal Crossing: Wild World"


class AnimalCrossingWildWorldWorld(World):
    game = "Animal Crossing: Wild World"

    options_dataclass = ACWWOptions
    options: ACWWOptions

    item_name_to_id = item_name_to_id
    location_name_to_id = location_name_to_id

    origin_region_name = "Town"

    CLOTHING_FILLER_PERCENT = 20
    MAX_CLOTHING_FILLER = 100

    MONTH_NAMES = (
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

    resolved_starting_month: int

    def generate_early(self) -> None:
        """Resolve Random Month once so every generation step agrees."""
        configured_month = int(self.options.starting_month)

        if configured_month == 0:
            self.resolved_starting_month = self.random.randint(1, 12)
        elif 1 <= configured_month <= 12:
            self.resolved_starting_month = configured_month
        else:
            raise ValueError(
                f"Invalid ACWW starting month: {configured_month}"
            )

    def get_starting_month_number(self) -> int:
        """Return the month selected for this generated seed."""
        if not hasattr(self, "resolved_starting_month"):
            configured_month = int(self.options.starting_month)

            if configured_month == 0:
                raise RuntimeError(
                    "Random starting month was requested before "
                    "generate_early resolved it."
                )

            if not 1 <= configured_month <= 12:
                raise ValueError(
                    f"Invalid ACWW starting month: {configured_month}"
                )

            self.resolved_starting_month = configured_month

        return self.resolved_starting_month

    def get_starting_month_name(self) -> str:
        """Return the resolved starting month's AP item name."""
        month_number = self.get_starting_month_number()
        return self.MONTH_NAMES[month_number - 1]

    def get_enabled_museum_percentage_locations(
        self,
    ) -> dict[str, int]:
        """Return percentage milestones selected by the configured interval."""
        interval = int(self.options.museum_percentage_milestones)

        if interval <= 0:
            return {}

        return {
            location_name: location_id
            for location_name, location_id
            in museum_percentage_milestone_locations.items()
            if int(location_name.split()[1].rstrip("%")) % interval == 0
        }

    def get_enabled_locations(self) -> dict[str, int]:
        """Return only the locations enabled by this slot's options."""
        enabled: dict[str, int] = {}

        if self.options.bug_catchsanity:
            enabled.update(bug_catch_locations)

        if self.options.fish_catchsanity:
            enabled.update(fish_catch_locations)

        if self.options.bug_journal_milestones:
            enabled.update(bug_journal_milestone_locations)

        if self.options.fish_journal_milestones:
            enabled.update(fish_journal_milestone_locations)

        if self.options.bug_museumsanity:
            enabled.update(bug_museum_locations)

        if self.options.fish_museumsanity:
            enabled.update(fish_museum_locations)

        if self.options.fossil_museumsanity:
            enabled.update(fossil_museum_locations)

            if self.options.fossil_exhibit_completions:
                enabled.update(
                    fossil_exhibit_completion_locations
                )

        if self.options.painting_museumsanity:
            enabled.update(painting_museum_locations)

            if self.options.painting_milestones:
                enabled.update(painting_milestone_locations)

        if self.options.starter_kit:
            enabled.update(starter_kit_locations)

        if self.options.four_leaf_clover_check:
            enabled.update(four_leaf_clover_locations)

        enabled.update(
            self.get_enabled_museum_percentage_locations()
        )

        return enabled

    def create_regions(self) -> None:
        """Create the initial permissive region layout."""
        menu = Region("Menu", self.player, self.multiworld)
        town = Region("Town", self.player, self.multiworld)

        for location_name, location_id in (
            self.get_enabled_locations().items()
        ):
            location = ACWWLocation(
                self.player,
                location_name,
                location_id,
                town,
            )

            if (
                self.options.exclude_high_rng_catch_progression
                and location_name.startswith("Catch ")
            ):
                species_name = location_name.removeprefix("Catch ")

                if (
                    species_name in HIGH_RNG_BUGS
                    or species_name in HIGH_RNG_FISH
                ):
                    location.progress_type = (
                        LocationProgressType.EXCLUDED
                    )

            town.locations.append(location)

        goal_location = ACWWLocation(
            self.player,
            "Museum Goal",
            None,
            town,
        )
        goal_location.place_locked_item(
            ACWWItem(
                "Victory",
                ItemClassification.progression,
                None,
                self.player,
            )
        )
        town.locations.append(goal_location)

        # The tutorial grants stage one of the three progressive tools.
        if self.options.starter_kit:
            locked_starter_items = {
                "Complete Tutorial - Fishing Rod":
                    "Progressive Fishing Rod",
                "Complete Tutorial - Net":
                    "Progressive Net",
                "Complete Tutorial - Shovel":
                    "Progressive Shovel",
            }

            for location_name, item_name in locked_starter_items.items():
                location = self.multiworld.get_location(
                    location_name,
                    self.player,
                )
                location.place_locked_item(
                    self.create_item(item_name)
                )

        enter_town = Entrance(
            self.player,
            "Start Game",
            menu,
        )

        menu.exits.append(enter_town)
        enter_town.connect(town)

        self.multiworld.regions += [menu, town]

    def create_item(self, name: str) -> ACWWItem:
        """Create one ACWW item from the canonical item table."""
        data = item_table[name]

        return ACWWItem(
            name,
            data["classification"],
            data["id"],
            self.player,
        )

    def create_items(self) -> None:
        """
        Build the randomized museum-speedrun pool.

        Progression consists of tool upgrades, month unlocks, and physical
        museum specimens, and required bug-environment items. Filler
        consists of fruits, clothing, and Bells.
        """
        enabled_locations = self.get_enabled_locations()

        locked_location_count = (
            len(starter_kit_locations)
            if self.options.starter_kit
            else 0
        )

        randomized_location_count = (
            len(enabled_locations)
            - locked_location_count
        )

        item_names: list[str] = []

        # With the starter kit, stage one is locked to the tutorial and one
        # randomized copy remains for the golden upgrade. Without it, both
        # progressive copies must be randomized.
        progressive_copy_count = (
            1 if self.options.starter_kit else 2
        )

        for item_name in progressive_tool_item_names:
            item_names.extend(
                [item_name] * progressive_copy_count
            )

        item_names.extend(golden_tool_item_names)

        # The configured starting month is granted immediately and excluded
        # from the randomized pool. The remaining eleven months are shuffled
        # as progression items.
        starting_month_name = self.get_starting_month_name()

        self.multiworld.push_precollected(
            self.create_item(starting_month_name)
        )

        item_names.extend(
            month_name
            for month_name in month_item_names
            if month_name != starting_month_name
        )

        if self.options.bug_museumsanity:
            item_names.extend(
                f"Bug: {name}"
                for name in BUGS
            )

        if self.options.fish_museumsanity:
            item_names.extend(
                f"Fish: {name}"
                for name in FISH
            )

        if self.options.fossil_museumsanity:
            item_names.extend(
                f"Fossil: {name}"
                for name in FOSSILS
            )

        if self.options.painting_museumsanity:
            item_names.extend(
                f"Painting: {name}"
                for name in PAINTINGS
            )

        # Include one copy of every normal fruit before repeatable filler.
        item_names.extend(fruit_item_names)

        # Guarantee the environmental resources required by special bugs.
        # Three flowers of each required color gives the player redundancy;
        # two coconuts allow coconut trees to be established; one spoiled
        # turnip guarantees a deterministic Ant/Fly spawn route.
        required_environment_counts = {
            "Red Roses": 3,
            "White Roses": 3,
            "Pink Roses": 3,
            "Purple Roses": 3,
            "Black Roses": 3,
            "Blue Roses": 3,
            "Coconut": 2,
            "Spoiled Turnips": 1,
        }

        unknown_environment_items = (
            set(required_environment_counts)
            - set(environment_item_names)
        )

        if unknown_environment_items:
            raise ValueError(
                "Missing ACWW environment item definitions: "
                + ", ".join(sorted(unknown_environment_items))
            )

        for item_name, count in required_environment_counts.items():
            item_names.extend([item_name] * count)

        filler_count = randomized_location_count - len(item_names)

        if filler_count < 0:
            raise ValueError(
                "The enabled ACWW item pool contains more required items "
                "than randomized locations. Enable more checks or reduce "
                "the required item categories."
            )

        clothing_count = min(
            round(
                filler_count
                * self.CLOTHING_FILLER_PERCENT
                / 100
            ),
            self.MAX_CLOTHING_FILLER,
            len(clothing_item_names),
        )

        bell_count = filler_count - clothing_count

        # Clothing is unique within a seed. Bell bags may repeat.
        item_names.extend(
            self.random.sample(
                clothing_item_names,
                clothing_count,
            )
        )

        item_names.extend(
            self.random.choice(bell_item_names)
            for _ in range(bell_count)
        )

        if len(item_names) != randomized_location_count:
            raise ValueError(
                "ACWW item-pool size does not match the number of "
                "randomized locations."
            )

        self.multiworld.itempool += [
            self.create_item(name)
            for name in item_names
        ]

    def set_rules(self) -> None:
        """Attach ACWW access rules and the museum completion event."""
        set_acww_rules(self)

    def fill_slot_data(self) -> dict:
        """Send generated options and enabled location IDs to the client."""
        return {
            "client_version": 2,
            "enabled_locations": sorted(
                self.get_enabled_locations().values()
            ),
            "starter_kit": bool(self.options.starter_kit),
            "four_leaf_clover_check": bool(
                self.options.four_leaf_clover_check
            ),
            "painting_milestones": bool(
                self.options.painting_milestones
            ),
            "bug_journal_milestones": bool(
                self.options.bug_journal_milestones
            ),
            "fish_journal_milestones": bool(
                self.options.fish_journal_milestones
            ),
            "exclude_high_rng_catch_progression": bool(
                self.options.exclude_high_rng_catch_progression
            ),
            "fossil_exhibit_completions": bool(
                self.options.fossil_exhibit_completions
            ),
            "museum_percentage_milestones": int(
                self.options.museum_percentage_milestones
            ),
            "bug_museumsanity": bool(
                self.options.bug_museumsanity
            ),
            "fish_museumsanity": bool(
                self.options.fish_museumsanity
            ),
            "fossil_museumsanity": bool(
                self.options.fossil_museumsanity
            ),
            "painting_museumsanity": bool(
                self.options.painting_museumsanity
            ),
            "starting_month": self.get_starting_month_number(),
            "starting_month_name": self.get_starting_month_name(),
            "goal": self.options.goal.current_key,
            "goal_percentage": int(
                self.options.goal_percentage
            ),
        }
