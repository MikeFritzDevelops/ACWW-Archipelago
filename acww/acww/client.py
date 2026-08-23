from __future__ import annotations

from typing import TYPE_CHECKING

import json
import time
from pathlib import Path

import worlds._bizhawk as bizhawk
from NetUtils import ClientStatus
from worlds._bizhawk.client import BizHawkClient
from .items import (
    MONTHS,
    item_table,
    received_item_data_by_ap_id,
)
from .rom_profiles import RomProfile, identify_rom_profile
from .locations import (
    BUGS,
    FISH,
    FOSSILS,
    PAINTINGS,
    location_id_to_name,
)

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext


class AnimalCrossingWildWorldClient(BizHawkClient):
    game = "Animal Crossing: Wild World"
    system = "NDS"
    patch_suffix = None

    # Catch-journal location IDs
    BUG_CATCH_BASE_ID = 1000
    FISH_CATCH_BASE_ID = 1100

    # Museum location IDs
    BUG_MUSEUM_BASE_ID = 2000
    FISH_MUSEUM_BASE_ID = 2100
    FOSSIL_MUSEUM_BASE_ID = 2200
    PAINTING_MUSEUM_BASE_ID = 2300

    # Standalone inventory-observation checks
    FOUR_LEAF_CLOVER_LOCATION_ID = 2403
    FOUR_LEAF_CLOVER_ITEM_ID = 0x1428

    PAINTING_MILESTONE_LOCATIONS = (
        (1, 2404),
        (5, 2405),
        (10, 2406),
    )

    BUG_JOURNAL_MILESTONE_LOCATIONS = (
        (1, 2407),
        (5, 2408),
        (10, 2409),
        (15, 2410),
        (20, 2411),
    )

    FISH_JOURNAL_MILESTONE_LOCATIONS = (
        (1, 2412),
        (5, 2413),
        (10, 2414),
        (15, 2415),
        (20, 2416),
    )

    MUSEUM_PERCENTAGE_MILESTONE_BASE_ID = 2431

    FOSSIL_EXHIBIT_COMPLETION_LOCATIONS = (
        ((10, 11, 12), 2417),          # T-rex
        ((13, 14, 15), 2418),          # Tricera
        ((16, 17), 2419),              # Mammoth
        ((18, 19, 20), 2420),          # Ankylo
        ((21, 22, 23), 2421),          # Apato
        ((24, 25, 26), 2422),          # Dimetrodon
        ((27, 28, 29), 2423),          # Iguanodon
        ((30, 31), 2424),              # Sabertooth
        ((32, 33, 34), 2425),          # Pachy
        ((35, 36, 37), 2426),          # Parasaur
        ((38, 39, 40, 41), 2427),      # Seismo
        ((42, 43, 44), 2428),          # Plesio
        ((45, 46, 47), 2429),          # Stego
        ((48, 49, 50, 51), 2430),      # Ptera
    )

    rom_profile: RomProfile | None = None


    OVERLAY_UPDATE_INTERVAL_SECONDS = 1.0
    INVENTORY_STABLE_SECONDS = 2.0
    BEE_TREE_CHECK_INTERVAL_SECONDS = 5.0
    TRAP_COOLDOWN_SECONDS = 60.0
    TRAP_OUTSIDE_STABLE_SECONDS = 5.0

    BEE_ATTACK_DATA_VALUE = 0x0011FF00
    BEE_IDLE_SEQUENCE_VALUE = 0x13
    BEE_TRAP_SEQUENCE_VALUES = {
        "Bee Trap": 0x04,
        "Invisible Bee Trap": 0x02,
    }

    NORMAL_TREE_OBJECT_ID = 0x002A
    NORMAL_TREE_WITH_BEEHIVE_OBJECT_ID = 0x0067
    CEDAR_TREE_OBJECT_ID = 0x0061
    CEDAR_TREE_WITH_BEEHIVE_OBJECT_ID = 0x006B

    # QoL: immediately mature planted/growing trees. Money trees are
    # intentionally excluded so this cannot be used to generate instant bells.
    TREE_GROWTH_TO_MATURE = {
        **{object_id: 0x002A for object_id in range(0x0025, 0x002A)},  # Normal
        **{object_id: 0x0033 for object_id in range(0x002F, 0x0033)},  # Peach
        **{object_id: 0x003B for object_id in range(0x0037, 0x003B)},  # Apple
        **{object_id: 0x0043 for object_id in range(0x003F, 0x0043)},  # Orange
        **{object_id: 0x004B for object_id in range(0x0047, 0x004B)},  # Pear
        **{object_id: 0x0053 for object_id in range(0x004F, 0x0053)},  # Cherry
        **{object_id: 0x0061 for object_id in range(0x005C, 0x0061)},  # Evergreen
        **{object_id: 0x00CC for object_id in range(0x00C7, 0x00CC)},  # Coconut
    }

    def _require_rom_profile(self) -> RomProfile:
        profile = self.rom_profile

        if profile is None:
            raise RuntimeError(
                "ACWW memory was accessed before ROM validation."
            )

        return profile

    @property
    def memory(self):
        return self._require_rom_profile().memory

    @staticmethod
    def _count_range(
        locations: set[int],
        base_id: int,
        count: int,
    ) -> int:
        return sum(
            1
            for location_id in range(base_id, base_id + count)
            if location_id in locations
        )

    def _get_goal_progress(
        self,
        ctx: "BizHawkClientContext",
        completed_locations: set[int],
        enabled_locations: set[int],
    ) -> tuple[str, int, int]:
        """Return the goal label, current progress, and required progress."""
        bug_museum = self._count_range(
            completed_locations,
            self.BUG_MUSEUM_BASE_ID,
            self.memory.bug_count,
        )
        fish_museum = self._count_range(
            completed_locations,
            self.FISH_MUSEUM_BASE_ID,
            self.memory.fish_count,
        )
        fossil_museum = self._count_range(
            completed_locations,
            self.FOSSIL_MUSEUM_BASE_ID,
            self.memory.fossil_count,
        )
        painting_museum = self._count_range(
            completed_locations,
            self.PAINTING_MUSEUM_BASE_ID,
            self.memory.painting_count,
        )

        enabled_bug_museum = self._count_range(
            enabled_locations,
            self.BUG_MUSEUM_BASE_ID,
            self.memory.bug_count,
        )
        enabled_fish_museum = self._count_range(
            enabled_locations,
            self.FISH_MUSEUM_BASE_ID,
            self.memory.fish_count,
        )
        enabled_fossil_museum = self._count_range(
            enabled_locations,
            self.FOSSIL_MUSEUM_BASE_ID,
            self.memory.fossil_count,
        )
        enabled_painting_museum = self._count_range(
            enabled_locations,
            self.PAINTING_MUSEUM_BASE_ID,
            self.memory.painting_count,
        )

        museum_current = (
            bug_museum
            + fish_museum
            + fossil_museum
            + painting_museum
        )
        museum_total = (
            enabled_bug_museum
            + enabled_fish_museum
            + enabled_fossil_museum
            + enabled_painting_museum
        )

        goal_key = "museum_percentage"
        goal_percentage = 100

        if ctx.slot_data:
            goal_key = str(
                ctx.slot_data.get("goal", goal_key)
            )
            goal_percentage = int(
                ctx.slot_data.get(
                    "goal_percentage",
                    goal_percentage,
                )
            )

        if goal_key == "all_bugs":
            return (
                "All Bugs",
                bug_museum,
                enabled_bug_museum or self.memory.bug_count,
            )

        if goal_key == "all_fish":
            return (
                "All Fish",
                fish_museum,
                enabled_fish_museum or self.memory.fish_count,
            )

        if goal_key == "all_fossils":
            return (
                "All Fossils",
                fossil_museum,
                enabled_fossil_museum or self.memory.fossil_count,
            )

        if goal_key == "completed_museum":
            return (
                "Complete Museum",
                museum_current,
                museum_total,
            )

        goal_required = (
            (museum_total * goal_percentage + 99) // 100
            if museum_total
            else 0
        )

        return (
            f"Museum {goal_percentage}%",
            museum_current,
            goal_required,
        )

    def _build_progress_overlay(
        self,
        ctx: "BizHawkClientContext",
        completed_locations: set[int],
        enabled_locations: set[int],
    ) -> str:
        bug_catches = self._count_range(
            completed_locations,
            self.BUG_CATCH_BASE_ID,
            self.memory.bug_count,
        )
        fish_catches = self._count_range(
            completed_locations,
            self.FISH_CATCH_BASE_ID,
            self.memory.fish_count,
        )
        bug_museum = self._count_range(
            completed_locations,
            self.BUG_MUSEUM_BASE_ID,
            self.memory.bug_count,
        )
        fish_museum = self._count_range(
            completed_locations,
            self.FISH_MUSEUM_BASE_ID,
            self.memory.fish_count,
        )
        fossil_museum = self._count_range(
            completed_locations,
            self.FOSSIL_MUSEUM_BASE_ID,
            self.memory.fossil_count,
        )
        painting_museum = self._count_range(
            completed_locations,
            self.PAINTING_MUSEUM_BASE_ID,
            self.memory.painting_count,
        )

        enabled_bug_catches = self._count_range(
            enabled_locations,
            self.BUG_CATCH_BASE_ID,
            self.memory.bug_count,
        )
        enabled_fish_catches = self._count_range(
            enabled_locations,
            self.FISH_CATCH_BASE_ID,
            self.memory.fish_count,
        )
        enabled_bug_museum = self._count_range(
            enabled_locations,
            self.BUG_MUSEUM_BASE_ID,
            self.memory.bug_count,
        )
        enabled_fish_museum = self._count_range(
            enabled_locations,
            self.FISH_MUSEUM_BASE_ID,
            self.memory.fish_count,
        )
        enabled_fossil_museum = self._count_range(
            enabled_locations,
            self.FOSSIL_MUSEUM_BASE_ID,
            self.memory.fossil_count,
        )
        enabled_painting_museum = self._count_range(
            enabled_locations,
            self.PAINTING_MUSEUM_BASE_ID,
            self.memory.painting_count,
        )

        checked_count = len(completed_locations & enabled_locations)
        total_checks = len(enabled_locations)

        goal_label, goal_current, goal_required = (
            self._get_goal_progress(
                ctx,
                completed_locations,
                enabled_locations,
            )
        )

        unlocked_months = self._get_unlocked_months(ctx)
        unlocked_month_names = [
            MONTHS[month_number - 1]
            for month_number in unlocked_months
        ]

        goal_display = (
            f"Goal: {goal_label}  {goal_current}/{goal_required}"
        )

        if goal_required > 0 and goal_current >= goal_required:
            goal_display += "  COMPLETE"

        lines = [
            "ACWW Archipelago",
            goal_display,
            f"Checks: {checked_count}/{total_checks}",
            "Months: " + (
                ", ".join(unlocked_month_names)
                if unlocked_month_names
                else "None"
            ),
        ]

        if enabled_bug_catches:
            lines.append(
                f"Bug catches: {bug_catches}/{enabled_bug_catches}"
            )

        if enabled_fish_catches:
            lines.append(
                f"Fish catches: {fish_catches}/{enabled_fish_catches}"
            )

        if enabled_bug_museum:
            lines.append(
                f"Bug museum: {bug_museum}/{enabled_bug_museum}"
            )

        if enabled_fish_museum:
            lines.append(
                f"Fish museum: {fish_museum}/{enabled_fish_museum}"
            )

        if enabled_fossil_museum:
            lines.append(
                f"Fossils: {fossil_museum}/{enabled_fossil_museum}"
            )

        if enabled_painting_museum:
            lines.append(
                f"Art: {painting_museum}/{enabled_painting_museum}"
            )

        delivery_cursor = getattr(
            self,
            "delivery_cursor",
            len(ctx.items_received),
        )
        pending_count = max(
            0,
            len(ctx.items_received) - delivery_cursor,
        )
        if pending_count:
            lines.append(f"Items waiting: {pending_count}")

        return "\n".join(lines)

    async def _update_progress_overlay(
        self,
        ctx: "BizHawkClientContext",
        completed_locations: set[int],
        enabled_locations: set[int],
    ) -> None:
        overlay_text = self._build_progress_overlay(
            ctx,
            completed_locations,
            enabled_locations,
        )
        overlay_lines = overlay_text.splitlines()

        if overlay_lines == getattr(
            self,
            "_previous_overlay_lines",
            None,
        ):
            return

        responses = await bizhawk.send_requests(
            ctx.bizhawk_ctx,
            [
                {
                    "type": "SET_OVERLAY",
                    "visible": True,
                    "x": 5,
                    "y": 5,
                    "line_height": 13,
                    "foreground": "white",
                    "background": "black",
                    "lines": overlay_lines,
                }
            ],
        )

        if (
            not responses
            or responses[0].get("type")
            != "SET_OVERLAY_RESPONSE"
        ):
            raise bizhawk.SyncError(
                "BizHawk connector did not acknowledge "
                "SET_OVERLAY."
            )

        self._previous_overlay_lines = overlay_lines

    @staticmethod
    def _player_name(
        ctx: "BizHawkClientContext",
        player_id: int,
    ) -> str:
        player_names = getattr(ctx, "player_names", None)

        if isinstance(player_names, dict):
            name = player_names.get(player_id)
            if name:
                return str(name)

        slot_info = getattr(ctx, "slot_info", None)

        if isinstance(slot_info, dict):
            info = slot_info.get(player_id)
            name = getattr(info, "name", None)

            if name:
                return str(name)

        if player_id == getattr(ctx, "slot", None):
            return str(getattr(ctx, "auth", None) or "You")

        return f"Player {player_id}"

    @staticmethod
    def _item_name_for_network_item(
        ctx: "BizHawkClientContext",
        network_item,
    ) -> str:
        item_names = getattr(ctx, "item_names", None)

        if item_names is not None:
            lookup = getattr(item_names, "lookup_in_game", None)

            if callable(lookup):
                try:
                    return str(
                        lookup(
                            network_item.item,
                            network_item.player,
                        )
                    )
                except (KeyError, TypeError, ValueError):
                    pass

            lookup = getattr(item_names, "lookup_in_slot", None)

            if callable(lookup):
                try:
                    return str(
                        lookup(
                            network_item.item,
                            network_item.player,
                        )
                    )
                except (KeyError, TypeError, ValueError):
                    pass

        item_data = received_item_data_by_ap_id.get(
            network_item.item
        )

        if item_data:
            return str(item_data["name"])

        return f"Item {network_item.item}"

    async def _show_check_notification(
        self,
        ctx: "BizHawkClientContext",
        location_id: int,
    ) -> None:
        location_name = location_id_to_name.get(
            location_id,
            f"Location {location_id}",
        )

        location_info = getattr(
            ctx,
            "locations_info",
            {},
        ).get(location_id)

        if location_info is None:
            lines = [
                location_name,
                "Check sent to Archipelago",
            ]
        else:
            item_name = self._item_name_for_network_item(
                ctx,
                location_info,
            )
            sender_name = self._player_name(
                ctx,
                getattr(ctx, "slot", 0) or 0,
            )
            recipient_name = self._player_name(
                ctx,
                location_info.player,
            )

            lines = [
                location_name,
                f"{sender_name} sent {item_name}",
                f"to {recipient_name}",
            ]

        responses = await bizhawk.send_requests(
            ctx.bizhawk_ctx,
            [
                {
                    "type": "SHOW_ACWW_NOTIFICATION",
                    "lines": lines,
                    "duration_frames": 300,
                    "x": 5,
                    "y": 150,
                }
            ],
        )

        if (
            not responses
            or responses[0].get("type")
            != "SHOW_ACWW_NOTIFICATION_RESPONSE"
        ):
            raise bizhawk.SyncError(
                "BizHawk connector did not acknowledge "
                "SHOW_ACWW_NOTIFICATION."
            )

    async def _show_received_item_notification(
        self,
        ctx: "BizHawkClientContext",
        network_item,
        item_name: str,
        *,
        delivered_to_inventory: bool,
        detail_line_override: str | None = None,
    ) -> None:
        sender_name = self._player_name(
            ctx,
            network_item.player,
        )

        if detail_line_override is not None:
            detail_line = detail_line_override
        elif delivered_to_inventory:
            detail_line = "Added to your inventory"
        else:
            detail_line = "Unlock activated"

        responses = await bizhawk.send_requests(
            ctx.bizhawk_ctx,
            [
                {
                    "type": "SHOW_ACWW_NOTIFICATION",
                    "lines": [
                        f"Received {item_name}",
                        f"from {sender_name}",
                        detail_line,
                    ],
                    "duration_frames": 300,
                    "x": 5,
                    "y": 150,
                }
            ],
        )

        if (
            not responses
            or responses[0].get("type")
            != "SHOW_ACWW_NOTIFICATION_RESPONSE"
        ):
            raise bizhawk.SyncError(
                "BizHawk connector did not acknowledge "
                "SHOW_ACWW_NOTIFICATION."
            )

    @staticmethod
    def _month_number_from_name(month_name: str) -> int | None:
        try:
            return MONTHS.index(month_name) + 1
        except ValueError:
            return None

    def _get_unlocked_months(
        self,
        ctx: "BizHawkClientContext",
    ) -> list[int]:
        """
        Rebuild the unlocked-month set from authoritative AP state.

        The configured starting month comes from slot_data. Every received
        virtual item in the "month" category adds its matching month.
        """
        unlocked: set[int] = set()

        if ctx.slot_data:
            starting_month = ctx.slot_data.get("starting_month")

            if isinstance(starting_month, int):
                if 1 <= starting_month <= 12:
                    unlocked.add(starting_month)

        for network_item in ctx.items_received:
            item_data = received_item_data_by_ap_id.get(
                network_item.item
            )

            if not item_data:
                continue

            if item_data.get("category") != "month":
                continue

            month_number = self._month_number_from_name(
                item_data["name"]
            )

            if month_number is not None:
                unlocked.add(month_number)

        return sorted(unlocked)

    def _get_unlocked_controller_controls(
        self,
        ctx: "BizHawkClientContext",
    ) -> list[str]:
        """Return Master Controller abilities permanently unlocked by AP."""
        unlocked: set[str] = set()

        for network_item in ctx.items_received:
            item_data = received_item_data_by_ap_id.get(
                network_item.item
            )
            if not item_data:
                continue
            if item_data.get("category") != "controller_unlock":
                continue
            unlocked.add(str(item_data["name"]))

        return sorted(unlocked)

    def _get_unlocked_claimables(
        self,
        ctx: "BizHawkClientContext",
    ) -> list[dict[str, int | str]]:
        """
        Return permanently reclaimable physical resources received from AP.

        Fruit, environment items, and Golden Tools are treated as permanent
        unlocks. Once received, the Lua master controller may create replacement
        copies in empty inventory slots whenever the player needs them.
        """
        claimables_by_name: dict[str, dict[str, int | str]] = {}

        for network_item in ctx.items_received:
            item_data = received_item_data_by_ap_id.get(
                network_item.item
            )

            if not item_data:
                continue

            if item_data.get("category") not in {
                "fruit",
                "environment",
                "golden_tool",
            }:
                continue

            game_item_id = item_data.get("game_id")

            if game_item_id is None:
                continue

            item_name = str(item_data["name"])

            claimables_by_name[item_name] = {
                "name": item_name,
                "game_id": int(game_item_id),
            }

        return [
            claimables_by_name[name]
            for name in sorted(claimables_by_name)
        ]

    def _get_server_checked_locations(
        self,
        ctx: "BizHawkClientContext",
    ) -> tuple[set[int], set[int]]:
        """Return enabled and server-confirmed completed location IDs."""
        enabled_locations: set[int] = set()

        if ctx.slot_data:
            enabled_locations = set(
                ctx.slot_data.get("enabled_locations", [])
            )

        missing_locations = set(
            getattr(ctx, "missing_locations", set()) or set()
        )
        checked_locations = enabled_locations - missing_locations
        checked_locations.update(
            set(
                getattr(ctx, "checked_locations", set())
                or set()
            )
        )

        return enabled_locations, checked_locations

    def _get_reclaimable_specimens(
        self,
        ctx: "BizHawkClientContext",
        inventory_data: bytes,
    ) -> list[dict[str, int | str]]:
        """
        Return undonated specimens recoverable from authoritative AP state.

        Bugs and fish qualify after either their Catch location is complete or
        their matching AP specimen item has been received. Fossils and
        paintings qualify after their matching AP item has been received.
        A specimen is omitted once its Donate location is complete or while a
        copy is already present in the current inventory snapshot.
        """
        enabled_locations, checked_locations = (
            self._get_server_checked_locations(ctx)
        )

        received_specimen_names: set[str] = set()

        for network_item in ctx.items_received:
            item_data = received_item_data_by_ap_id.get(
                network_item.item
            )

            if not item_data:
                continue

            if item_data.get("category") not in {
                "bug",
                "fish",
                "fossil",
                "painting",
            }:
                continue

            received_specimen_names.add(str(item_data["name"]))

        inventory_item_ids = {
            int.from_bytes(
                inventory_data[offset:offset + 2],
                byteorder="little",
            )
            for offset in range(
                0,
                len(inventory_data),
                self.memory.inventory_slot_size,
            )
            if len(inventory_data[offset:offset + 2]) == 2
        }

        category_data = (
            (
                "Bugs",
                "Bug",
                BUGS,
                self.BUG_CATCH_BASE_ID,
                self.BUG_MUSEUM_BASE_ID,
            ),
            (
                "Fish",
                "Fish",
                FISH,
                self.FISH_CATCH_BASE_ID,
                self.FISH_MUSEUM_BASE_ID,
            ),
            (
                "Fossils",
                "Fossil",
                FOSSILS,
                None,
                self.FOSSIL_MUSEUM_BASE_ID,
            ),
            (
                "Paintings",
                "Painting",
                PAINTINGS,
                None,
                self.PAINTING_MUSEUM_BASE_ID,
            ),
        )

        reclaimable: list[dict[str, int | str]] = []

        for (
            category_label,
            item_prefix,
            names,
            catch_base_id,
            donation_base_id,
        ) in category_data:
            for index, specimen_name in enumerate(names):
                donation_location_id = donation_base_id + index

                # No donation check exists for this category in this slot.
                if donation_location_id not in enabled_locations:
                    continue

                # Server truth says this specimen was already donated.
                if donation_location_id in checked_locations:
                    continue

                item_name = f"{item_prefix}: {specimen_name}"
                received = item_name in received_specimen_names
                caught = (
                    catch_base_id is not None
                    and catch_base_id + index in checked_locations
                )

                if not (received or caught):
                    continue

                item_data = item_table.get(item_name)
                game_item_id = (
                    item_data.get("game_id")
                    if item_data
                    else None
                )

                if game_item_id is None:
                    continue

                game_item_id = int(game_item_id)

                if game_item_id in inventory_item_ids:
                    continue

                reclaimable.append({
                    "category": category_label,
                    "name": specimen_name,
                    "game_id": game_item_id,
                })

        return sorted(
            reclaimable,
            key=lambda entry: (
                str(entry["category"]),
                str(entry["name"]),
            ),
        )

    def _get_restore_progress_payload(
        self,
        ctx: "BizHawkClientContext",
    ) -> dict[str, list[int]]:
        """
        Convert server-confirmed AP locations into restorable save indexes.

        Only individual Catch and Donate locations are used. Milestone checks
        do not identify which exact species or exhibits created them.
        """
        _, checked_locations = self._get_server_checked_locations(
            ctx
        )

        def checked_indexes(
            base_id: int,
            count: int,
        ) -> list[int]:
            return [
                index
                for index in range(count)
                if base_id + index in checked_locations
            ]

        return {
            "bugs": checked_indexes(
                self.BUG_CATCH_BASE_ID,
                self.memory.bug_count,
            ),
            "fish": checked_indexes(
                self.FISH_CATCH_BASE_ID,
                self.memory.fish_count,
            ),
            "museum_bugs": checked_indexes(
                self.BUG_MUSEUM_BASE_ID,
                self.memory.bug_count,
            ),
            "museum_fish": checked_indexes(
                self.FISH_MUSEUM_BASE_ID,
                self.memory.fish_count,
            ),
            "museum_fossils": checked_indexes(
                self.FOSSIL_MUSEUM_BASE_ID,
                self.memory.fossil_count,
            ),
            "museum_paintings": checked_indexes(
                self.PAINTING_MUSEUM_BASE_ID,
                self.memory.painting_count,
            ),
        }

    async def _update_controller_state(
        self,
        ctx: "BizHawkClientContext",
        unlocked_months: list[int],
        unlocked_controls: list[str],
        claimables: list[dict[str, int | str]],
        reclaimable_specimens: list[dict[str, int | str]],
        restore_payload: dict[str, list[int]],
    ) -> None:
        """Initialize the Lua controller once, then send only changed sections."""
        profile = self._require_rom_profile()

        controller_state = {
            "rom_profile": {
                "key": profile.key,
                "display_name": profile.display_name,
                "memory": profile.memory.to_lua_payload(),
                "outside_state_address": (
                    0x02000000 + profile.outside_state_address
                ),
            },
            "unlocked_months": list(unlocked_months),
            "unlocked_controls": list(unlocked_controls),
            "claimables": [
                dict(claimable)
                for claimable in claimables
            ],
            "reclaimable_specimens": [
                dict(specimen)
                for specimen in reclaimable_specimens
            ],
            "restore_progress": {
                key: list(indexes)
                for key, indexes in restore_payload.items()
            },
        }

        previous_state = getattr(
            self,
            "_controller_state_sent_to_lua",
            None,
        )

        # The full state is only needed when the Lua controller is first
        # initialized for this ROM/slot connection.
        if previous_state is None:
            responses = await bizhawk.send_requests(
                ctx.bizhawk_ctx,
                [{
                    "type": "SET_ACWW_STATE",
                    "state": controller_state,
                }],
            )

            if (
                not responses
                or responses[0].get("type")
                != "SET_ACWW_STATE_RESPONSE"
            ):
                raise bizhawk.SyncError(
                    "BizHawk connector did not acknowledge "
                    "SET_ACWW_STATE."
                )

            self._controller_state_sent_to_lua = controller_state
            return

        changed_state = {
            key: controller_state[key]
            for key in (
                "unlocked_months",
                "unlocked_controls",
                "claimables",
                "reclaimable_specimens",
                "restore_progress",
            )
            if controller_state[key] != previous_state.get(key)
        }

        if not changed_state:
            return

        responses = await bizhawk.send_requests(
            ctx.bizhawk_ctx,
            [{
                "type": "UPDATE_ACWW_STATE",
                "state": changed_state,
            }],
        )

        if (
            not responses
            or responses[0].get("type")
            != "UPDATE_ACWW_STATE_RESPONSE"
        ):
            raise bizhawk.SyncError(
                "BizHawk connector did not acknowledge "
                "UPDATE_ACWW_STATE."
            )

        self._controller_state_sent_to_lua = controller_state

    DELIVERY_STATE_PATH = (
        Path.home()
        / ".archipelago"
        / "acww_delivery_state.json"
    )

    def _delivery_state_key(
        self,
        ctx: "BizHawkClientContext",
    ) -> str | None:
        """Build a persistent key only when AP exposes a real seed identity.

        Never persist under a generic fallback: doing so can make unrelated
        generated seeds with the same team/slot/auth share delivery/trap state.
        """
        seed_value = (
            getattr(ctx, "seed_name", None)
            or getattr(ctx, "seed", None)
        )
        if not seed_value:
            return None

        seed_name = str(seed_value)
        team = int(getattr(ctx, "team", 0) or 0)
        slot = int(getattr(ctx, "slot", 0) or 0)
        auth = str(getattr(ctx, "auth", "") or "")

        return f"{seed_name}|team={team}|slot={slot}|auth={auth}"

    def _read_delivery_state_file(self) -> dict[str, int]:
        try:
            if not self.DELIVERY_STATE_PATH.exists():
                return {}

            raw = json.loads(
                self.DELIVERY_STATE_PATH.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(raw, dict):
                return {}

            result: dict[str, int] = {}

            for key, value in raw.items():
                if isinstance(key, str) and isinstance(value, int):
                    result[key] = max(0, value)

            return result
        except (OSError, ValueError, TypeError):
            return {}

    def _write_delivery_state_file(
        self,
        state_data: dict[str, int],
    ) -> None:
        self.DELIVERY_STATE_PATH.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_path = self.DELIVERY_STATE_PATH.with_suffix(
            ".tmp"
        )

        temporary_path.write_text(
            json.dumps(
                state_data,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

        temporary_path.replace(self.DELIVERY_STATE_PATH)

    def _load_delivery_cursor(
        self,
        ctx: "BizHawkClientContext",
        completed_locations: set[int],
    ) -> int:
        state_key = self._delivery_state_key(ctx)
        state_data = self._read_delivery_state_file()

        if state_key is None:
            # No trustworthy seed identity means disk persistence is unsafe.
            # Preserve the old migration behavior without sharing state across seeds.
            server_checked = set(
                getattr(ctx, "checked_locations", set()) or set()
            )
            return (
                len(ctx.items_received)
                if completed_locations or server_checked
                else 0
            )

        if state_key in state_data:
            cursor = min(
                state_data[state_key],
                len(ctx.items_received),
            )
            print(
                "Loaded ACWW delivery cursor:",
                cursor,
                "of",
                len(ctx.items_received),
            )
            return cursor

        # Migration safety for games played before delivery persistence
        # existed. If this save/server already has checks, assume the existing
        # received-item history was handled previously rather than replaying
        # the entire backlog into the inventory.
        server_checked = set(
            getattr(ctx, "checked_locations", set()) or set()
        )

        if completed_locations or server_checked:
            cursor = len(ctx.items_received)
            state_data[state_key] = cursor
            self._write_delivery_state_file(state_data)

            print(
                "Initialized ACWW delivery cursor at current history "
                f"({cursor}) to prevent reconnect redelivery."
            )
            return cursor

        # Brand-new seed/save: deliver received items from the beginning.
        state_data[state_key] = 0
        self._write_delivery_state_file(state_data)
        return 0

    def _save_delivery_cursor(
        self,
        ctx: "BizHawkClientContext",
        cursor: int,
    ) -> None:
        state_key = self._delivery_state_key(ctx)
        if state_key is None:
            return
        state_data = self._read_delivery_state_file()
        state_data[state_key] = max(0, cursor)
        self._write_delivery_state_file(state_data)

    TRAP_STATE_PATH = (
        Path.home()
        / ".archipelago"
        / "acww_trap_state.json"
    )

    def _read_trap_state_file(self) -> dict[str, dict[str, object]]:
        try:
            if not self.TRAP_STATE_PATH.exists():
                return {}

            raw = json.loads(
                self.TRAP_STATE_PATH.read_text(encoding="utf-8")
            )
            if not isinstance(raw, dict):
                return {}

            result: dict[str, dict[str, object]] = {}
            for key, value in raw.items():
                if isinstance(key, str) and isinstance(value, dict):
                    result[key] = dict(value)
            return result
        except (OSError, ValueError, TypeError):
            return {}

    def _write_trap_state_file(
        self,
        state_data: dict[str, dict[str, object]],
    ) -> None:
        self.TRAP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.TRAP_STATE_PATH.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(state_data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary_path.replace(self.TRAP_STATE_PATH)

    def _load_trap_runtime_state(
        self,
        ctx: "BizHawkClientContext",
    ) -> None:
        state_key = self._delivery_state_key(ctx)
        if state_key is None:
            if not getattr(self, "_trap_state_memory_only_initialized", False):
                self._pending_traps = []
                self._next_trap_allowed_time = 0.0
                self._trap_outside_since = None
                self._trap_state_memory_only_initialized = True
            return

        if getattr(self, "_trap_state_loaded_key", None) == state_key:
            return

        state_data = self._read_trap_state_file()
        entry = state_data.get(state_key, {})

        pending_raw = entry.get("pending_traps", [])
        if not isinstance(pending_raw, list):
            pending_raw = []

        self._pending_traps = [
            str(name)
            for name in pending_raw
            if str(name) in self.BEE_TRAP_SEQUENCE_VALUES
        ]

        next_allowed_wall_time = entry.get("next_allowed_wall_time", 0.0)
        try:
            remaining = max(
                0.0,
                float(next_allowed_wall_time) - time.time(),
            )
        except (TypeError, ValueError):
            remaining = 0.0

        self._next_trap_allowed_time = time.monotonic() + remaining
        self._trap_state_loaded_key = state_key

        if self._pending_traps:
            print(
                "Loaded pending ACWW traps:",
                ", ".join(self._pending_traps),
            )

    def _save_trap_runtime_state(
        self,
        ctx: "BizHawkClientContext",
    ) -> None:
        state_key = self._delivery_state_key(ctx)
        if state_key is None:
            return
        self._load_trap_runtime_state(ctx)
        state_data = self._read_trap_state_file()

        remaining = max(
            0.0,
            getattr(self, "_next_trap_allowed_time", 0.0)
            - time.monotonic(),
        )

        pending_traps = list(getattr(self, "_pending_traps", []))
        if not pending_traps and remaining <= 0.0:
            state_data.pop(state_key, None)
        else:
            state_data[state_key] = {
                "pending_traps": pending_traps,
                "next_allowed_wall_time": time.time() + remaining,
            }

        self._write_trap_state_file(state_data)

    def _clear_trap_runtime_state(
        self,
        ctx: "BizHawkClientContext",
    ) -> None:
        """Clear queued/cooldown trap state when a genuinely new town starts."""
        state_key = self._delivery_state_key(ctx)
        if state_key is not None:
            state_data = self._read_trap_state_file()
            if state_key in state_data:
                state_data.pop(state_key, None)
                self._write_trap_state_file(state_data)

        self._pending_traps = []
        self._next_trap_allowed_time = 0.0
        self._trap_outside_since = None
        self._trap_state_loaded_key = state_key
        self._trap_state_memory_only_initialized = True
        print("Cleared ACWW trap queue for new town.")

    def _queue_trap(
        self,
        ctx: "BizHawkClientContext",
        trap_name: str,
    ) -> None:
        self._load_trap_runtime_state(ctx)
        self._pending_traps.append(trap_name)
        self._save_trap_runtime_state(ctx)
        print(
            f"Queued ACWW trap: {trap_name} "
            f"({len(self._pending_traps)} pending)"
        )

    async def _process_pending_traps(
        self,
        ctx: "BizHawkClientContext",
        outside_state: int,
        now: float,
    ) -> None:
        self._load_trap_runtime_state(ctx)

        # 0 can appear during the tail end of a door transition. Require it to
        # remain continuously outside for a few seconds before consuming a trap.
        if outside_state != 0:
            self._trap_outside_since = None
            return

        outside_since = getattr(self, "_trap_outside_since", None)
        if outside_since is None:
            self._trap_outside_since = now
            return

        if now - outside_since < self.TRAP_OUTSIDE_STABLE_SECONDS:
            return

        if not self._pending_traps:
            return

        if now < getattr(self, "_next_trap_allowed_time", 0.0):
            return

        trap_name = self._pending_traps[0]
        sequence_value = self.BEE_TRAP_SEQUENCE_VALUES.get(trap_name)
        if sequence_value is None:
            print(f"Discarding unsupported queued ACWW trap: {trap_name}")
            self._pending_traps.pop(0)
            self._save_trap_runtime_state(ctx)
            return

        profile = self._require_rom_profile()

        # Do not overwrite an active bee/event sequence. This also ensures the
        # post-door transition has returned to the observed idle value (0x13).
        sequence_data = (
            await bizhawk.read(
                ctx.bizhawk_ctx,
                [(
                    profile.bee_sequence_address,
                    1,
                    self.memory.memory_domain,
                )],
            )
        )[0]

        if (
            not sequence_data
            or sequence_data[0] != self.BEE_IDLE_SEQUENCE_VALUE
        ):
            return

        # The event data must exist before the sequence byte advances. Sending
        # both writes in one BizHawk batch keeps them on the same watcher pass.
        await bizhawk.write(
            ctx.bizhawk_ctx,
            [
                (
                    profile.bee_attack_data_address,
                    self.BEE_ATTACK_DATA_VALUE.to_bytes(4, byteorder="little"),
                    self.memory.memory_domain,
                ),
                (
                    profile.bee_sequence_address,
                    bytes([sequence_value]),
                    self.memory.memory_domain,
                ),
            ],
        )

        self._pending_traps.pop(0)
        self._next_trap_allowed_time = now + self.TRAP_COOLDOWN_SECONDS
        self._save_trap_runtime_state(ctx)

        print(
            f"Fired ACWW trap: {trap_name}; "
            f"{len(self._pending_traps)} pending; "
            f"{self.TRAP_COOLDOWN_SECONDS:.0f}s grace period started."
        )

    def _inventory_contains_item(
        self,
        inventory_data: bytes,
        item_id: int,
    ) -> bool:
        """Return whether one inventory slot contains the given item ID."""
        for slot_index in range(self.memory.inventory_slot_count):
            offset = slot_index * self.memory.inventory_slot_size

            slot_item_id = int.from_bytes(
                inventory_data[offset:offset + 2],
                byteorder="little",
            )

            if slot_item_id == item_id:
                return True

        return False

    def _find_empty_inventory_slot(
        self,
        inventory_data: bytes,
    ) -> int | None:
        for slot_index in range(self.memory.inventory_slot_count):
            offset = slot_index * self.memory.inventory_slot_size

            item_id = int.from_bytes(
                inventory_data[offset:offset + 2],
                byteorder="little",
            )

            if item_id == self.memory.empty_inventory_item_id:
                return slot_index

        return None

    async def _clear_starting_vegetation(
        self,
        ctx: "BizHawkClientContext",
    ) -> int:
        """Remove vegetation from the outdoor town-object table once at startup."""
        table_size = self.memory.town_object_slot_count * 2
        town_data = bytearray(
            (
                await bizhawk.read(
                    ctx.bizhawk_ctx,
                    [(
                        self.memory.town_object_base_address,
                        table_size,
                        self.memory.memory_domain,
                    )],
                )
            )[0]
        )

        empty_bytes = self.memory.empty_town_object_id.to_bytes(
            2,
            byteorder="little",
        )
        removed_count = 0

        for slot_index in range(self.memory.town_object_slot_count):
            offset = slot_index * 2
            object_id = int.from_bytes(
                town_data[offset:offset + 2],
                byteorder="little",
            )

            if (
                0x0000 <= object_id <= 0x00A5
                or 0x00C7 <= object_id <= 0x00CF
            ):
                town_data[offset:offset + 2] = empty_bytes
                removed_count += 1

        if removed_count:
            await bizhawk.write(
                ctx.bizhawk_ctx,
                [(
                    self.memory.town_object_base_address,
                    bytes(town_data),
                    self.memory.memory_domain,
                )],
            )

        return removed_count

    async def _insta_grow_trees(
        self,
        ctx: "BizHawkClientContext",
    ) -> int:
        """Immediately mature non-money trees that are still growing."""
        table_size = self.memory.town_object_slot_count * 2
        town_data = (
            await bizhawk.read(
                ctx.bizhawk_ctx,
                [(
                    self.memory.town_object_base_address,
                    table_size,
                    self.memory.memory_domain,
                )],
            )
        )[0]

        writes: list[tuple[int, bytes, str]] = []

        for slot_index in range(self.memory.town_object_slot_count):
            offset = slot_index * 2
            object_id = int.from_bytes(
                town_data[offset:offset + 2],
                byteorder="little",
            )
            mature_id = self.TREE_GROWTH_TO_MATURE.get(object_id)
            if mature_id is None:
                continue

            writes.append((
                self.memory.town_object_base_address + offset,
                mature_id.to_bytes(2, byteorder="little"),
                self.memory.memory_domain,
            ))

        if not writes:
            return 0

        await bizhawk.write(ctx.bizhawk_ctx, writes)
        print(f"Instant-grew {len(writes)} ACWW tree(s).")
        return len(writes)

    async def _ensure_bee_tree(
        self,
        ctx: "BizHawkClientContext",
    ) -> bool:
        """Guarantee one renewable beehive whenever a mature tree exists.

        Natural hive trees are left alone. If no normal or cedar hive tree is
        present, the first eligible mature normal/cedar tree is converted to
        its matching hive variant. After the player shakes the hive down and
        the game restores the tree to its ordinary mature state, a later
        watcher pass can create another attempt.
        """
        table_size = self.memory.town_object_slot_count * 2
        town_data = (
            await bizhawk.read(
                ctx.bizhawk_ctx,
                [(
                    self.memory.town_object_base_address,
                    table_size,
                    self.memory.memory_domain,
                )],
            )
        )[0]

        eligible_slot: tuple[int, int] | None = None
        hive_ids = {
            self.NORMAL_TREE_WITH_BEEHIVE_OBJECT_ID,
            self.CEDAR_TREE_WITH_BEEHIVE_OBJECT_ID,
        }

        for slot_index in range(self.memory.town_object_slot_count):
            offset = slot_index * 2
            object_id = int.from_bytes(
                town_data[offset:offset + 2],
                byteorder="little",
            )

            if object_id in hive_ids:
                return False

            if eligible_slot is None:
                if object_id == self.NORMAL_TREE_OBJECT_ID:
                    eligible_slot = (
                        slot_index,
                        self.NORMAL_TREE_WITH_BEEHIVE_OBJECT_ID,
                    )
                elif object_id == self.CEDAR_TREE_OBJECT_ID:
                    eligible_slot = (
                        slot_index,
                        self.CEDAR_TREE_WITH_BEEHIVE_OBJECT_ID,
                    )

        if eligible_slot is None:
            return False

        slot_index, hive_object_id = eligible_slot
        slot_address = self.memory.town_object_base_address + slot_index * 2

        await bizhawk.write(
            ctx.bizhawk_ctx,
            [(
                slot_address,
                hive_object_id.to_bytes(2, byteorder="little"),
                self.memory.memory_domain,
            )],
        )

        print(
            "Guaranteed ACWW bee tree:",
            f"slot {slot_index}, object 0x{hive_object_id:04X}",
        )
        return True

    async def _ensure_starting_tools(
        self,
        ctx: "BizHawkClientContext",
        inventory_data: bytes,
    ) -> bool:
        """
        Insert any missing Start with Tools items into empty inventory slots.

        Returns True when at least one item was written. The watcher should end
        that pass afterward because inventory_data is only a snapshot from the
        start of the pass.
        """
        starting_tool_names = (
            "Shovel",
            "Fishing Rod",
            "Net",
        )

        inventory_item_ids = {
            int.from_bytes(
                inventory_data[offset:offset + 2],
                byteorder="little",
            )
            for offset in range(
                0,
                len(inventory_data),
                self.memory.inventory_slot_size,
            )
            if len(inventory_data[offset:offset + 2]) == 2
        }

        empty_slots = [
            slot_index
            for slot_index in range(self.memory.inventory_slot_count)
            if int.from_bytes(
                inventory_data[
                    slot_index * self.memory.inventory_slot_size:
                    (slot_index + 1) * self.memory.inventory_slot_size
                ],
                byteorder="little",
            ) == self.memory.empty_inventory_item_id
        ]

        writes: list[tuple[int, bytes, str]] = []
        delivered_names: list[str] = []

        for item_name in starting_tool_names:
            item_data = item_table.get(item_name)
            game_item_id = (
                item_data.get("game_id")
                if item_data
                else None
            )

            if game_item_id is None:
                continue

            game_item_id = int(game_item_id)

            if game_item_id in inventory_item_ids:
                continue

            if not empty_slots:
                break

            slot_index = empty_slots.pop(0)
            slot_address = (
                self.memory.inventory_base_address
                + slot_index * self.memory.inventory_slot_size
            )

            writes.append(
                (
                    slot_address,
                    game_item_id.to_bytes(2, byteorder="little"),
                    self.memory.memory_domain,
                )
            )
            inventory_item_ids.add(game_item_id)
            delivered_names.append(item_name)

        if not writes:
            return False

        await bizhawk.write(
            ctx.bizhawk_ctx,
            writes,
        )

        print(
            "Provided Start with Tools loadout:",
            ", ".join(delivered_names),
        )

        return True

    async def validate_rom(
        self,
        ctx: "BizHawkClientContext",
    ) -> bool:
        """Identify and activate the memory profile for the loaded ROM.

        Nintendo DS header:
            0x00-0x0B: internal title
            0x0C-0x0F: game code
            0x1E:      revision
        """
        try:
            header = (
                await bizhawk.read(
                    ctx.bizhawk_ctx,
                    [(0x00000000, 0x20, "ROM")],
                )
            )[0]
        except bizhawk.RequestFailedError:
            return False

        if len(header) < 0x20:
            return False

        internal_title = header[0x00:0x0C].rstrip(b"\x00 ")
        game_code = header[0x0C:0x10]
        revision = header[0x1E]

        profile = identify_rom_profile(
            internal_title,
            game_code,
            revision,
        )

        if profile is None:
            return False

        self.rom_profile = profile
        self._controller_state_sent_to_lua = None

        print(f"Detected ACWW ROM profile: {profile.display_name}")

        ctx.game = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True

        return True

    def _journal_flag_is_set(
        self,
        journal_data: bytes,
        global_index: int,
    ) -> bool:
        absolute_bit = (
            self.memory.journal_start_bit
            + global_index
        )

        byte_index = absolute_bit // 8
        bit_index = absolute_bit % 8

        return (
            journal_data[byte_index]
            & (1 << bit_index)
        ) != 0

    def _museum_nibble(
        self,
        museum_data: bytes,
        section_address: int,
        absolute_index: int,
    ) -> int:
        """
        Return the four-bit museum record for one entry.

        Every group of eight entries occupies four bytes:

            entry 0: bits 0-3
            entry 1: bits 4-7
            entry 2: bits 8-11
            ...
            entry 7: bits 28-31
        """
        group_index = absolute_index // 8
        position_in_group = absolute_index % 8

        group_address = section_address + (group_index * 4)
        relative_address = (
            group_address - self.memory.museum_base_address
        )

        group_value = int.from_bytes(
            museum_data[
                relative_address:relative_address + 4
            ],
            byteorder="little",
        )

        shift = position_in_group * 4

        return (group_value >> shift) & 0x0F

    def _museum_entry_is_donated(
        self,
        museum_data: bytes,
        section_address: int,
        absolute_index: int,
    ) -> bool:
        return self._museum_nibble(
            museum_data,
            section_address,
            absolute_index,
        ) != 0

    def _collect_journal_locations(
        self,
        journal_data: bytes,
    ) -> set[int]:
        completed_locations: set[int] = set()
        unique_bug_count = 0
        unique_fish_count = 0

        for bug_index in range(self.memory.bug_count):
            if self._journal_flag_is_set(
                journal_data,
                bug_index,
            ):
                unique_bug_count += 1

                completed_locations.add(
                    self.BUG_CATCH_BASE_ID + bug_index
                )

        for fish_index in range(self.memory.fish_count):
            global_index = self.memory.bug_count + fish_index

            if self._journal_flag_is_set(
                journal_data,
                global_index,
            ):
                unique_fish_count += 1

                completed_locations.add(
                    self.FISH_CATCH_BASE_ID + fish_index
                )

        for required_count, location_id in (
            self.BUG_JOURNAL_MILESTONE_LOCATIONS
        ):
            if unique_bug_count >= required_count:
                completed_locations.add(location_id)

        for required_count, location_id in (
            self.FISH_JOURNAL_MILESTONE_LOCATIONS
        ):
            if unique_fish_count >= required_count:
                completed_locations.add(location_id)

        return completed_locations

    def _collect_museum_locations(
        self,
        ctx: "BizHawkClientContext",
        museum_data: bytes,
    ) -> set[int]:
        completed_locations: set[int] = set()
        donated_bug_count = 0
        donated_fish_count = 0
        donated_fossil_count = 0
        donated_painting_count = 0

        for bug_index in range(self.memory.bug_count):
            if self._museum_entry_is_donated(
                museum_data,
                self.memory.bug_museum_address,
                bug_index,
            ):
                donated_bug_count += 1

                completed_locations.add(
                    self.BUG_MUSEUM_BASE_ID + bug_index
                )

        for fish_index in range(self.memory.fish_count):
            absolute_index = (
                self.memory.fish_museum_start_index
                + fish_index
            )

            if self._museum_entry_is_donated(
                museum_data,
                self.memory.fish_museum_address,
                absolute_index,
            ):
                donated_fish_count += 1

                completed_locations.add(
                    self.FISH_MUSEUM_BASE_ID + fish_index
                )

        donated_fossil_indexes: set[int] = set()

        for fossil_index in range(self.memory.fossil_count):
            if self._museum_entry_is_donated(
                museum_data,
                self.memory.fossil_museum_address,
                fossil_index,
            ):
                donated_fossil_count += 1
                donated_fossil_indexes.add(fossil_index)

                completed_locations.add(
                    self.FOSSIL_MUSEUM_BASE_ID
                    + fossil_index
                )

        for required_indexes, location_id in (
            self.FOSSIL_EXHIBIT_COMPLETION_LOCATIONS
        ):
            if all(
                fossil_index in donated_fossil_indexes
                for fossil_index in required_indexes
            ):
                completed_locations.add(location_id)

        for painting_index in range(
            self.memory.painting_count
        ):
            absolute_index = (
                self.memory.painting_museum_start_index
                + painting_index
            )

            if self._museum_entry_is_donated(
                museum_data,
                self.memory.painting_museum_address,
                absolute_index,
            ):
                donated_painting_count += 1

                completed_locations.add(
                    self.PAINTING_MUSEUM_BASE_ID
                    + painting_index
                )

        for required_count, location_id in (
            self.PAINTING_MILESTONE_LOCATIONS
        ):
            if donated_painting_count >= required_count:
                completed_locations.add(location_id)

        enabled_bug_museum = bool(
            ctx.slot_data.get("bug_museumsanity", True)
        ) if ctx.slot_data else True
        enabled_fish_museum = bool(
            ctx.slot_data.get("fish_museumsanity", True)
        ) if ctx.slot_data else True
        enabled_fossil_museum = bool(
            ctx.slot_data.get("fossil_museumsanity", True)
        ) if ctx.slot_data else True
        enabled_painting_museum = bool(
            ctx.slot_data.get("painting_museumsanity", False)
        ) if ctx.slot_data else False

        museum_current = (
            donated_bug_count if enabled_bug_museum else 0
        ) + (
            donated_fish_count if enabled_fish_museum else 0
        ) + (
            donated_fossil_count if enabled_fossil_museum else 0
        ) + (
            donated_painting_count if enabled_painting_museum else 0
        )

        museum_total = (
            self.memory.bug_count if enabled_bug_museum else 0
        ) + (
            self.memory.fish_count if enabled_fish_museum else 0
        ) + (
            self.memory.fossil_count if enabled_fossil_museum else 0
        ) + (
            self.memory.painting_count if enabled_painting_museum else 0
        )

        interval = int(
            ctx.slot_data.get("museum_percentage_milestones", 0)
        ) if ctx.slot_data else 0

        if museum_total > 0 and interval > 0:
            for percentage in range(interval, 101, interval):
                required_count = (
                    museum_total * percentage + 99
                ) // 100

                if museum_current >= required_count:
                    location_id = (
                        self.MUSEUM_PERCENTAGE_MILESTONE_BASE_ID
                        + (percentage // 5) - 1
                    )
                    completed_locations.add(location_id)

        return completed_locations

    @staticmethod
    def _ap_slot_is_ready(
        ctx: "BizHawkClientContext",
    ) -> bool:
        """
        Return True only after the AP server has authenticated a real slot.

        The generic BizHawk client may already have a server socket before
        the player enters the slot name. Sending LocationChecks during that
        intermediate state queues bogus RAM reads and flushes them after
        authentication. slot_data is only supplied by the server's Connected
        packet, so it is the safest readiness signal for this client.
        """
        server = getattr(ctx, "server", None)

        if server is None:
            return False

        socket = getattr(server, "socket", None)

        if socket is None or socket.closed:
            return False

        if getattr(ctx, "slot", None) is None:
            return False

        slot_data = getattr(ctx, "slot_data", None)

        return isinstance(slot_data, dict) and bool(slot_data)

    def _reset_slot_session_state(
        self,
        ctx: "BizHawkClientContext",
    ) -> None:
        """
        Reset only transient watcher state when a newly authenticated slot
        becomes active.

        Persistent delivery progress is still loaded from disk using the
        generated slot key, so reconnecting cannot redeliver old items.
        """
        slot_key = (
            str(getattr(ctx, "seed_name", None) or ""),
            int(getattr(ctx, "team", 0) or 0),
            int(getattr(ctx, "slot", 0) or 0),
            str(getattr(ctx, "auth", None) or ""),
        )

        if getattr(self, "_active_slot_key", None) == slot_key:
            return

        self._active_slot_key = slot_key

        transient_attributes = (
            "previous_completed_locations",
            "delivery_cursor",
            "_controller_state_sent_to_lua",
            "_previous_unlocked_months",
            "_previous_unlocked_claimables",
            "_previous_reclaimable_specimens",
            "_acww_goal_status_sent",
            "_last_inventory_snapshot",
            "_inventory_stable_since",
            "printed_starter_debug",
            "_previous_house_debt",
            "_last_bee_tree_check",
            "_pending_traps",
            "_next_trap_allowed_time",
            "_trap_state_loaded_key",
            "_trap_outside_since",
        )

        for attribute_name in transient_attributes:
            if hasattr(self, attribute_name):
                delattr(self, attribute_name)

    async def game_watcher(
        self,
        ctx: "BizHawkClientContext",
    ) -> None:
        # Do not read RAM, deliver items, update controllers, or send checks
        # until the AP server has accepted a slot and supplied slot data.
        #
        # This prevents pre-authentication car-ride/menu memory from being
        # queued as LocationChecks and then flushed after the slot name is
        # entered.
        if not self._ap_slot_is_ready(ctx):
            return

        self._reset_slot_session_state(ctx)

        try:
            (
                journal_data,
                museum_data,
                inventory_data,
                house_debt_data,
                outside_state_data,
            ) = await bizhawk.read(
                ctx.bizhawk_ctx,
                [
                    (
                        self.memory.journal_base_address,
                        self.memory.journal_read_size,
                        self.memory.memory_domain
                    ),
                    (
                        self.memory.museum_base_address,
                        self.memory.museum_read_size,
                        self.memory.memory_domain
                    ),
                    (
                        self.memory.inventory_base_address,
                        self.memory.inventory_slot_count
                        * self.memory.inventory_slot_size,
                        self.memory.memory_domain
                    ),
                    (
                        self.memory.house_debt_address,
                        2,
                        self.memory.memory_domain,
                    ),
                    (
                        self._require_rom_profile().outside_state_address,
                        1,
                        self.memory.memory_domain,
                    ),
                ],
            )

            outside_state = (
                outside_state_data[0]
                if outside_state_data
                else 0xFF
            )

            house_debt = int.from_bytes(
                house_debt_data,
                byteorder="little",
            )

            now = time.monotonic()
            previous_inventory_snapshot = getattr(
                self,
                "_last_inventory_snapshot",
                None,
            )

            if inventory_data != previous_inventory_snapshot:
                self._last_inventory_snapshot = inventory_data
                self._inventory_stable_since = now

            inventory_stable_since = getattr(
                self,
                "_inventory_stable_since",
                now,
            )
            inventory_is_stable = (
                now - inventory_stable_since
                >= self.INVENTORY_STABLE_SECONDS
            )

            previous_house_debt = getattr(
                self,
                "_previous_house_debt",
                None,
            )
            self._previous_house_debt = house_debt

            new_town_initialized = (
                previous_house_debt == 0
                and house_debt == self.memory.initial_house_debt
            )

            if new_town_initialized:
                self._clear_trap_runtime_state(ctx)
                print(
                    "Detected ACWW new-town initialization:",
                    f"0 -> {self.memory.initial_house_debt} Bells debt",
                )

                if bool(ctx.slot_data.get("skip_nook_tutorial", False)):
                    await bizhawk.write(
                        ctx.bizhawk_ctx,
                        [(
                            self.memory.nook_tutorial_flag_address,
                            bytes([0]),
                            self.memory.memory_domain,
                        )],
                    )
                    print("Skipped Tom Nook tutorial for new town.")

                if bool(ctx.slot_data.get("barren_town", False)):
                    removed_count = await self._clear_starting_vegetation(ctx)
                    print(
                        "Cleared starting vegetation for barren town:",
                        f"{removed_count} town objects removed.",
                    )

                if bool(ctx.slot_data.get("start_with_tools", False)):
                    starting_tools_written = (
                        await self._ensure_starting_tools(
                            ctx,
                            inventory_data,
                        )
                    )

                    if starting_tools_written:
                        # The inventory snapshot is now stale. Continue normal
                        # processing on the next watcher pass.
                        return

            last_bee_tree_check = getattr(
                self,
                "_last_bee_tree_check",
                0.0,
            )

            if (
                now - last_bee_tree_check
                >= self.BEE_TREE_CHECK_INTERVAL_SECONDS
            ):
                self._last_bee_tree_check = now
                await self._insta_grow_trees(ctx)
                await self._ensure_bee_tree(ctx)

            completed_locations = (
                self._collect_journal_locations(
                    journal_data
                )
                | self._collect_museum_locations(
                    ctx,
                    museum_data,
                )
            )

            if self._inventory_contains_item(
                inventory_data,
                self.FOUR_LEAF_CLOVER_ITEM_ID,
            ):
                completed_locations.add(
                    self.FOUR_LEAF_CLOVER_LOCATION_ID
                )

            # Only report locations that exist in this generated slot.
            enabled_locations = set(completed_locations)

            if ctx.slot_data:
                enabled_locations = set(
                    ctx.slot_data.get(
                        "enabled_locations",
                        completed_locations,
                    )
                )
                completed_locations &= enabled_locations

            _, goal_current, goal_required = self._get_goal_progress(
                ctx,
                completed_locations,
                enabled_locations,
            )

            goal_reached = (
                goal_required > 0
                and goal_current >= goal_required
            )

            if (
                goal_reached
                and not getattr(
                    self,
                    "_acww_goal_status_sent",
                    False,
                )
            ):
                await ctx.send_msgs([
                    {
                        "cmd": "StatusUpdate",
                        "status": ClientStatus.CLIENT_GOAL,
                    }
                ])

                self._acww_goal_status_sent = True
                ctx.finished_game = True

                print(
                    "ACWW goal status sent:",
                    f"{goal_current}/{goal_required}",
                )

            unlocked_months = self._get_unlocked_months(ctx)

            if unlocked_months != getattr(
                self,
                "_previous_unlocked_months",
                None,
            ):
                unlocked_names = [
                    MONTHS[month_number - 1]
                    for month_number in unlocked_months
                ]

                print(
                    "Unlocked ACWW months:",
                    ", ".join(unlocked_names),
                )

                self._previous_unlocked_months = unlocked_months

            unlocked_controls = self._get_unlocked_controller_controls(ctx)

            if unlocked_controls != getattr(
                self,
                "_previous_unlocked_controls",
                None,
            ):
                print(
                    "Unlocked ACWW Master Controller controls:",
                    ", ".join(unlocked_controls) or "None",
                )
                self._previous_unlocked_controls = list(unlocked_controls)

            unlocked_claimables = self._get_unlocked_claimables(ctx)

            if unlocked_claimables != getattr(
                self,
                "_previous_unlocked_claimables",
                None,
            ):
                print(
                    "Unlocked ACWW reclaimables:",
                    ", ".join(
                        str(claimable["name"])
                        for claimable in unlocked_claimables
                    ) or "None",
                )
                self._previous_unlocked_claimables = [
                    dict(claimable)
                    for claimable in unlocked_claimables
                ]

            reclaimable_specimens = self._get_reclaimable_specimens(
                ctx,
                inventory_data,
            )

            if reclaimable_specimens != getattr(
                self,
                "_previous_reclaimable_specimens",
                None,
            ):
                print(
                    "Recoverable ACWW specimens:",
                    ", ".join(
                        f'{entry["category"]}: {entry["name"]}'
                        for entry in reclaimable_specimens
                    ) or "None",
                )
                self._previous_reclaimable_specimens = [
                    dict(entry)
                    for entry in reclaimable_specimens
                ]

            restore_payload = self._get_restore_progress_payload(
                ctx
            )

            await self._update_controller_state(
                ctx,
                unlocked_months,
                unlocked_controls,
                unlocked_claimables,
                reclaimable_specimens,
                restore_payload,
            )

            if not hasattr(self, "delivery_cursor"):
                self.delivery_cursor = self._load_delivery_cursor(
                    ctx,
                    completed_locations,
                )

            self._load_trap_runtime_state(ctx)

            # Process received items in strict order. A physical item is only
            # acknowledged after it is successfully written to inventory.
            # Virtual unlocks are acknowledged immediately.
            while self.delivery_cursor < len(ctx.items_received):
                network_item = ctx.items_received[
                    self.delivery_cursor
                ]

                item_data = received_item_data_by_ap_id.get(
                    network_item.item
                )

                if item_data is None:
                    print(
                        "Unknown ACWW AP item ID:",
                        network_item.item,
                    )
                    self.delivery_cursor += 1
                    self._save_delivery_cursor(
                        ctx,
                        self.delivery_cursor,
                    )
                    continue

                item_name = str(item_data["name"])
                game_item_id = item_data.get("game_id")
                item_category = item_data.get("category")

                if item_category == "starting_tool":
                    print(
                        f"Starting loadout item already handled: {item_name}"
                    )
                    self.delivery_cursor += 1
                    self._save_delivery_cursor(
                        ctx,
                        self.delivery_cursor,
                    )
                    continue

                if item_category == "trap":
                    self._queue_trap(ctx, item_name)
                    self.delivery_cursor += 1
                    self._save_delivery_cursor(
                        ctx,
                        self.delivery_cursor,
                    )

                    await self._show_received_item_notification(
                        ctx,
                        network_item,
                        item_name,
                        delivered_to_inventory=False,
                        detail_line_override="Trap queued",
                    )
                    continue

                if game_item_id is None:
                    print(
                        f"Received non-inventory unlock: {item_name} "
                        f"(category={item_category})"
                    )
                    self.delivery_cursor += 1
                    self._save_delivery_cursor(
                        ctx,
                        self.delivery_cursor,
                    )

                    await self._show_received_item_notification(
                        ctx,
                        network_item,
                        item_name,
                        delivered_to_inventory=False,
                    )
                    continue

                if not inventory_is_stable:
                    # The game may be in the middle of catching, picking up,
                    # dropping, selling, or otherwise changing inventory.
                    # Keep the delivery cursor on this physical item and retry
                    # only after the inventory has remained unchanged for two
                    # full seconds.
                    break

                empty_slot = self._find_empty_inventory_slot(
                    inventory_data
                )

                if empty_slot is None:
                    # Leave the cursor on this item so it is retried after the
                    # player frees an inventory slot or reconnects.
                    break

                slot_address = (
                    self.memory.inventory_base_address
                    + empty_slot * self.memory.inventory_slot_size
                )

                await bizhawk.write(
                    ctx.bizhawk_ctx,
                    [
                        (
                            slot_address,
                            int(game_item_id).to_bytes(
                                2,
                                byteorder="little",
                            ),
                            self.memory.memory_domain,
                        )
                    ],
                )

                self.delivery_cursor += 1
                self._save_delivery_cursor(
                    ctx,
                    self.delivery_cursor,
                )

                print(
                    f"Delivered received item: {item_name} "
                    f"to slot {empty_slot + 1}"
                )

                await self._show_received_item_notification(
                    ctx,
                    network_item,
                    item_name,
                    delivered_to_inventory=True,
                )

                # inventory_data is the snapshot from the beginning of this
                # watcher pass. Deliver at most one physical item per pass.
                break

            await self._process_pending_traps(
                ctx,
                outside_state,
                now,
            )

            if not hasattr(
                self,
                "previous_completed_locations",
            ):
                # Treat the current save state as the baseline when first
                # connecting, so reconnecting does not replay every old check.
                self.previous_completed_locations = set(
                    completed_locations
                )
                new_locations: set[int] = set()
            else:
                new_locations = (
                    completed_locations
                    - self.previous_completed_locations
                )

            if new_locations:
                print(
                    "New ACWW locations:",
                    sorted(new_locations),
                )

                for location_id in sorted(new_locations):
                    await self._show_check_notification(
                        ctx,
                        location_id,
                    )

            # When connected to a generated ACWW slot, compare RAM
            # against the locations the AP server already knows.
            server_missing_locations = (
                completed_locations
                - ctx.checked_locations
            )

            if (
                server_missing_locations
                and self._ap_slot_is_ready(ctx)
            ):
                await ctx.send_msgs([
                    {
                        "cmd": "LocationChecks",
                        "locations": sorted(
                            server_missing_locations
                        ),
                    }
                ])

            await self._update_progress_overlay(
                ctx,
                completed_locations,
                enabled_locations,
            )

            self.previous_completed_locations = (
                completed_locations
            )

        except bizhawk.RequestFailedError:
            return