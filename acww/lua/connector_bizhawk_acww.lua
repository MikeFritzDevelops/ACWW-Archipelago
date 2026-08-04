--[[
Copyright (c) 2023 Zunawe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
]]

-- Animal Crossing: Wild World Archipelago connector
local SCRIPT_VERSION = 1

-- Set to log incoming requests
-- Will cause lag due to large console output
local DEBUG = false

--[[
This script expects to receive JSON and will send JSON back. A message should
be a list of 1 or more requests which will be executed in order. Each request
will have a corresponding response in the same order.

Every individual request and response is a JSON object with at minimum one
field `type`. The value of `type` determines what other fields may exist.

To get the script version, instead of JSON, send "VERSION" to get the script
version directly (e.g. "2").

#### Ex. 1

Request: `[{"type": "PING"}]`

Response: `[{"type": "PONG"}]`

---

#### Ex. 2

Request: `[{"type": "LOCK"}, {"type": "HASH"}]`

Response: `[{"type": "LOCKED"}, {"type": "HASH_RESPONSE", "value": "F7D18982"}]`

---

#### Ex. 3

Request:

```json
[
    {"type": "GUARD", "address": 100, "expected_data": "aGVsbG8=", "domain": "System Bus"},
    {"type": "READ", "address": 500, "size": 4, "domain": "ROM"}
]
```

Response:

```json
[
    {"type": "GUARD_RESPONSE", "address": 100, "value": true},
    {"type": "READ_RESPONSE", "value": "dGVzdA=="}
]
```

---

#### Ex. 4

Request:

```json
[
    {"type": "GUARD", "address": 100, "expected_data": "aGVsbG8=", "domain": "System Bus"},
    {"type": "READ", "address": 500, "size": 4, "domain": "ROM"}
]
```

Response:

```json
[
    {"type": "GUARD_RESPONSE", "address": 100, "value": false},
    {"type": "GUARD_RESPONSE", "address": 100, "value": false}
]
```

---

### Supported Request Types

- `PING`  
    Does nothing; resets timeout.

    Expected Response Type: `PONG`

- `SYSTEM`  
    Returns the system of the currently loaded ROM (N64, GBA, etc...).

    Expected Response Type: `SYSTEM_RESPONSE`

- `PREFERRED_CORES`  
    Returns the user's default cores for systems with multiple cores. If the
    current ROM's system has multiple cores, the one that is currently
    running is very probably the preferred core.

    Expected Response Type: `PREFERRED_CORES_RESPONSE`

- `HASH`  
    Returns the hash of the currently loaded ROM calculated by BizHawk.

    Expected Response Type: `HASH_RESPONSE`

- `MEMORY_SIZE`  
    Returns the size in bytes of the specified memory domain.

    Expected Response Type: `MEMORY_SIZE_RESPONSE`

    Additional Fields:
    - `domain` (`string`): The name of the memory domain to check

- `GUARD`  
    Checks a section of memory against `expected_data`. If the bytes starting
    at `address` do not match `expected_data`, the response will have `value`
    set to `false`, and all subsequent requests will not be executed and
    receive the same `GUARD_RESPONSE`.

    Expected Response Type: `GUARD_RESPONSE`

    Additional Fields:
    - `address` (`int`): The address of the memory to check
    - `expected_data` (string): A base64 string of contiguous data
    - `domain` (`string`): The name of the memory domain the address
    corresponds to

- `LOCK`  
    Halts emulation and blocks on incoming requests until an `UNLOCK` request
    is received or the client times out. All requests processed while locked
    will happen on the same frame.

    Expected Response Type: `LOCKED`

- `UNLOCK`  
    Resumes emulation after the current list of requests is done being
    executed.

    Expected Response Type: `UNLOCKED`

- `READ`  
    Reads an array of bytes at the provided address.

    Expected Response Type: `READ_RESPONSE`

    Additional Fields:
    - `address` (`int`): The address of the memory to read
    - `size` (`int`): The number of bytes to read
    - `domain` (`string`): The name of the memory domain the address
    corresponds to

- `WRITE`  
    Writes an array of bytes to the provided address.

    Expected Response Type: `WRITE_RESPONSE`

    Additional Fields:
    - `address` (`int`): The address of the memory to write to
    - `value` (`string`): A base64 string representing the data to write
    - `domain` (`string`): The name of the memory domain the address
    corresponds to

- `DISPLAY_MESSAGE`  
    Adds a message to the message queue which will be displayed using
    `gui.addmessage` according to the message interval.

    Expected Response Type: `DISPLAY_MESSAGE_RESPONSE`

    Additional Fields:
    - `message` (`string`): The string to display

- `SET_MESSAGE_INTERVAL`  
    Sets the minimum amount of time to wait between displaying messages.
    Potentially useful if you add many messages quickly but want players
    to be able to read each of them.

    Expected Response Type: `SET_MESSAGE_INTERVAL_RESPONSE`

    Additional Fields:
    - `value` (`number`): The number of seconds to set the interval to


### Response Types

- `PONG`  
    Acknowledges `PING`.

- `SYSTEM_RESPONSE`  
    Contains the name of the system for currently running ROM.

    Additional Fields:
    - `value` (`string`): The returned system name

- `PREFERRED_CORES_RESPONSE`  
    Contains the user's preferred cores for systems with multiple supported
    cores. Currently includes NES, SNES, GB, GBC, DGB, SGB, PCE, PCECD, and
    SGX.

    Additional Fields:
    - `value` (`{[string]: [string]}`): A dictionary map from system name to
    core name

- `HASH_RESPONSE`  
    Contains the hash of the currently loaded ROM calculated by BizHawk.

    Additional Fields:
    - `value` (`string`): The returned hash

- `MEMORY_SIZE_RESPONSE`  
    Contains the size in bytes of the specified memory domain.

    Additional Fields:
    - `value` (`number`): The size of the domain in bytes

- `GUARD_RESPONSE`  
    The result of an attempted `GUARD` request.

    Additional Fields:
    - `value` (`boolean`): true if the memory was validated, false if not
    - `address` (`int`): The address of the memory that was invalid (the same
    address provided by the `GUARD`, not the address of the individual invalid
    byte)

- `LOCKED`  
    Acknowledges `LOCK`.

- `UNLOCKED`  
    Acknowledges `UNLOCK`.

- `READ_RESPONSE`  
    Contains the result of a `READ` request.

    Additional Fields:
    - `value` (`string`): A base64 string representing the read data

- `WRITE_RESPONSE`  
    Acknowledges `WRITE`.

- `DISPLAY_MESSAGE_RESPONSE`  
    Acknowledges `DISPLAY_MESSAGE`.

- `SET_MESSAGE_INTERVAL_RESPONSE`  
    Acknowledges `SET_MESSAGE_INTERVAL`.

- `ERROR`  
    Signifies that something has gone wrong while processing a request.

    Additional Fields:
    - `err` (`string`): A description of the problem
]]

local bizhawk_version = client.getversion()
local bizhawk_major, bizhawk_minor, bizhawk_patch = bizhawk_version:match("(%d+)%.(%d+)%.?(%d*)")
bizhawk_major = tonumber(bizhawk_major)
bizhawk_minor = tonumber(bizhawk_minor)
if bizhawk_patch == "" then
    bizhawk_patch = 0
else
    bizhawk_patch = tonumber(bizhawk_patch)
end

local lua_major, lua_minor = _VERSION:match("Lua (%d+)%.(%d+)")
lua_major = tonumber(lua_major)
lua_minor = tonumber(lua_minor)

if lua_major > 5 or (lua_major == 5 and lua_minor >= 3) then
    require("lua_5_3_compat")
end

local base64 = require("base64")
local socket = require("socket")
local json = require("json")

local SOCKET_PORT_FIRST = 43055
local SOCKET_PORT_RANGE_SIZE = 5
local SOCKET_PORT_LAST = SOCKET_PORT_FIRST + SOCKET_PORT_RANGE_SIZE

local STATE_NOT_CONNECTED = 0
local STATE_CONNECTED = 1

local server = nil
local client_socket = nil

local current_state = STATE_NOT_CONNECTED

local timeout_timer = 0
local message_timer = 0
local message_interval = 0
local prev_time = 0
local current_time = 0

local locked = false

local rom_hash = nil

function queue_push (self, value)
    self[self.right] = value
    self.right = self.right + 1
end

function queue_is_empty (self)
    return self.right == self.left
end

function queue_shift (self)
    value = self[self.left]
    self[self.left] = nil
    self.left = self.left + 1
    return value
end

function new_queue ()
    local queue = {left = 1, right = 1}
    return setmetatable(queue, {__index = {is_empty = queue_is_empty, push = queue_push, shift = queue_shift}})
end

local message_queue = new_queue()

-- Persistent text overlay controlled by the connected AP client.
-- Coordinates use BizHawk's full client canvas. For vertically stacked
-- Nintendo DS screens, y=5 places the overlay on the upper screen.
local persistent_overlay = {
    visible = false,
    x = 5,
    y = 5,
    line_height = 13,
    foreground = "white",
    background = "black",
    lines = {},
}

local acww_notification = {
    visible = false,
    x = 5,
    y = 150,
    line_height = 13,
    foreground = "white",
    background = "black",
    remaining_frames = 0,
    lines = {},
}

local acww_notification_queue = new_queue()

local function draw_persistent_overlay()
    if not persistent_overlay.visible then
        return
    end

    for index, line in ipairs(persistent_overlay.lines) do
        gui.text(
            persistent_overlay.x,
            persistent_overlay.y
                + ((index - 1) * persistent_overlay.line_height),
            tostring(line),
            persistent_overlay.foreground,
            persistent_overlay.background
        )
    end
end


local function activate_next_acww_notification()
    if acww_notification_queue:is_empty() then
        acww_notification.visible = false
        return
    end

    local next_notification =
        acww_notification_queue:shift()

    acww_notification.visible = true
    acww_notification.x = next_notification.x
    acww_notification.y = next_notification.y
    acww_notification.line_height =
        next_notification.line_height
    acww_notification.foreground =
        next_notification.foreground
    acww_notification.background =
        next_notification.background
    acww_notification.remaining_frames =
        next_notification.duration_frames
    acww_notification.lines =
        next_notification.lines
end

local function draw_acww_notification()
    if (
        not acww_notification.visible
        or acww_notification.remaining_frames <= 0
    ) then
        activate_next_acww_notification()
    end

    if not acww_notification.visible then
        return
    end

    for index, line in ipairs(acww_notification.lines) do
        gui.text(
            acww_notification.x,
            acww_notification.y
                + ((index - 1) * acww_notification.line_height),
            tostring(line),
            acww_notification.foreground,
            acww_notification.background
        )
    end

    acww_notification.remaining_frames =
        acww_notification.remaining_frames - 1
end


-- ACWW forward-only time controller.
-- The AP client sends only unlocked months. The dropdown is rebuilt whenever
-- that list changes, so unavailable months never appear.
local ACWW_CLOCK_OFFSET_ADDRESS = 0x021ED304
local ACWW_TIME_STRUCT_ADDRESS = 0x021D72EC

-- Inventory layout through the ARM9 System Bus.
local ACWW_INVENTORY_BASE_ADDRESS = 0x021D8E7E
local ACWW_INVENTORY_SLOT_COUNT = 15
local ACWW_INVENTORY_SLOT_SIZE = 2
local ACWW_EMPTY_INVENTORY_ITEM = 0xFFF1

-- Outdoor town-object table used by the Wild World v1.1 weed-removal
-- Action Replay code. Each entry is a 16-bit object ID.
local ACWW_TOWN_OBJECT_BASE_ADDRESS = 0x021E36A4
local ACWW_TOWN_OBJECT_SLOT_COUNT = 0x1000
local ACWW_FIRST_WEED_OBJECT_ID = 0x001C
local ACWW_LAST_WEED_OBJECT_ID = 0x0025
local ACWW_EMPTY_TOWN_OBJECT_ID = 0xFFF1

-- Save-data addresses through the ARM9 System Bus.
-- memory_map.py stores Main RAM offsets, so add 0x02000000 for bus access.
local ACWW_JOURNAL_BASE_ADDRESS = 0x021D8F39
local ACWW_JOURNAL_START_BIT = 1
local ACWW_BUG_COUNT = 56

local ACWW_FOSSIL_MUSEUM_ADDRESS = 0x021ED0A0
local ACWW_FISH_MUSEUM_ADDRESS = 0x021ED0B8
local ACWW_BUG_MUSEUM_ADDRESS = 0x021ED0D8
local ACWW_PAINTING_MUSEUM_ADDRESS = 0x021ED0F4
local ACWW_FISH_MUSEUM_START_INDEX = 6
local ACWW_PAINTING_MUSEUM_START_INDEX = 2

local ACWW_MONTH_NAMES = {
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
}

local ACWW_RECLAIMABLE_RESOURCES = {
    {name = "Apple", game_id = 0x1518},
    {name = "Orange", game_id = 0x1519},
    {name = "Pear", game_id = 0x151A},
    {name = "Peach", game_id = 0x151B},
    {name = "Cherry", game_id = 0x151C},
    {name = "Red Roses", game_id = 0x1483},
    {name = "White Roses", game_id = 0x1484},
    {name = "Pink Roses", game_id = 0x1486},
    {name = "Purple Roses", game_id = 0x1488},
    {name = "Black Roses", game_id = 0x1489},
    {name = "Blue Roses", game_id = 0x148A},
    {name = "Coconut", game_id = 0x1548},
    {name = "Spoiled Turnips", game_id = 0x154A},
}

local acww_unlocked_months = {}
local acww_claimables = {}
local acww_claimables_by_name = {}
local acww_claimable_buttons = {}
local acww_reclaimable_specimens = {}
local acww_reclaimable_specimens_by_category = {}
local acww_specimen_category_dropdown = nil
local acww_specimen_dropdown = nil
local acww_specimen_reclaim_button = nil
local acww_previous_specimen_category = nil
local acww_restore_progress = {
    bugs = {},
    fish = {},
    museum_bugs = {},
    museum_fish = {},
    museum_fossils = {},
    museum_paintings = {},
}
local acww_time_form = nil
local acww_month_dropdown = nil
local acww_day_box = nil
local acww_hour_box = nil
local acww_minute_box = nil
local acww_current_label = nil
local acww_target_label = nil
local acww_status_label = nil

local function string_contains(text, fragment)
    return string.find(
        string.lower(text),
        string.lower(fragment),
        1,
        true
    ) ~= nil
end

local function find_memory_domain(required_fragments)
    for _, domain in ipairs(memory.getmemorydomainlist()) do
        local matches = true

        for _, fragment in ipairs(required_fragments) do
            if not string_contains(domain, fragment) then
                matches = false
                break
            end
        end

        if matches then
            return domain
        end
    end

    return nil
end

local function acww_get_domains()
    local arm7 =
        find_memory_domain({"arm7", "system bus"}) or
        find_memory_domain({"arm7", "bus"})

    local arm9 =
        find_memory_domain({"arm9", "system bus"}) or
        find_memory_domain({"arm9", "bus"})

    return arm7, arm9
end

local function acww_normalize_year(year)
    if year >= 0 and year <= 99 then
        return 2000 + year
    end

    return year
end

local function acww_read_game_time()
    local _, arm9 = acww_get_domains()

    if arm9 == nil then
        error("ACWW time controller could not find ARM9 System Bus.")
    end

    return {
        year = acww_normalize_year(
            memory.read_u32_le(
                ACWW_TIME_STRUCT_ADDRESS + 0x00,
                arm9
            )
        ),
        month = memory.read_u32_le(
            ACWW_TIME_STRUCT_ADDRESS + 0x04,
            arm9
        ),
        day = memory.read_u32_le(
            ACWW_TIME_STRUCT_ADDRESS + 0x08,
            arm9
        ),
        hour = memory.read_u32_le(
            ACWW_TIME_STRUCT_ADDRESS + 0x10,
            arm9
        ),
        minute = memory.read_u32_le(
            ACWW_TIME_STRUCT_ADDRESS + 0x14,
            arm9
        ),
        second = memory.read_u32_le(
            ACWW_TIME_STRUCT_ADDRESS + 0x18,
            arm9
        ),
    }
end

local function acww_u32_to_s32(value)
    if value >= 0x80000000 then
        return value - 0x100000000
    end

    return value
end

local function acww_s32_to_u32(value)
    if value < 0 then
        return value + 0x100000000
    end

    return value
end

local function acww_read_offset()
    local arm7, _ = acww_get_domains()

    if arm7 == nil then
        error("ACWW time controller could not find ARM7 System Bus.")
    end

    return acww_u32_to_s32(
        memory.read_u32_le(
            ACWW_CLOCK_OFFSET_ADDRESS,
            arm7
        )
    )
end

local function acww_write_offset(value)
    local arm7, _ = acww_get_domains()

    if arm7 == nil then
        error("ACWW time controller could not find ARM7 System Bus.")
    end

    if value < -2147483648 or value > 2147483647 then
        error("Calculated ACWW time offset is outside int32 range.")
    end

    memory.write_u32_le(
        ACWW_CLOCK_OFFSET_ADDRESS,
        acww_s32_to_u32(value),
        arm7
    )
end

local function acww_is_leap_year(year)
    return
        (year % 4 == 0 and year % 100 ~= 0)
        or year % 400 == 0
end

local ACWW_DAYS_IN_MONTH = {
    31, 28, 31, 30, 31, 30,
    31, 31, 30, 31, 30, 31,
}

local function acww_days_in_month(year, month)
    if month == 2 and acww_is_leap_year(year) then
        return 29
    end

    return ACWW_DAYS_IN_MONTH[month]
end

local function acww_date_to_day_number(year, month, day)
    local adjusted_year = year

    if month <= 2 then
        adjusted_year = adjusted_year - 1
    end

    local era = math.floor(adjusted_year / 400)
    local year_of_era = adjusted_year - era * 400

    local adjusted_month

    if month > 2 then
        adjusted_month = month - 3
    else
        adjusted_month = month + 9
    end

    local day_of_year =
        math.floor((153 * adjusted_month + 2) / 5)
        + day - 1

    local day_of_era =
        year_of_era * 365
        + math.floor(year_of_era / 4)
        - math.floor(year_of_era / 100)
        + day_of_year

    return era * 146097 + day_of_era
end

local function acww_datetime_to_minutes(value)
    return
        acww_date_to_day_number(
            value.year,
            value.month,
            value.day
        ) * 1440
        + value.hour * 60
        + value.minute
end

local function acww_parse_integer(control, label)
    local value = tonumber(forms.gettext(control))

    if value == nil or value ~= math.floor(value) then
        error(label .. " must be a whole number.")
    end

    return value
end

local function acww_month_number_from_name(month_name)
    -- BizHawk's forms.dropdown alphabetizes its entries. Dropdown labels are
    -- prefixed with the month number so they remain in calendar order.
    local normalized_name = tostring(month_name)
    normalized_name = string.gsub(
        normalized_name,
        "%s*%-%s*Locked$",
        ""
    )

    for month_number, name in ipairs(ACWW_MONTH_NAMES) do
        if name == normalized_name then
            return month_number
        end
    end

    return nil
end

local function acww_is_month_unlocked(month_number)
    for _, unlocked_month in ipairs(acww_unlocked_months) do
        if unlocked_month == month_number then
            return true
        end
    end

    return false
end

local function acww_choose_next_target(
    current,
    month,
    day,
    hour,
    minute
)
    local candidate_year = current.year

    while candidate_year <= 2099 do
        if day <= acww_days_in_month(candidate_year, month) then
            local candidate = {
                year = candidate_year,
                month = month,
                day = day,
                hour = hour,
                minute = minute,
            }

            if acww_datetime_to_minutes(candidate)
                > acww_datetime_to_minutes(current) then
                return candidate
            end
        end

        candidate_year = candidate_year + 1
    end

    return nil
end

local function acww_validate_request(month, day, hour, minute)
    if month == nil then
        return false, "Select a month."
    end

    if not acww_is_month_unlocked(month) then
        return false, "That month has not been unlocked yet."
    end

    if day < 1 or day > 31 then
        return false, "Day must be between 1 and 31."
    end

    if hour < 0 or hour > 23 then
        return false, "Hour must be between 0 and 23."
    end

    if minute < 0 or minute > 59 then
        return false, "Minute must be between 0 and 59."
    end

    return true, nil
end

local function acww_refresh_form_labels()
    if (
        acww_time_form == nil
        or acww_current_label == nil
    ) then
        return
    end

    local ok, current = pcall(acww_read_game_time)

    if not ok then
        forms.settext(
            acww_current_label,
            "Waiting for ACWW..."
        )
        return
    end

    forms.settext(
        acww_current_label,
        string.format(
            "%04d-%02d-%02d %02d:%02d:%02d",
            current.year,
            current.month,
            current.day,
            current.hour,
            current.minute,
            current.second
        )
    )
end

local function acww_preview_time()
    local ok, message = pcall(function()
        local current = acww_read_game_time()
        local month_name = forms.gettext(acww_month_dropdown)
        local month = acww_month_number_from_name(month_name)
        local day = acww_parse_integer(acww_day_box, "Day")
        local hour = acww_parse_integer(acww_hour_box, "Hour")
        local minute = acww_parse_integer(
            acww_minute_box,
            "Minute"
        )

        local valid, validation_error =
            acww_validate_request(month, day, hour, minute)

        if not valid then
            error(validation_error)
        end

        local target = acww_choose_next_target(
            current,
            month,
            day,
            hour,
            minute
        )

        if target == nil then
            error("No later matching date exists before 2099.")
        end

        local delta =
            acww_datetime_to_minutes(target)
            - acww_datetime_to_minutes(current)

        forms.settext(
            acww_target_label,
            string.format(
                "%04d-%02d-%02d %02d:%02d",
                target.year,
                target.month,
                target.day,
                target.hour,
                target.minute
            )
        )

        forms.settext(
            acww_status_label,
            string.format(
                "Advance %d days, %d hours, %d minutes.",
                math.floor(delta / 1440),
                math.floor((delta % 1440) / 60),
                delta % 60
            )
        )
    end)

    if not ok then
        forms.settext(
            acww_status_label,
            "ERROR: " .. tostring(message)
        )
    end
end

local function acww_advance_time()
    local ok, message = pcall(function()
        local current = acww_read_game_time()
        local current_offset = acww_read_offset()
        local month_name = forms.gettext(acww_month_dropdown)
        local month = acww_month_number_from_name(month_name)
        local day = acww_parse_integer(acww_day_box, "Day")
        local hour = acww_parse_integer(acww_hour_box, "Hour")
        local minute = acww_parse_integer(
            acww_minute_box,
            "Minute"
        )

        local valid, validation_error =
            acww_validate_request(month, day, hour, minute)

        if not valid then
            error(validation_error)
        end

        local target = acww_choose_next_target(
            current,
            month,
            day,
            hour,
            minute
        )

        if target == nil then
            error("No later matching date exists before 2099.")
        end

        if day > acww_days_in_month(target.year, month) then
            error("That day does not exist in the selected month.")
        end

        local delta =
            acww_datetime_to_minutes(target)
            - acww_datetime_to_minutes(current)

        local new_offset = current_offset + delta
        acww_write_offset(new_offset)

        forms.settext(
            acww_target_label,
            string.format(
                "%04d-%02d-%02d %02d:%02d",
                target.year,
                target.month,
                target.day,
                target.hour,
                target.minute
            )
        )

        forms.settext(
            acww_status_label,
            "Time advanced. Exit/enter a building and allow "
            .. "the mayor rollover."
        )
    end)

    if not ok then
        forms.settext(
            acww_status_label,
            "ERROR: " .. tostring(message)
        )
    end
end

local function acww_find_inventory_domain()
    return
        find_memory_domain({"arm9", "system bus"}) or
        find_memory_domain({"arm9", "bus"})
end

local function acww_find_empty_inventory_slot()
    local inventory_domain = acww_find_inventory_domain()

    if inventory_domain == nil then
        error(
            "ACWW reclaim system could not find "
            .. "the ARM9 System Bus."
        )
    end

    for slot_index = 0, ACWW_INVENTORY_SLOT_COUNT - 1 do
        local slot_address =
            ACWW_INVENTORY_BASE_ADDRESS
            + slot_index * ACWW_INVENTORY_SLOT_SIZE

        local item_id = memory.read_u16_le(
            slot_address,
            inventory_domain
        )

        if item_id == ACWW_EMPTY_INVENTORY_ITEM then
            return slot_index, inventory_domain
        end
    end

    return nil, inventory_domain
end

local function acww_inventory_contains_item(game_item_id)
    local inventory_domain = acww_find_inventory_domain()

    if inventory_domain == nil then
        error(
            "ACWW reclaim system could not find "
            .. "the ARM9 System Bus."
        )
    end

    for slot_index = 0, ACWW_INVENTORY_SLOT_COUNT - 1 do
        local slot_address =
            ACWW_INVENTORY_BASE_ADDRESS
            + slot_index * ACWW_INVENTORY_SLOT_SIZE

        if memory.read_u16_le(slot_address, inventory_domain)
            == game_item_id then
            return true
        end
    end

    return false
end

local function acww_claim_item(item_name, game_item_id)
    local ok, message = pcall(function()
        local slot_index, inventory_domain =
            acww_find_empty_inventory_slot()

        if slot_index == nil then
            error("Inventory is full.")
        end

        local slot_address =
            ACWW_INVENTORY_BASE_ADDRESS
            + slot_index * ACWW_INVENTORY_SLOT_SIZE

        memory.write_u16_le(
            slot_address,
            game_item_id,
            inventory_domain
        )

        forms.settext(
            acww_status_label,
            string.format(
                "Claimed %s in inventory slot %d.",
                item_name,
                slot_index + 1
            )
        )

        print(string.format(
            "ACWW reclaim: %s (0x%04X) -> slot %d",
            item_name,
            game_item_id,
            slot_index + 1
        ))
    end)

    if not ok then
        forms.settext(
            acww_status_label,
            "ERROR: " .. tostring(message)
        )
    end
end

local function acww_find_restore_domain()
    local _, arm9 = acww_get_domains()
    return arm9
end

local function acww_set_journal_bit(
    arm9,
    global_index
)
    local absolute_bit =
        ACWW_JOURNAL_START_BIT + global_index
    local byte_offset = math.floor(absolute_bit / 8)
    local bit_index = absolute_bit % 8
    local address =
        ACWW_JOURNAL_BASE_ADDRESS + byte_offset

    local current = memory.read_u8(address, arm9)
    local mask = bit.lshift(1, bit_index)

    if bit.band(current, mask) ~= 0 then
        return false
    end

    memory.write_u8(
        address,
        bit.bor(current, mask),
        arm9
    )
    return true
end

local function acww_set_museum_nibble(
    arm9,
    section_address,
    absolute_index
)
    local group_index = math.floor(absolute_index / 8)
    local position_in_group = absolute_index % 8
    local group_address =
        section_address + group_index * 4
    local shift = position_in_group * 4
    local group_value = memory.read_u32_le(
        group_address,
        arm9
    )
    local current_nibble =
        bit.band(bit.rshift(group_value, shift), 0x0F)

    if current_nibble ~= 0 then
        return false
    end

    local updated_value = bit.bor(
        group_value,
        bit.lshift(1, shift)
    )

    memory.write_u32_le(
        group_address,
        updated_value,
        arm9
    )
    return true
end

local function acww_restore_ap_progress()
    local ok, message = pcall(function()
        local arm9 = acww_find_restore_domain()

        if arm9 == nil then
            error(
                "Restore AP Progress could not find ARM9 System Bus."
            )
        end

        local restored_journal = 0
        local restored_museum = 0

        for _, bug_index in ipairs(
            acww_restore_progress.bugs
        ) do
            if acww_set_journal_bit(
                arm9,
                bug_index
            ) then
                restored_journal = restored_journal + 1
            end
        end

        for _, fish_index in ipairs(
            acww_restore_progress.fish
        ) do
            if acww_set_journal_bit(
                arm9,
                ACWW_BUG_COUNT + fish_index
            ) then
                restored_journal = restored_journal + 1
            end
        end

        local museum_sections = {
            {
                indexes =
                    acww_restore_progress.museum_bugs,
                address = ACWW_BUG_MUSEUM_ADDRESS,
                start_index = 0,
            },
            {
                indexes =
                    acww_restore_progress.museum_fish,
                address = ACWW_FISH_MUSEUM_ADDRESS,
                start_index =
                    ACWW_FISH_MUSEUM_START_INDEX,
            },
            {
                indexes =
                    acww_restore_progress.museum_fossils,
                address = ACWW_FOSSIL_MUSEUM_ADDRESS,
                start_index = 0,
            },
            {
                indexes =
                    acww_restore_progress.museum_paintings,
                address = ACWW_PAINTING_MUSEUM_ADDRESS,
                start_index =
                    ACWW_PAINTING_MUSEUM_START_INDEX,
            },
        }

        for _, section in ipairs(museum_sections) do
            for _, item_index in ipairs(section.indexes) do
                if acww_set_museum_nibble(
                    arm9,
                    section.address,
                    section.start_index + item_index
                ) then
                    restored_museum = restored_museum + 1
                end
            end
        end

        forms.settext(
            acww_status_label,
            string.format(
                "Restored %d journal entr%s and %d museum entr%s. "
                .. "Save normally after confirming the results.",
                restored_journal,
                restored_journal == 1 and "y" or "ies",
                restored_museum,
                restored_museum == 1 and "y" or "ies"
            )
        )

        print(string.format(
            "ACWW Restore AP Progress: %d journal, %d museum.",
            restored_journal,
            restored_museum
        ))
    end)

    if not ok then
        forms.settext(
            acww_status_label,
            "ERROR: " .. tostring(message)
        )
    end
end

local function acww_remove_all_weeds()
    local ok, message = pcall(function()
        local _, arm9 = acww_get_domains()

        if arm9 == nil then
            error("Weed Whacker could not find ARM9 System Bus.")
        end

        local removed_count = 0

        for slot_index = 0, ACWW_TOWN_OBJECT_SLOT_COUNT - 1 do
            local object_address =
                ACWW_TOWN_OBJECT_BASE_ADDRESS + slot_index * 2

            local object_id = memory.read_u16_le(
                object_address,
                arm9
            )

            if (
                object_id >= ACWW_FIRST_WEED_OBJECT_ID
                and object_id <= ACWW_LAST_WEED_OBJECT_ID
            ) then
                memory.write_u16_le(
                    object_address,
                    ACWW_EMPTY_TOWN_OBJECT_ID,
                    arm9
                )

                removed_count = removed_count + 1
            end
        end

        forms.settext(
            acww_status_label,
            string.format(
                "Weed Whacker removed %d weed%s. "
                .. "Exit and re-enter an acre or building to refresh.",
                removed_count,
                removed_count == 1 and "" or "s"
            )
        )

        print(string.format(
            "ACWW Weed Whacker removed %d weeds.",
            removed_count
        ))
    end)

    if not ok then
        forms.settext(
            acww_status_label,
            "ERROR: " .. tostring(message)
        )
    end
end


local function acww_destroy_time_form()
    if acww_time_form ~= nil then
        forms.destroy(acww_time_form)
        acww_time_form = nil
        acww_month_dropdown = nil
        acww_claimable_buttons = {}
        acww_specimen_category_dropdown = nil
        acww_specimen_dropdown = nil
        acww_specimen_reclaim_button = nil
        acww_previous_specimen_category = nil
        acww_day_box = nil
        acww_hour_box = nil
        acww_minute_box = nil
        acww_current_label = nil
        acww_target_label = nil
        acww_status_label = nil
    end
end

local function acww_month_display_name(month_number)
    local label = ACWW_MONTH_NAMES[month_number]

    if not acww_is_month_unlocked(month_number) then
        label = label .. " - Locked"
    end

    return label
end

local function acww_update_month_dropdown()
    if acww_month_dropdown == nil then
        return
    end

    local previous_month = acww_month_number_from_name(
        forms.gettext(acww_month_dropdown)
    )
    local dropdown_items = {}

    for month_number = 1, 12 do
        table.insert(
            dropdown_items,
            acww_month_display_name(month_number)
        )
    end

    forms.setdropdownitems(
        acww_month_dropdown,
        dropdown_items,
        false
    )

    if previous_month ~= nil then
        forms.settext(
            acww_month_dropdown,
            acww_month_display_name(previous_month)
        )
        return
    end

    local first_month = acww_unlocked_months[1] or 1
    forms.settext(
        acww_month_dropdown,
        acww_month_display_name(first_month)
    )
end

local function acww_update_claimable_buttons()
    if acww_time_form == nil then
        return
    end

    for _, resource in ipairs(ACWW_RECLAIMABLE_RESOURCES) do
        local button = acww_claimable_buttons[resource.name]

        if button ~= nil then
            forms.setproperty(
                button,
                "Enabled",
                acww_claimables_by_name[resource.name] == true
            )
        end
    end
end

local ACWW_SPECIMEN_CATEGORIES = {
    "Bugs",
    "Fish",
    "Fossils",
    "Paintings",
}

local function acww_get_selected_reclaimable_specimen()
    if (
        acww_specimen_category_dropdown == nil
        or acww_specimen_dropdown == nil
    ) then
        return nil
    end

    local category = forms.gettext(
        acww_specimen_category_dropdown
    )
    local specimen_name = forms.gettext(acww_specimen_dropdown)
    local category_specimens =
        acww_reclaimable_specimens_by_category[category] or {}

    for _, specimen in ipairs(category_specimens) do
        if specimen.name == specimen_name then
            return specimen
        end
    end

    return nil
end

local function acww_update_specimen_dropdown(force)
    if (
        acww_specimen_category_dropdown == nil
        or acww_specimen_dropdown == nil
    ) then
        return
    end

    local category = forms.gettext(
        acww_specimen_category_dropdown
    )

    if category == "" then
        category = ACWW_SPECIMEN_CATEGORIES[1]
        forms.settext(acww_specimen_category_dropdown, category)
    end

    if not force and category == acww_previous_specimen_category then
        return
    end

    acww_previous_specimen_category = category

    local previous_name = forms.gettext(acww_specimen_dropdown)
    local names = {}
    local category_specimens =
        acww_reclaimable_specimens_by_category[category] or {}

    for _, specimen in ipairs(category_specimens) do
        table.insert(names, specimen.name)
    end

    if #names == 0 then
        table.insert(names, "None available")
    end

    forms.setdropdownitems(acww_specimen_dropdown, names, false)

    local selected_name = names[1]

    for _, name in ipairs(names) do
        if name == previous_name then
            selected_name = previous_name
            break
        end
    end

    forms.settext(acww_specimen_dropdown, selected_name)

    if acww_specimen_reclaim_button ~= nil then
        forms.setproperty(
            acww_specimen_reclaim_button,
            "Enabled",
            #category_specimens > 0
        )
    end
end

local function acww_remove_local_reclaimable_specimen(specimen)
    local remaining = {}

    for _, current in ipairs(acww_reclaimable_specimens) do
        if not (
            current.category == specimen.category
            and current.name == specimen.name
        ) then
            table.insert(remaining, current)
        end
    end

    acww_reclaimable_specimens = remaining
    acww_reclaimable_specimens_by_category = {}

    for _, current in ipairs(acww_reclaimable_specimens) do
        local category_list =
            acww_reclaimable_specimens_by_category[current.category]

        if category_list == nil then
            category_list = {}
            acww_reclaimable_specimens_by_category[current.category] =
                category_list
        end

        table.insert(category_list, current)
    end
end

local function acww_reclaim_selected_specimen()
    local ok, message = pcall(function()
        local specimen = acww_get_selected_reclaimable_specimen()

        if specimen == nil then
            error("No recoverable specimen is selected.")
        end

        if acww_inventory_contains_item(specimen.game_id) then
            acww_remove_local_reclaimable_specimen(specimen)
            acww_previous_specimen_category = nil
            acww_update_specimen_dropdown(true)
            error(specimen.name .. " is already in the inventory.")
        end

        local slot_index, inventory_domain =
            acww_find_empty_inventory_slot()

        if slot_index == nil then
            error("Inventory is full.")
        end

        local slot_address =
            ACWW_INVENTORY_BASE_ADDRESS
            + slot_index * ACWW_INVENTORY_SLOT_SIZE

        memory.write_u16_le(
            slot_address,
            specimen.game_id,
            inventory_domain
        )

        acww_remove_local_reclaimable_specimen(specimen)
        acww_previous_specimen_category = nil
        acww_update_specimen_dropdown(true)

        forms.settext(
            acww_status_label,
            string.format(
                "Restored %s to inventory slot %d.",
                specimen.name,
                slot_index + 1
            )
        )

        print(string.format(
            "ACWW specimen recovery: %s (%s, 0x%04X) -> slot %d",
            specimen.name,
            specimen.category,
            specimen.game_id,
            slot_index + 1
        ))
    end)

    if not ok then
        forms.settext(
            acww_status_label,
            "ERROR: " .. tostring(message)
        )
    end
end

local function acww_create_time_form()
    acww_destroy_time_form()

    if emu.getsystemid() ~= "NDS" then
        return
    end

    local claimable_rows =
        math.ceil(#ACWW_RECLAIMABLE_RESOURCES / 2)

    local form_height = 535 + claimable_rows * 34

    acww_time_form = forms.newform(
        430,
        form_height,
        "ACWW Archipelago Master Controller"
    )

    forms.label(
        acww_time_form,
        "Current game time:",
        10,
        10,
        130,
        20
    )

    acww_current_label = forms.label(
        acww_time_form,
        "Reading...",
        145,
        10,
        235,
        20
    )

    forms.label(
        acww_time_form,
        "Next matching date:",
        10,
        35,
        130,
        20
    )

    acww_target_label = forms.label(
        acww_time_form,
        "Preview first",
        145,
        35,
        235,
        20
    )

    forms.label(acww_time_form, "Month", 20, 80, 80, 20)
    acww_month_dropdown = forms.dropdown(
        acww_time_form,
        {},
        115,
        77,
        120,
        24
    )

    forms.label(acww_time_form, "Day", 20, 115, 80, 20)
    acww_day_box = forms.textbox(
        acww_time_form,
        "1",
        120,
        20,
        nil,
        115,
        112
    )

    forms.label(
        acww_time_form,
        "Hour (0-23)",
        20,
        150,
        90,
        20
    )
    acww_hour_box = forms.textbox(
        acww_time_form,
        "12",
        120,
        20,
        nil,
        115,
        147
    )

    forms.label(acww_time_form, "Minute", 20, 185, 80, 20)
    acww_minute_box = forms.textbox(
        acww_time_form,
        "0",
        120,
        20,
        nil,
        115,
        182
    )

    forms.button(
        acww_time_form,
        "Preview",
        acww_preview_time,
        265,
        80,
        115,
        35
    )

    forms.button(
        acww_time_form,
        "Advance Time",
        acww_advance_time,
        265,
        130,
        115,
        45
    )

    forms.button(
        acww_time_form,
        "Weed Whacker",
        acww_remove_all_weeds,
        265,
        185,
        115,
        35
    )

    forms.button(
        acww_time_form,
        "Restore AP Progress",
        acww_restore_ap_progress,
        20,
        225,
        360,
        35
    )

    forms.label(
        acww_time_form,
        "Reclaimable Resources",
        10,
        280,
        220,
        20
    )

    acww_claimable_buttons = {}

    for index, resource in ipairs(ACWW_RECLAIMABLE_RESOURCES) do
        local column = (index - 1) % 2
        local row = math.floor((index - 1) / 2)
        local button_x = 20 + column * 195
        local button_y = 305 + row * 34
        local item_name = resource.name
        local game_item_id = resource.game_id

        local button = forms.button(
            acww_time_form,
            item_name,
            function()
                if acww_claimables_by_name[item_name] then
                    acww_claim_item(
                        item_name,
                        game_item_id
                    )
                end
            end,
            button_x,
            button_y,
            180,
            28
        )

        acww_claimable_buttons[item_name] = button
    end

    local specimen_y = 350 + claimable_rows * 34

    forms.label(
        acww_time_form,
        "Restore Undonated Specimen",
        10,
        specimen_y,
        240,
        20
    )

    forms.label(
        acww_time_form,
        "Category",
        20,
        specimen_y + 30,
        80,
        20
    )

    acww_specimen_category_dropdown = forms.dropdown(
        acww_time_form,
        ACWW_SPECIMEN_CATEGORIES,
        105,
        specimen_y + 27,
        125,
        24
    )

    if acww_specimen_category_dropdown ~= nil then
        forms.settext(
            acww_specimen_category_dropdown,
            ACWW_SPECIMEN_CATEGORIES[1]
        )
    end

    forms.label(
        acww_time_form,
        "Specimen",
        20,
        specimen_y + 65,
        80,
        20
    )

    acww_specimen_dropdown = forms.dropdown(
        acww_time_form,
        {"None available"},
        105,
        specimen_y + 62,
        170,
        24
    )

    acww_specimen_reclaim_button = forms.button(
        acww_time_form,
        "Restore Specimen",
        acww_reclaim_selected_specimen,
        285,
        specimen_y + 57,
        105,
        34
    )

    local status_y = specimen_y + 110

    acww_status_label = forms.label(
        acww_time_form,
        "Locked months are labeled; locked resources are disabled.",
        10,
        status_y,
        395,
        45
    )

    if acww_month_dropdown ~= nil then
        acww_update_month_dropdown()
    end
    acww_update_claimable_buttons()
    if (
        acww_specimen_category_dropdown ~= nil
        and acww_specimen_dropdown ~= nil
    ) then
        acww_update_specimen_dropdown(true)
    end
    acww_refresh_form_labels()
end

local function acww_set_claimables(claimables)
    local sanitized = {}
    local seen = {}

    if type(claimables) == "table" then
        for _, raw_claimable in ipairs(claimables) do
            if type(raw_claimable) == "table" then
                local item_name = tostring(
                    raw_claimable["name"] or ""
                )
                local game_item_id = tonumber(
                    raw_claimable["game_id"]
                )

                if (
                    item_name ~= ""
                    and game_item_id ~= nil
                    and game_item_id >= 0
                    and game_item_id <= 0xFFFF
                    and not seen[item_name]
                ) then
                    seen[item_name] = true
                    table.insert(
                        sanitized,
                        {
                            name = item_name,
                            game_id = math.floor(game_item_id),
                        }
                    )
                end
            end
        end
    end

    table.sort(
        sanitized,
        function(left, right)
            return left.name < right.name
        end
    )

    acww_claimables = sanitized
    acww_claimables_by_name = {}

    for _, claimable in ipairs(acww_claimables) do
        acww_claimables_by_name[claimable.name] = true
    end

end


local function acww_set_reclaimable_specimens(specimens)
    local sanitized = {}
    local seen = {}

    if type(specimens) == "table" then
        for _, raw_specimen in ipairs(specimens) do
            if type(raw_specimen) == "table" then
                local category = tostring(
                    raw_specimen["category"] or ""
                )
                local specimen_name = tostring(
                    raw_specimen["name"] or ""
                )
                local game_item_id = tonumber(
                    raw_specimen["game_id"]
                )
                local unique_key = category .. "|" .. specimen_name

                if (
                    category ~= ""
                    and specimen_name ~= ""
                    and game_item_id ~= nil
                    and game_item_id >= 0
                    and game_item_id <= 0xFFFF
                    and not seen[unique_key]
                ) then
                    seen[unique_key] = true
                    table.insert(sanitized, {
                        category = category,
                        name = specimen_name,
                        game_id = math.floor(game_item_id),
                    })
                end
            end
        end
    end

    table.sort(
        sanitized,
        function(left, right)
            if left.category == right.category then
                return left.name < right.name
            end

            return left.category < right.category
        end
    )

    acww_reclaimable_specimens = sanitized
    acww_reclaimable_specimens_by_category = {}

    for _, specimen in ipairs(acww_reclaimable_specimens) do
        local category_list =
            acww_reclaimable_specimens_by_category[specimen.category]

        if category_list == nil then
            category_list = {}
            acww_reclaimable_specimens_by_category[specimen.category] =
                category_list
        end

        table.insert(category_list, specimen)
    end

    acww_previous_specimen_category = nil

    if (
        acww_time_form ~= nil
        and acww_specimen_category_dropdown ~= nil
        and acww_specimen_dropdown ~= nil
    ) then
        acww_update_specimen_dropdown(true)
    end
end

local function acww_sanitize_index_list(
    raw_indexes,
    maximum_count
)
    local sanitized = {}
    local seen = {}

    if type(raw_indexes) == "table" then
        for _, raw_index in ipairs(raw_indexes) do
            local index = tonumber(raw_index)

            if index ~= nil then
                index = math.floor(index)

                if (
                    index >= 0
                    and index < maximum_count
                    and not seen[index]
                ) then
                    seen[index] = true
                    table.insert(sanitized, index)
                end
            end
        end
    end

    table.sort(sanitized)
    return sanitized
end

local function acww_set_restore_progress(progress)
    progress =
        type(progress) == "table" and progress or {}

    acww_restore_progress = {
        bugs = acww_sanitize_index_list(
            progress["bugs"],
            56
        ),
        fish = acww_sanitize_index_list(
            progress["fish"],
            56
        ),
        museum_bugs = acww_sanitize_index_list(
            progress["museum_bugs"],
            56
        ),
        museum_fish = acww_sanitize_index_list(
            progress["museum_fish"],
            56
        ),
        museum_fossils = acww_sanitize_index_list(
            progress["museum_fossils"],
            52
        ),
        museum_paintings = acww_sanitize_index_list(
            progress["museum_paintings"],
            20
        ),
    }

end


local function acww_set_unlocked_months(months)
    local sanitized = {}
    local seen = {}

    if type(months) == "table" then
        for _, raw_month in ipairs(months) do
            local month_number = tonumber(raw_month)

            if month_number ~= nil then
                month_number = math.floor(month_number)

                if (
                    month_number >= 1
                    and month_number <= 12
                    and not seen[month_number]
                ) then
                    seen[month_number] = true
                    table.insert(sanitized, month_number)
                end
            end
        end
    end

    table.sort(sanitized)
    acww_unlocked_months = sanitized

end


function lock ()
    locked = true
    client_socket:settimeout(2)
end

function unlock ()
    locked = false
    client_socket:settimeout(0)
end

request_handlers = {
    ["PING"] = function (req)
        local res = {}

        res["type"] = "PONG"

        return res
    end,

    ["SYSTEM"] = function (req)
        local res = {}

        res["type"] = "SYSTEM_RESPONSE"
        res["value"] = emu.getsystemid()

        return res
    end,

    ["PREFERRED_CORES"] = function (req)
        local res = {}
        local preferred_cores = client.getconfig().PreferredCores
        local systems_enumerator = preferred_cores.Keys:GetEnumerator()

        res["type"] = "PREFERRED_CORES_RESPONSE"
        res["value"] = {}

        while systems_enumerator:MoveNext() do
            res["value"][systems_enumerator.Current] = preferred_cores[systems_enumerator.Current]
        end

        return res
    end,

    ["HASH"] = function (req)
        local res = {}

        res["type"] = "HASH_RESPONSE"
        res["value"] = rom_hash

        return res
    end,

    ["MEMORY_SIZE"] = function (req)
        local res = {}

        res["type"] = "MEMORY_SIZE_RESPONSE"
        res["value"] = memory.getmemorydomainsize(req["domain"])

        return res
    end,

    ["GUARD"] = function (req)
        local res = {}
        local expected_data = base64.decode(req["expected_data"])
        local actual_data = memory.read_bytes_as_array(req["address"], #expected_data, req["domain"])

        local data_is_validated = true
        for i, byte in ipairs(actual_data) do
            if byte ~= expected_data[i] then
                data_is_validated = false
                break
            end
        end

        res["type"] = "GUARD_RESPONSE"
        res["value"] = data_is_validated
        res["address"] = req["address"]

        return res
    end,

    ["LOCK"] = function (req)
        local res = {}

        res["type"] = "LOCKED"
        lock()

        return res
    end,

    ["UNLOCK"] = function (req)
        local res = {}

        res["type"] = "UNLOCKED"
        unlock()

        return res
    end,

    ["READ"] = function (req)
        local res = {}

        res["type"] = "READ_RESPONSE"
        res["value"] = base64.encode(memory.read_bytes_as_array(req["address"], req["size"], req["domain"]))

        return res
    end,

    ["WRITE"] = function (req)
        local res = {}

        res["type"] = "WRITE_RESPONSE"
        memory.write_bytes_as_array(req["address"], base64.decode(req["value"]), req["domain"])

        return res
    end,

    ["SET_ACWW_STATE"] = function (req)
        local res = {}
        local state =
            type(req["state"]) == "table"
            and req["state"]
            or {}

        acww_set_unlocked_months(
            state["unlocked_months"]
        )
        acww_set_claimables(
            state["claimables"]
        )
        acww_set_reclaimable_specimens(
            state["reclaimable_specimens"]
        )
        acww_set_restore_progress(
            state["restore_progress"]
        )

        if acww_time_form == nil then
            acww_create_time_form()
        end

        if acww_time_form ~= nil then
            acww_update_month_dropdown()
            acww_update_claimable_buttons()
            acww_update_specimen_dropdown(true)
            acww_refresh_form_labels()
        end

        res["type"] = "SET_ACWW_STATE_RESPONSE"
        return res
    end,

    ["SHOW_ACWW_NOTIFICATION"] = function (req)
        local res = {}
        local queued_notification = {
            x = tonumber(req["x"]) or 5,
            y = tonumber(req["y"]) or 150,
            line_height =
                tonumber(req["line_height"]) or 13,
            foreground =
                req["foreground"] or "white",
            background =
                req["background"] or "black",
            duration_frames =
                tonumber(req["duration_frames"]) or 300,
            lines = {},
        }

        if type(req["lines"]) == "table" then
            for _, line in ipairs(req["lines"]) do
                table.insert(
                    queued_notification.lines,
                    tostring(line)
                )
            end
        end

        acww_notification_queue:push(
            queued_notification
        )

        res["type"] = "SHOW_ACWW_NOTIFICATION_RESPONSE"
        return res
    end,

    ["SET_OVERLAY"] = function (req)
        local res = {}

        persistent_overlay.visible = req["visible"] ~= false
        persistent_overlay.x = tonumber(req["x"]) or 5
        persistent_overlay.y = tonumber(req["y"]) or 5
        persistent_overlay.line_height =
            tonumber(req["line_height"]) or 13
        persistent_overlay.foreground =
            req["foreground"] or "white"
        persistent_overlay.background =
            req["background"] or "black"
        persistent_overlay.lines = {}

        if type(req["lines"]) == "table" then
            for _, line in ipairs(req["lines"]) do
                table.insert(
                    persistent_overlay.lines,
                    tostring(line)
                )
            end
        end

        res["type"] = "SET_OVERLAY_RESPONSE"
        return res
    end,

    ["CLEAR_OVERLAY"] = function (req)
        local res = {}

        persistent_overlay.visible = false
        persistent_overlay.lines = {}

        res["type"] = "CLEAR_OVERLAY_RESPONSE"
        return res
    end,

    ["DISPLAY_MESSAGE"] = function (req)
        local res = {}

        res["type"] = "DISPLAY_MESSAGE_RESPONSE"
        message_queue:push(req["message"])

        return res
    end,

    ["SET_MESSAGE_INTERVAL"] = function (req)
        local res = {}

        res["type"] = "SET_MESSAGE_INTERVAL_RESPONSE"
        message_interval = req["value"]

        return res
    end,

    ["default"] = function (req)
        local res = {}

        res["type"] = "ERROR"
        res["err"] = "Unknown command: "..req["type"]

        return res
    end,
}

function process_request (req)
    if request_handlers[req["type"]] then
        return request_handlers[req["type"]](req)
    else
        return request_handlers["default"](req)
    end
end

-- Receive data from AP client and send message back
function send_receive ()
    local message, err = client_socket:receive()

    -- Handle errors
    if err == "closed" then
        if current_state == STATE_CONNECTED then
            print("Connection to client closed")
        end
        current_state = STATE_NOT_CONNECTED
        return
    elseif err == "timeout" then
        unlock()
        return
    elseif err ~= nil then
        print(err)
        current_state = STATE_NOT_CONNECTED
        unlock()
        return
    end

    -- Reset timeout timer
    timeout_timer = 5

    -- Process received data
    if DEBUG then
        print("Received Message ["..emu.framecount().."]: "..'"'..message..'"')
    end

    if message == "VERSION" then
        client_socket:send(tostring(SCRIPT_VERSION).."\n")
    else
        local res = {}
        local data = json.decode(message)
        local failed_guard_response = nil
        for i, req in ipairs(data) do
            if failed_guard_response ~= nil then
                res[i] = failed_guard_response
            else
                -- An error is more likely to cause an NLua exception than to return an error here
                local status, response = pcall(process_request, req)
                if status then
                    res[i] = response

                    -- If the GUARD validation failed, skip the remaining commands
                    if response["type"] == "GUARD_RESPONSE" and not response["value"] then
                        failed_guard_response = response
                    end
                else
                    if type(response) ~= "string" then response = "Unknown error" end
                    res[i] = {type = "ERROR", err = response}
                end
            end
        end

        client_socket:send(json.encode(res).."\n")
    end
end

function initialize_server ()
    local err
    local port = SOCKET_PORT_FIRST
    local res = nil

    server, err = socket.socket.tcp4()
    while res == nil and port <= SOCKET_PORT_LAST do
        res, err = server:bind("localhost", port)
        if res == nil and err ~= "address already in use" then
            print(err)
            return
        end

        if res == nil then
            port = port + 1
        end
    end

    if port > SOCKET_PORT_LAST then
        print("Too many instances of connector script already running. Exiting.")
        return
    end

    res, err = server:listen(0)

    if err ~= nil then
        print(err)
        return
    end

    server:settimeout(0)
end

function main ()
    while true do
        if server == nil then
            initialize_server()
        end

        current_time = socket.socket.gettime()
        timeout_timer = timeout_timer - (current_time - prev_time)
        message_timer = message_timer - (current_time - prev_time)
        prev_time = current_time

        if message_timer <= 0 and not message_queue:is_empty() then
            gui.addmessage(message_queue:shift())
            message_timer = message_interval
        end

        if current_state == STATE_NOT_CONNECTED then
            if emu.framecount() % 30 == 0 then
                print("Looking for client...")
                local client, timeout = server:accept()
                if timeout == nil then
                    print("Client connected")
                    current_state = STATE_CONNECTED
                    client_socket = client
                    server:close()
                    server = nil
                    client_socket:settimeout(0)
                end
            end
        else
            repeat
                send_receive()
            until not locked

            if timeout_timer <= 0 then
                print("Client timed out")
                current_state = STATE_NOT_CONNECTED
            end
        end

        if acww_time_form ~= nil then
            acww_refresh_form_labels()
            acww_update_specimen_dropdown(false)
        end
        draw_persistent_overlay()
        draw_acww_notification()
        coroutine.yield()
    end
end

event.onexit(function ()
    acww_destroy_time_form()
    print("\n-- Restarting Script --\n")
    if server ~= nil then
        server:close()
    end
end)

if bizhawk_major < 2 or (bizhawk_major == 2 and bizhawk_minor < 7) then
    print("Must use BizHawk 2.7.0 or newer")
else
    if bizhawk_major > 2 or (bizhawk_major == 2 and bizhawk_minor > 10) then
        print("Warning: This version of BizHawk is newer than this script. If it doesn't work, consider downgrading to 2.10.")
    end

    if emu.getsystemid() == "NULL" then
        print("No ROM is loaded. Please load a ROM.")
        while emu.getsystemid() == "NULL" do
            emu.frameadvance()
        end
    end

    rom_hash = gameinfo.getromhash()

    -- Create the ACWW controller only after SET_ACWW_STATE arrives.
    -- This avoids updating partially initialized .NET form controls.

    print("Waiting for client to connect. This may take longer the more instances of this script you have open at once.\n")

    local co = coroutine.create(main)
    function tick ()
        local status, err = coroutine.resume(co)

        if not status and err ~= "cannot resume dead coroutine" then
            print("\nERROR: "..err)
            print("Consider reporting this crash.\n")
    
            if server ~= nil then
                server:close()
            end

            co = coroutine.create(main)
        end
    end

    -- Gambatte has a setting which can cause script execution to become
    -- misaligned, so for GB and GBC we explicitly set the callback on
    -- vblank instead.
    -- https://github.com/TASEmulators/BizHawk/issues/3711
    if emu.getsystemid() == "GB" or emu.getsystemid() == "GBC" or emu.getsystemid() == "SGB" then
        event.onmemoryexecute(tick, 0x40, "tick", "System Bus")
    else
        event.onframeend(tick)
    end

    while true do
        emu.frameadvance()
    end
end
