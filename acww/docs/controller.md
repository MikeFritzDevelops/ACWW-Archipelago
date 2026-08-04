# Animal Crossing: Wild World Master Controller

The Master Controller is a companion application that launches automatically after the Lua connector successfully connects to Animal Crossing: Wild World.

It provides quality-of-life features that make Archipelago playthroughs significantly more enjoyable while also offering recovery tools for crashes and save-state restores.

---

# Month Selection

Animal Crossing: Wild World normally follows the Nintendo DS system clock.

In Archipelago, seasonal progression is instead controlled by **Month** items.

The Month Selection menu allows you to switch between any months you have unlocked through Archipelago.

Only unlocked months may be selected.

This allows players to:

- Catch seasonal bugs
- Catch seasonal fish
- Complete museum goals
- Continue progression without waiting in real time

> **Important**
>
> During the opening cutscene, the game initializes its date using the system clock.
>
> Before collecting any checks, switch to one of your unlocked months to ensure the game matches your Archipelago progression. A bell chime should play and a short fade-out cutscene should play following the time change.

---

# Restore AP Progress

Loading an older save or save state can cause your in-game journal and museum to fall behind your Archipelago progress.

Restore AP Progress synchronizes:

- Bug Journal
- Fish Journal
- Museum Donations
- Fossil Exhibits

using your current Archipelago save data.

This tool does **not** resend Archipelago checks.

---

# Recover Undonated Specimens

If you lose progress after catching museum specimens but before donating them, the game may know you caught them while your inventory no longer contains them.

Recover Undonated Specimens recreates every bug, fish, fossil, painting that:

- has been received from Archipelago
- has not yet been donated

allowing you to finish museum donations without permanently losing progression.

Recovered specimens appear directly in your inventory.

> **Note**
>
> This feature is intended as crash and save-state recovery.
> Because the game cannot determine whether a specimen was sold, stored, or intentionally discarded, it relies on player honesty.

---

# Reclaim Renewable Resources

Planted flowers may be lost due to time travel or accidental destruction.

Reclaim Renewable Resources adds unlocked flowers and fruits to the inventory to allow the player to hunt specific catches as required.

---

# Weed Removal

Removes every weed currently present in town.

This is purely a quality-of-life feature and does not affect progression.

---

# Connection Status

The controller continuously monitors:

- Emulator connection
- Lua connection
- Archipelago connection

The status indicators update automatically while playing.

---

# Future Features

Planned improvements include:

- Additional ROM revision support
- Automatic month synchronization
- Additional quality-of-life utilities