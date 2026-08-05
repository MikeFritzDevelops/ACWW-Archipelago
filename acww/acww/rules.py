from __future__ import annotations

import math
from typing import TYPE_CHECKING, Callable

from Options import OptionError
from worlds.generic.Rules import add_rule

from .availability import (
    can_catch_bug,
    can_catch_fish,
    validate_bug_availability,
    validate_fish_availability,
)
from .locations import (
    BUGS,
    FISH,
    FOSSILS,
    PAINTINGS,
    bug_journal_milestone_locations,
    fish_journal_milestone_locations,
    FOSSIL_EXHIBIT_GROUPS,
    fossil_exhibit_completion_locations,
    museum_percentage_milestone_locations,
    painting_milestone_locations,
)

if TYPE_CHECKING:
    from BaseClasses import CollectionState
    from . import AnimalCrossingWildWorldWorld


AccessPredicate = Callable[["CollectionState"], bool]


def _bug_donation_predicate(
    world: "AnimalCrossingWildWorldWorld",
    bug_name: str,
) -> AccessPredicate:
    return lambda state: (
        state.has(f"Bug: {bug_name}", world.player)
        and can_catch_bug(state, world.player, bug_name)
    )


def _fish_donation_predicate(
    world: "AnimalCrossingWildWorldWorld",
    fish_name: str,
) -> AccessPredicate:
    return lambda state: (
        state.has(f"Fish: {fish_name}", world.player)
        and can_catch_fish(state, world.player, fish_name)
    )


def _fossil_donation_predicate(
    world: "AnimalCrossingWildWorldWorld",
    fossil_name: str,
) -> AccessPredicate:
    # Physical fossil items are currently the guaranteed logical route.
    return lambda state: state.has(
        f"Fossil: {fossil_name}",
        world.player,
    )


def _painting_donation_predicate(
    world: "AnimalCrossingWildWorldWorld",
    painting_name: str,
) -> AccessPredicate:
    # Physical painting items are currently the guaranteed logical route.
    return lambda state: state.has(
        f"Painting: {painting_name}",
        world.player,
    )


def _set_bug_rules(
    world: "AnimalCrossingWildWorldWorld",
) -> list[AccessPredicate]:
    donation_predicates: list[AccessPredicate] = []

    if world.options.bug_catchsanity:
        for bug_name in BUGS:
            location = world.multiworld.get_location(
                f"Catch {bug_name}",
                world.player,
            )

            add_rule(
                location,
                lambda state, bug_name=bug_name:
                    can_catch_bug(
                        state,
                        world.player,
                        bug_name,
                    ),
            )

    if world.options.bug_museumsanity:
        for bug_name in BUGS:
            predicate = _bug_donation_predicate(
                world,
                bug_name,
            )
            donation_predicates.append(predicate)

            location = world.multiworld.get_location(
                f"Donate {bug_name}",
                world.player,
            )
            add_rule(location, predicate)

    return donation_predicates


def _set_fish_rules(
    world: "AnimalCrossingWildWorldWorld",
) -> list[AccessPredicate]:
    donation_predicates: list[AccessPredicate] = []

    if world.options.fish_catchsanity:
        for fish_name in FISH:
            location = world.multiworld.get_location(
                f"Catch {fish_name}",
                world.player,
            )

            add_rule(
                location,
                lambda state, fish_name=fish_name:
                    can_catch_fish(
                        state,
                        world.player,
                        fish_name,
                    ),
            )

    if world.options.fish_museumsanity:
        for fish_name in FISH:
            predicate = _fish_donation_predicate(
                world,
                fish_name,
            )
            donation_predicates.append(predicate)

            location = world.multiworld.get_location(
                f"Donate {fish_name}",
                world.player,
            )
            add_rule(location, predicate)

    return donation_predicates


def _set_journal_milestone_rules(
    world: "AnimalCrossingWildWorldWorld",
) -> None:
    """Require enough logically catchable unique species for each milestone."""
    milestone_counts = (1, 5, 10, 15, 20)

    if world.options.bug_journal_milestones:
        bug_predicates = [
            (
                lambda state, bug_name=bug_name:
                    can_catch_bug(
                        state,
                        world.player,
                        bug_name,
                    )
            )
            for bug_name in BUGS
        ]

        for index, required_count in enumerate(milestone_counts):
            location_name = (
                f"Register {required_count} Unique "
                f"Bug{'s' if required_count != 1 else ''} in the Journal"
            )
            location = world.multiworld.get_location(
                location_name,
                world.player,
            )

            add_rule(
                location,
                lambda state, required_count=required_count: sum(
                    1
                    for predicate in bug_predicates
                    if predicate(state)
                ) >= required_count,
            )

    if world.options.fish_journal_milestones:
        fish_predicates = [
            (
                lambda state, fish_name=fish_name:
                    can_catch_fish(
                        state,
                        world.player,
                        fish_name,
                    )
            )
            for fish_name in FISH
        ]

        for index, required_count in enumerate(milestone_counts):
            location_name = (
                f"Register {required_count} Unique Fish in the Journal"
            )
            location = world.multiworld.get_location(
                location_name,
                world.player,
            )

            add_rule(
                location,
                lambda state, required_count=required_count: sum(
                    1
                    for predicate in fish_predicates
                    if predicate(state)
                ) >= required_count,
            )


def _set_fossil_rules(
    world: "AnimalCrossingWildWorldWorld",
) -> list[AccessPredicate]:
    donation_predicates: list[AccessPredicate] = []

    if not world.options.fossil_museumsanity:
        return donation_predicates

    for fossil_name in FOSSILS:
        predicate = _fossil_donation_predicate(
            world,
            fossil_name,
        )
        donation_predicates.append(predicate)

        location = world.multiworld.get_location(
            f"Donate {fossil_name}",
            world.player,
        )
        add_rule(location, predicate)

    return donation_predicates


def _set_fossil_exhibit_completion_rules(
    world: "AnimalCrossingWildWorldWorld",
) -> None:
    """Require every physical fossil item belonging to an exhibit."""
    if (
        not world.options.fossil_museumsanity
        or not world.options.fossil_exhibit_completions
    ):
        return

    for exhibit_name, fossil_names in FOSSIL_EXHIBIT_GROUPS.items():
        location_name = f"Complete the {exhibit_name} Exhibit"

        if location_name not in fossil_exhibit_completion_locations:
            raise ValueError(
                "Missing fossil exhibit completion location: "
                + location_name
            )

        location = world.multiworld.get_location(
            location_name,
            world.player,
        )

        add_rule(
            location,
            lambda state, fossil_names=fossil_names: all(
                state.has(
                    f"Fossil: {fossil_name}",
                    world.player,
                )
                for fossil_name in fossil_names
            ),
        )


def _set_painting_rules(
    world: "AnimalCrossingWildWorldWorld",
) -> list[AccessPredicate]:
    donation_predicates: list[AccessPredicate] = []

    if not world.options.painting_museumsanity:
        return donation_predicates

    for painting_name in PAINTINGS:
        predicate = _painting_donation_predicate(
            world,
            painting_name,
        )
        donation_predicates.append(predicate)

        location = world.multiworld.get_location(
            f"Donate {painting_name}",
            world.player,
        )
        add_rule(location, predicate)

    return donation_predicates


def _set_painting_milestone_rules(
    world: "AnimalCrossingWildWorldWorld",
    painting_predicates: list[AccessPredicate],
) -> None:
    """Require enough logically obtainable paintings for each milestone."""
    if (
        not world.options.painting_museumsanity
        or not world.options.painting_milestones
    ):
        return

    milestones = {
        "Donate Your First Painting": 1,
        "Donate 5 Paintings": 5,
        "Donate 10 Paintings": 10,
    }

    unknown_locations = (
        set(milestones)
        - set(painting_milestone_locations)
    )

    if unknown_locations:
        raise ValueError(
            "Missing painting milestone location definitions: "
            + ", ".join(sorted(unknown_locations))
        )

    for location_name, required_count in milestones.items():
        location = world.multiworld.get_location(
            location_name,
            world.player,
        )

        add_rule(
            location,
            lambda state, required_count=required_count: sum(
                1
                for predicate in painting_predicates
                if predicate(state)
            ) >= required_count,
        )


def _set_museum_percentage_milestone_rules(
    world: "AnimalCrossingWildWorldWorld",
    donation_predicates: list[AccessPredicate],
) -> None:
    """Gate each selected milestone behind enough logical donations."""
    interval = int(world.options.museum_percentage_milestones)

    if interval <= 0 or not donation_predicates:
        return

    total_donations = len(donation_predicates)

    for percentage in range(interval, 101, interval):
        location_name = f"Complete {percentage}% of the Museum"

        if location_name not in museum_percentage_milestone_locations:
            raise ValueError(
                "Missing museum percentage milestone location: "
                + location_name
            )

        required_count = math.ceil(
            total_donations * percentage / 100
        )

        location = world.multiworld.get_location(
            location_name,
            world.player,
        )

        add_rule(
            location,
            lambda state, required_count=required_count: sum(
                1
                for predicate in donation_predicates
                if predicate(state)
            ) >= required_count,
        )


def _set_goal_rule(
    world: "AnimalCrossingWildWorldWorld",
    donation_predicates: list[AccessPredicate],
) -> None:
    goal_location = world.multiworld.get_location(
        "Museum Goal",
        world.player,
    )

    goal_percentage = int(world.options.goal_percentage)
    required_count = math.ceil(
        len(donation_predicates) * goal_percentage / 100
    )

    def goal_reached(state: "CollectionState") -> bool:
        completed_count = sum(
            1
            for predicate in donation_predicates
            if predicate(state)
        )
        return completed_count >= required_count

    add_rule(goal_location, goal_reached)

    world.multiworld.completion_condition[world.player] = (
        lambda state: state.has("Victory", world.player)
    )


def set_acww_rules(
    world: "AnimalCrossingWildWorldWorld",
) -> None:
    """Attach all current ACWW location and completion rules."""
    validate_bug_availability(BUGS)
    validate_fish_availability(FISH)

    bug_predicates = _set_bug_rules(world)
    fish_predicates = _set_fish_rules(world)
    fossil_predicates = _set_fossil_rules(world)
    painting_predicates = _set_painting_rules(world)

    donation_predicates = [
        *bug_predicates,
        *fish_predicates,
        *fossil_predicates,
        *painting_predicates,
    ]

    _set_fossil_exhibit_completion_rules(world)
    _set_painting_milestone_rules(
        world,
        painting_predicates,
    )
    _set_journal_milestone_rules(world)
    _set_museum_percentage_milestone_rules(
        world,
        donation_predicates,
    )

    if (
        world.options.goal.current_key == "museum_percentage"
        and not donation_predicates
    ):
        raise OptionError(
            "The Museum Percentage goal requires at least one enabled "
            "museum donation category."
        )

    _set_goal_rule(world, donation_predicates)
