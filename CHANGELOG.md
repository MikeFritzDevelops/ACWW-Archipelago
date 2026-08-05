# Changelog

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