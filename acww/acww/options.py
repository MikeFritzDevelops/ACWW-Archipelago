from __future__ import annotations

from dataclasses import dataclass

from Options import Choice, DefaultOnToggle, PerGameCommonOptions, Range, Toggle


class BugCatchsanity(DefaultOnToggle):
    """Adds a location for each bug added to the player's journal."""

    display_name = "Bug Catchsanity"

class FishCatchsanity(DefaultOnToggle):
    """Adds a location for each fish added to the player's journal."""

    display_name = "Fish Catchsanity"

class ExcludeHighRNGCatchProgression(DefaultOnToggle):
    """
    Prevents the listed high-RNG Catch locations from containing progression.

    Their matching Donate locations remain normal progression locations.

    Bugs: Bee, Birdwing Butterfly, Oak Silk Moth, Mole Cricket, Flea,
    Dung Beetle, Pill Bug, Snail, Spider, Tarantula, and Scorpion.

    Fish: Tuna, Blue Marlin, Ocean Sunfish, Hammerhead Shark, Shark, and
    Coelacanth.
    """

    display_name = "Exclude High-RNG Catch Progression"


class BugJournalMilestones(DefaultOnToggle):
    """Adds checks for registering 1, 5, 10, 15, and 20 unique bugs."""

    display_name = "Bug Journal Milestones"


class FishJournalMilestones(DefaultOnToggle):
    """Adds checks for registering 1, 5, 10, 15, and 20 unique fish."""

    display_name = "Fish Journal Milestones"


class BugMuseumsanity(DefaultOnToggle):
    """Adds a location for each bug donated to the museum."""

    display_name = "Bug Museumsanity"

class FishMuseumsanity(DefaultOnToggle):
    """Adds a location for each fish donated to the museum."""

    display_name = "Fish Museumsanity"

class FossilMuseumsanity(DefaultOnToggle):
    """Adds a location for each fossil donated to the museum."""

    display_name = "Fossil Museumsanity"

class FossilExhibitCompletions(DefaultOnToggle):
    """
    Adds one check for completing each multi-part fossil exhibit.

    Fossil Museumsanity must also be enabled.
    """

    display_name = "Fossil Exhibit Completions"


class PaintingMuseumsanity(Toggle):
    """Adds a location for each painting donated to the museum."""

    display_name = "Painting Museumsanity"

class PaintingMilestones(Toggle):
    """
    Adds checks for donating 1, 5, and 10 paintings.

    Painting Museumsanity must also be enabled.
    """

    display_name = "Painting Milestones"

class FourLeafCloverCheck(Toggle):
    """Adds a check for finding a four-leaf clover."""

    display_name = "Four-Leaf Clover Check"


class StartWithTools(DefaultOnToggle):
    """
    When enabled, the Fishing Rod, Net, and Shovel are provided immediately.

    When disabled, players must obtain these tools normally from
    Tom Nook's rotating shop inventory.
    """

    display_name = "Start with Tools"


class StartingMonth(Choice):
    """
    Determines which month is available to the player at the start.

    Random Month selects one of the twelve months during generation.
    """

    display_name = "Starting Month"

    option_random_month = 0
    option_january = 1
    option_february = 2
    option_march = 3
    option_april = 4
    option_may = 5
    option_june = 6
    option_july = 7
    option_august = 8
    option_september = 9
    option_october = 10
    option_november = 11
    option_december = 12

    default = 0


class MuseumPercentageMilestones(Choice):
    """
    Adds checks at regular museum-completion percentages.

    Completion is calculated from the museum categories enabled in the seed.
    """

    display_name = "Museum Percentage Milestones"

    option_off = 0
    option_every_5_percent = 5
    option_every_10_percent = 10
    option_every_25_percent = 25

    default = 0


class Goal(Choice):
    """Determines the objective required to finish the game."""

    display_name = "Goal"

    option_museum_percentage = 0

    default = 0


class GoalPercentage(Range):
    """
    Percentage of enabled museum donations required for the
    Museum Percentage goal.
    """

    display_name = "Goal Percentage"

    range_start = 10
    range_end = 100
    default = 50


@dataclass
class ACWWOptions(PerGameCommonOptions):
    bug_catchsanity: BugCatchsanity
    fish_catchsanity: FishCatchsanity
    exclude_high_rng_catch_progression: ExcludeHighRNGCatchProgression
    bug_journal_milestones: BugJournalMilestones
    fish_journal_milestones: FishJournalMilestones

    bug_museumsanity: BugMuseumsanity
    fish_museumsanity: FishMuseumsanity
    fossil_museumsanity: FossilMuseumsanity
    fossil_exhibit_completions: FossilExhibitCompletions
    painting_museumsanity: PaintingMuseumsanity
    painting_milestones: PaintingMilestones
    four_leaf_clover_check: FourLeafCloverCheck
    museum_percentage_milestones: MuseumPercentageMilestones

    start_with_tools: StartWithTools
    starting_month: StartingMonth

    goal: Goal
    goal_percentage: GoalPercentage