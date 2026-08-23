# Changelog

## v0.1.2-alpha

## Added

- Added an option to Skip Tom Nook's Tutorial
- Added an option to set 'Barren Town' which removes all plants and trees from town at start, requiring player to sculpt their town to their desire to hunt bugs requiring flowers and trees.
- Added QoL feature to guarantee at least 1 tree in town always has a bee hive to make Bee hunting less of a grind.
- Added QoL feature to instantly grow trees to full mature state.
- Added Bee and Invisible Bee Traps as optional trap settings.
- Added Weather Control to Master Controller to allow for forced rain/snow.

## Changed

- Updated availability logic for weather-dependent bugs and fish to account for Weather Control.

## Fixed

- Fixed a bug that caused tools to be repeatedly added to inventory if one was lost/equipped.
- Fixed an issue where every check caused a full refresh of the Master Controller leading to performance issues.
- Fixed poptracker availability for some fish and bugs, and improved clarity of images.

## v0.1.1-alpha

### Added

- Refactored memory profile architecture to lay the groundwork for future game version support.
- Improved the inventory watcher to use stable inventory snapshots before processing changes.

### Changed

- **Starter Kit** renamed to **Start with Tools**
- **Start with Tools** now grants the tools without sending three initial checks.
- Normal tools no longer considered progression for logic; Golden tools remain randomized items.
- Updated PopTracker with monthly Bug and Fish Journals, improved availability information, and corrected bug and fish logic.

### Fixed

- Museum goal validation now raises an 'OptionError' instead of 'ValueError'.
- Fixed several client-side issues related to starting tool handling and internal state synchronization.
- General stability improvements and code cleanup.


## v0.1.0-alpha

### Added

- Catchsanity
- Museumsanity
- Museum percentage goals
- Journal milestones
- Fossil exhibit completion
- Master Controller
- Restore AP Progress
- Reclaimable resources and donatables
- Crash recovery
- High RNG catch progression exclusion