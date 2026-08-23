from __future__ import annotations

from dataclasses import asdict, dataclass


MAIN_RAM_BUS_OFFSET = 0x02000000


@dataclass(frozen=True)
class MemoryProfile:
    """Version-specific ACWW memory layout.

    Python/BizHawk reads use Main RAM offsets. The Lua connector uses ARM
    system-bus addresses, exposed through ``to_lua_payload``.
    """

    memory_domain: str

    inventory_base_address: int
    inventory_slot_count: int
    inventory_slot_size: int
    empty_inventory_item_id: int

    journal_base_address: int
    journal_read_size: int
    journal_start_bit: int

    museum_base_address: int
    museum_read_size: int
    fossil_museum_address: int
    fish_museum_address: int
    bug_museum_address: int
    painting_museum_address: int
    fish_museum_start_index: int
    painting_museum_start_index: int

    house_debt_address: int
    initial_house_debt: int
    post_tutorial_house_debt: int
    nook_tutorial_flag_address: int

    bug_count: int
    fish_count: int
    fossil_count: int
    painting_count: int

    clock_offset_bus_address: int
    time_struct_bus_address: int

    weather_current_bus_address: int
    weather_target_bus_address: int
    weather_precipitation_bus_address: int

    town_object_bus_address: int
    town_object_slot_count: int
    first_weed_object_id: int
    last_weed_object_id: int
    empty_town_object_id: int

    @property
    def town_object_base_address(self) -> int:
        """Return the outdoor town-object table as a Main RAM offset."""
        return self.town_object_bus_address - MAIN_RAM_BUS_OFFSET

    def to_lua_payload(self) -> dict[str, int]:
        """Return the fields used directly by the Lua Master Controller."""
        return {
            "clock_offset_address": self.clock_offset_bus_address,
            "time_struct_address": self.time_struct_bus_address,
            "weather_current_address": self.weather_current_bus_address,
            "weather_target_address": self.weather_target_bus_address,
            "weather_precipitation_address": (
                self.weather_precipitation_bus_address
            ),
            "inventory_base_address": (
                self.inventory_base_address + MAIN_RAM_BUS_OFFSET
            ),
            "inventory_slot_count": self.inventory_slot_count,
            "inventory_slot_size": self.inventory_slot_size,
            "empty_inventory_item_id": self.empty_inventory_item_id,
            "town_object_base_address": self.town_object_bus_address,
            "town_object_slot_count": self.town_object_slot_count,
            "first_weed_object_id": self.first_weed_object_id,
            "last_weed_object_id": self.last_weed_object_id,
            "empty_town_object_id": self.empty_town_object_id,
            "journal_base_address": (
                self.journal_base_address + MAIN_RAM_BUS_OFFSET
            ),
            "journal_start_bit": self.journal_start_bit,
            "bug_count": self.bug_count,
            "fossil_museum_address": (
                self.fossil_museum_address + MAIN_RAM_BUS_OFFSET
            ),
            "fish_museum_address": (
                self.fish_museum_address + MAIN_RAM_BUS_OFFSET
            ),
            "bug_museum_address": (
                self.bug_museum_address + MAIN_RAM_BUS_OFFSET
            ),
            "painting_museum_address": (
                self.painting_museum_address + MAIN_RAM_BUS_OFFSET
            ),
            "fish_museum_start_index": self.fish_museum_start_index,
            "painting_museum_start_index": (
                self.painting_museum_start_index
            ),
        }


USA_REV_1_MEMORY = MemoryProfile(
    memory_domain="Main RAM",

    inventory_base_address=0x1D8E7E,
    inventory_slot_count=15,
    inventory_slot_size=2,
    empty_inventory_item_id=0xFFF1,

    journal_base_address=0x1D8F39,
    journal_read_size=15,
    journal_start_bit=1,

    museum_base_address=0x1ED0A0,
    museum_read_size=0x60,
    fossil_museum_address=0x1ED0A0,
    fish_museum_address=0x1ED0B8,
    bug_museum_address=0x1ED0D8,
    painting_museum_address=0x1ED0F4,
    fish_museum_start_index=6,
    painting_museum_start_index=2,

    house_debt_address=0x1E6E38,
    initial_house_debt=19800,
    post_tutorial_house_debt=18400,
    nook_tutorial_flag_address=0x1ED3BC,

    bug_count=56,
    fish_count=56,
    fossil_count=52,
    painting_count=20,

    clock_offset_bus_address=0x021ED304,
    time_struct_bus_address=0x021D72EC,

    # Runtime outdoor weather manager (verified on USA Rev 1).
    weather_current_bus_address=0x021F146C,
    weather_target_bus_address=0x021F1470,
    weather_precipitation_bus_address=0x021F147C,

    town_object_bus_address=0x021E36A4,
    town_object_slot_count=0x1000,
    first_weed_object_id=0x001C,
    last_weed_object_id=0x0025,
    empty_town_object_id=0xFFF1,
)
