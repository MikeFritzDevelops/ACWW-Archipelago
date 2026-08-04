from __future__ import annotations
from . import memory_map

from typing import TYPE_CHECKING

import json
import time
from pathlib import Path

import worlds._bizhawk as bizhawk
from NetUtils import ClientStatus
from worlds._bizhawk.client import BizHawkClient
from .items import (
    MONTHS,
    PROGRESSIVE_TOOL_STAGES,
    item_table,
    received_item_data_by_ap_id,
)
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

    # Tutorial Finish Check
    HOUSE_DEBT_ADDRESS = memory_map.HOUSE_DEBT_ADDRESS
    POST_TUTORIAL_DEBT = memory_map.POST_TUTORIAL_HOUSE_DEBT

    STARTER_LOCATION_IDS = {
        2400,
        2401,
        2402,
    }

    BUG_COUNT = memory_map.BUG_COUNT
    FISH_COUNT = memory_map.FISH_COUNT
    FOSSIL_COUNT = memory_map.FOSSIL_COUNT
    PAINTING_COUNT = memory_map.PAINTING_COUNT

    JOURNAL_BASE_ADDRESS = memory_map.JOURNAL_BASE_ADDRESS
    JOURNAL_READ_SIZE = memory_map.JOURNAL_READ_SIZE
    JOURNAL_START_BIT = memory_map.JOURNAL_START_BIT

    MUSEUM_BASE_ADDRESS = memory_map.MUSEUM_BASE_ADDRESS
    MUSEUM_READ_SIZE = memory_map.MUSEUM_READ_SIZE

    FOSSIL_MUSEUM_ADDRESS = memory_map.FOSSIL_MUSEUM_ADDRESS
    FISH_MUSEUM_ADDRESS = memory_map.FISH_MUSEUM_ADDRESS
    BUG_MUSEUM_ADDRESS = memory_map.BUG_MUSEUM_ADDRESS
    PAINTING_MUSEUM_ADDRESS = memory_map.PAINTING_MUSEUM_ADDRESS

    FISH_MUSEUM_START_INDEX = memory_map.FISH_MUSEUM_START_INDEX
    PAINTING_MUSEUM_START_INDEX = memory_map.PAINTING_MUSEUM_START_INDEX

    INVENTORY_BASE_ADDRESS = memory_map.INVENTORY_BASE_ADDRESS
    INVENTORY_SLOT_COUNT = memory_map.INVENTORY_SLOT_COUNT
    INVENTORY_SLOT_SIZE = memory_map.INVENTORY_SLOT_SIZE
    EMPTY_INVENTORY_ITEM = memory_map.EMPTY_INVENTORY_ITEM_ID


    OVERLAY_UPDATE_INTERVAL_SECONDS = 1.0

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
            self.BUG_COUNT,
        )
        fish_museum = self._count_range(
            completed_locations,
            self.FISH_MUSEUM_BASE_ID,
            self.FISH_COUNT,
        )
        fossil_museum = self._count_range(
            completed_locations,
            self.FOSSIL_MUSEUM_BASE_ID,
            self.FOSSIL_COUNT,
        )
        painting_museum = self._count_range(
            completed_locations,
            self.PAINTING_MUSEUM_BASE_ID,
            self.PAINTING_COUNT,
        )

        enabled_bug_museum = self._count_range(
            enabled_locations,
            self.BUG_MUSEUM_BASE_ID,
            self.BUG_COUNT,
        )
        enabled_fish_museum = self._count_range(
            enabled_locations,
            self.FISH_MUSEUM_BASE_ID,
            self.FISH_COUNT,
        )
        enabled_fossil_museum = self._count_range(
            enabled_locations,
            self.FOSSIL_MUSEUM_BASE_ID,
            self.FOSSIL_COUNT,
        )
        enabled_painting_museum = self._count_range(
            enabled_locations,
            self.PAINTING_MUSEUM_BASE_ID,
            self.PAINTING_COUNT,
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
                enabled_bug_museum or self.BUG_COUNT,
            )

        if goal_key == "all_fish":
            return (
                "All Fish",
                fish_museum,
                enabled_fish_museum or self.FISH_COUNT,
            )

        if goal_key == "all_fossils":
            return (
                "All Fossils",
                fossil_museum,
                enabled_fossil_museum or self.FOSSIL_COUNT,
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
            self.BUG_COUNT,
        )
        fish_catches = self._count_range(
            completed_locations,
            self.FISH_CATCH_BASE_ID,
            self.FISH_COUNT,
        )
        bug_museum = self._count_range(
            completed_locations,
            self.BUG_MUSEUM_BASE_ID,
            self.BUG_COUNT,
        )
        fish_museum = self._count_range(
            completed_locations,
            self.FISH_MUSEUM_BASE_ID,
            self.FISH_COUNT,
        )
        fossil_museum = self._count_range(
            completed_locations,
            self.FOSSIL_MUSEUM_BASE_ID,
            self.FOSSIL_COUNT,
        )
        painting_museum = self._count_range(
            completed_locations,
            self.PAINTING_MUSEUM_BASE_ID,
            self.PAINTING_COUNT,
        )

        enabled_bug_catches = self._count_range(
            enabled_locations,
            self.BUG_CATCH_BASE_ID,
            self.BUG_COUNT,
        )
        enabled_fish_catches = self._count_range(
            enabled_locations,
            self.FISH_CATCH_BASE_ID,
            self.FISH_COUNT,
        )
        enabled_bug_museum = self._count_range(
            enabled_locations,
            self.BUG_MUSEUM_BASE_ID,
            self.BUG_COUNT,
        )
        enabled_fish_museum = self._count_range(
            enabled_locations,
            self.FISH_MUSEUM_BASE_ID,
            self.FISH_COUNT,
        )
        enabled_fossil_museum = self._count_range(
            enabled_locations,
            self.FOSSIL_MUSEUM_BASE_ID,
            self.FOSSIL_COUNT,
        )
        enabled_painting_museum = self._count_range(
            enabled_locations,
            self.PAINTING_MUSEUM_BASE_ID,
            self.PAINTING_COUNT,
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
    ) -> None:
        sender_name = self._player_name(
            ctx,
            network_item.player,
        )

        if delivered_to_inventory:
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

    def _get_unlocked_claimables(
        self,
        ctx: "BizHawkClientContext",
    ) -> list[dict[str, int | str]]:
        """
        Return permanently reclaimable physical resources received from AP.

        Fruit and environment items are treated as permanent unlocks. Once
        received, the Lua master controller may create replacement copies in
        empty inventory slots whenever the player needs them.
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
                self.INVENTORY_SLOT_SIZE,
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
                self.BUG_COUNT,
            ),
            "fish": checked_indexes(
                self.FISH_CATCH_BASE_ID,
                self.FISH_COUNT,
            ),
            "museum_bugs": checked_indexes(
                self.BUG_MUSEUM_BASE_ID,
                self.BUG_COUNT,
            ),
            "museum_fish": checked_indexes(
                self.FISH_MUSEUM_BASE_ID,
                self.FISH_COUNT,
            ),
            "museum_fossils": checked_indexes(
                self.FOSSIL_MUSEUM_BASE_ID,
                self.FOSSIL_COUNT,
            ),
            "museum_paintings": checked_indexes(
                self.PAINTING_MUSEUM_BASE_ID,
                self.PAINTING_COUNT,
            ),
        }

    async def _update_controller_state(
        self,
        ctx: "BizHawkClientContext",
        unlocked_months: list[int],
        claimables: list[dict[str, int | str]],
        reclaimable_specimens: list[dict[str, int | str]],
        restore_payload: dict[str, list[int]],
    ) -> None:
        controller_state = {
            "unlocked_months": list(unlocked_months),
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

        if controller_state == getattr(
            self,
            "_controller_state_sent_to_lua",
            None,
        ):
            return

        responses = await bizhawk.send_requests(
            ctx.bizhawk_ctx,
            [
                {
                    "type": "SET_ACWW_STATE",
                    "state": controller_state,
                }
            ],
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

    DELIVERY_STATE_PATH = (
        Path.home()
        / ".archipelago"
        / "acww_delivery_state.json"
    )

    def _delivery_state_key(
        self,
        ctx: "BizHawkClientContext",
    ) -> str:
        """
        Build a stable key for this generated slot.

        seed_name distinguishes different generated games; team/slot keeps
        multiplayer slots separate. Fallbacks keep this compatible with
        slightly different BizHawk context versions.
        """
        seed_name = str(
            getattr(ctx, "seed_name", None)
            or getattr(ctx, "seed", None)
            or "unknown-seed"
        )
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
        state_data = self._read_delivery_state_file()
        state_data[state_key] = max(0, cursor)
        self._write_delivery_state_file(state_data)

    @classmethod
    def _inventory_contains_item(
        cls,
        inventory_data: bytes,
        item_id: int,
    ) -> bool:
        """Return whether one inventory slot contains the given item ID."""
        for slot_index in range(cls.INVENTORY_SLOT_COUNT):
            offset = slot_index * cls.INVENTORY_SLOT_SIZE

            slot_item_id = int.from_bytes(
                inventory_data[offset:offset + 2],
                byteorder="little",
            )

            if slot_item_id == item_id:
                return True

        return False

    @classmethod
    def _find_empty_inventory_slot(
        cls,
        inventory_data: bytes,
    ) -> int | None:
        for slot_index in range(cls.INVENTORY_SLOT_COUNT):
            offset = slot_index * cls.INVENTORY_SLOT_SIZE

            item_id = int.from_bytes(
                inventory_data[offset:offset + 2],
                byteorder="little",
            )

            if item_id == cls.EMPTY_INVENTORY_ITEM:
                return slot_index

        return None

    async def validate_rom(
        self,
        ctx: "BizHawkClientContext",
    ) -> bool:
        """
        Accept only Animal Crossing: Wild World USA Rev 1.

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

        if game_code != b"ADME":
            return False

        if revision != 1:
            return False

        # Optional extra protection. We primarily trust the unique game code.
        if not internal_title.startswith(b"ANIMAL"):
            return False

        ctx.game = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True

        return True

    @staticmethod
    def _journal_flag_is_set(
        journal_data: bytes,
        global_index: int,
    ) -> bool:
        absolute_bit = (
            AnimalCrossingWildWorldClient.JOURNAL_START_BIT
            + global_index
        )

        byte_index = absolute_bit // 8
        bit_index = absolute_bit % 8

        return (
            journal_data[byte_index]
            & (1 << bit_index)
        ) != 0

    @classmethod
    def _museum_nibble(
        cls,
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
            group_address - cls.MUSEUM_BASE_ADDRESS
        )

        group_value = int.from_bytes(
            museum_data[
                relative_address:relative_address + 4
            ],
            byteorder="little",
        )

        shift = position_in_group * 4

        return (group_value >> shift) & 0x0F

    @classmethod
    def _museum_entry_is_donated(
        cls,
        museum_data: bytes,
        section_address: int,
        absolute_index: int,
    ) -> bool:
        return cls._museum_nibble(
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

        for bug_index in range(self.BUG_COUNT):
            if self._journal_flag_is_set(
                journal_data,
                bug_index,
            ):
                unique_bug_count += 1

                completed_locations.add(
                    self.BUG_CATCH_BASE_ID + bug_index
                )

        for fish_index in range(self.FISH_COUNT):
            global_index = self.BUG_COUNT + fish_index

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

        for bug_index in range(self.BUG_COUNT):
            if self._museum_entry_is_donated(
                museum_data,
                self.BUG_MUSEUM_ADDRESS,
                bug_index,
            ):
                donated_bug_count += 1

                completed_locations.add(
                    self.BUG_MUSEUM_BASE_ID + bug_index
                )

        for fish_index in range(self.FISH_COUNT):
            absolute_index = (
                self.FISH_MUSEUM_START_INDEX
                + fish_index
            )

            if self._museum_entry_is_donated(
                museum_data,
                self.FISH_MUSEUM_ADDRESS,
                absolute_index,
            ):
                donated_fish_count += 1

                completed_locations.add(
                    self.FISH_MUSEUM_BASE_ID + fish_index
                )

        donated_fossil_indexes: set[int] = set()

        for fossil_index in range(self.FOSSIL_COUNT):
            if self._museum_entry_is_donated(
                museum_data,
                self.FOSSIL_MUSEUM_ADDRESS,
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
            self.PAINTING_COUNT
        ):
            absolute_index = (
                self.PAINTING_MUSEUM_START_INDEX
                + painting_index
            )

            if self._museum_entry_is_donated(
                museum_data,
                self.PAINTING_MUSEUM_ADDRESS,
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
            self.BUG_COUNT if enabled_bug_museum else 0
        ) + (
            self.FISH_COUNT if enabled_fish_museum else 0
        ) + (
            self.FOSSIL_COUNT if enabled_fossil_museum else 0
        ) + (
            self.PAINTING_COUNT if enabled_painting_museum else 0
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
            "printed_starter_debug",
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
            journal_data, museum_data, inventory_data, debt_data = await bizhawk.read(
                ctx.bizhawk_ctx,
                [
                    (
                        self.JOURNAL_BASE_ADDRESS,
                        self.JOURNAL_READ_SIZE,
                        memory_map.MEMORY_DOMAIN
                    ),
                    (
                        self.MUSEUM_BASE_ADDRESS,
                        self.MUSEUM_READ_SIZE,
                        memory_map.MEMORY_DOMAIN
                    ),
                    (
                        self.INVENTORY_BASE_ADDRESS,
                        self.INVENTORY_SLOT_COUNT
                        * self.INVENTORY_SLOT_SIZE,
                        memory_map.MEMORY_DOMAIN
                    ),
                    (
                        self.HOUSE_DEBT_ADDRESS,
                        2,
                        memory_map.MEMORY_DOMAIN
                    ),
                ],
            )

            completed_locations = (
                self._collect_journal_locations(
                    journal_data
                )
                | self._collect_museum_locations(
                    ctx,
                    museum_data,
                )
            )

            current_debt = int.from_bytes(
                debt_data,
                byteorder="little",
            )

            if not hasattr(self, "printed_starter_debug"):
                self.printed_starter_debug = True
                print("Current debt:", current_debt)
                print("Slot data:", ctx.slot_data)
                print(
                    "Starter IDs enabled:",
                    self.STARTER_LOCATION_IDS.issubset(
                        set(
                            ctx.slot_data.get(
                                "enabled_locations",
                                [],
                            )
                        )
                    )
                    if ctx.slot_data
                    else False
                )

            starter_kit_enabled = bool(
                ctx.slot_data
                and ctx.slot_data.get("starter_kit", False)
            )

            if (
                starter_kit_enabled
                and current_debt <= self.POST_TUTORIAL_DEBT
            ):
                completed_locations.update(
                    self.STARTER_LOCATION_IDS
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
                unlocked_claimables,
                reclaimable_specimens,
                restore_payload,
            )

            if not hasattr(self, "delivery_cursor"):
                self.delivery_cursor = self._load_delivery_cursor(
                    ctx,
                    completed_locations,
                )

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

                # Progressive Shovel/Rod/Net each have two received stages:
                # copy 1 = normal tool, copy 2+ = golden tool.
                #
                # Count directly from the server's received-item history rather
                # than a transient local counter. This remains correct after
                # reconnects and when the persisted delivery cursor resumes in
                # the middle of the item list.
                if (
                    item_category == "progressive_tool"
                    and item_name in PROGRESSIVE_TOOL_STAGES
                ):
                    received_stage_count = sum(
                        1
                        for prior_item in ctx.items_received[
                            : self.delivery_cursor + 1
                        ]
                        if prior_item.item == network_item.item
                    )

                    stages = PROGRESSIVE_TOOL_STAGES[item_name]
                    stage_index = min(
                        received_stage_count - 1,
                        len(stages) - 1,
                    )
                    game_item_id = stages[stage_index]

                    print(
                        f"Resolved {item_name} stage "
                        f"{received_stage_count} to game item "
                        f"0x{game_item_id:04X}"
                    )

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

                empty_slot = self._find_empty_inventory_slot(
                    inventory_data
                )

                if empty_slot is None:
                    # Leave the cursor on this item so it is retried after the
                    # player frees an inventory slot or reconnects.
                    break

                slot_address = (
                    self.INVENTORY_BASE_ADDRESS
                    + empty_slot * self.INVENTORY_SLOT_SIZE
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
                            memory_map.MEMORY_DOMAIN,
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