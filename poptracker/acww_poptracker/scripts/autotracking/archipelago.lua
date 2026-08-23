ScriptHost:LoadScript("scripts/autotracking/item_mapping.lua")
ScriptHost:LoadScript("scripts/autotracking/location_mapping.lua")

Tracker.AllowDeferredLogicUpdate = false

CURRENT_ITEM_INDEX = -1

local OVERVIEW_CODES = {
    bugs = "museum_progress_bugs",
    fish = "museum_progress_fish",
    fossils = "museum_progress_fossils",
    art = "museum_progress_art",
}

local completed_counts = {
    bugs = 0,
    fish = 0,
    fossils = 0,
    art = 0,
}

local function set_overview_stage(category, count)
    local code = OVERVIEW_CODES[category]
    local object = Tracker:FindObjectForCode(code)

    if object then
        object.CurrentStage = count
    end
end

local function reset_overview()
    completed_counts.bugs = 0
    completed_counts.fish = 0
    completed_counts.fossils = 0
    completed_counts.art = 0

    set_overview_stage("bugs", 0)
    set_overview_stage("fish", 0)
    set_overview_stage("fossils", 0)
    set_overview_stage("art", 0)
end

local function reset_locations()
    for _, paths in pairs(LOCATION_MAPPING) do
        for _, path in ipairs(paths) do
            local object = Tracker:FindObjectForCode(path)

            if object then
                object.AvailableChestCount = object.ChestCount
            end
        end
    end
end

local function reset_items()
    for _, mapping in pairs(ITEM_MAPPING) do
        local code = mapping[1]
        local kind = mapping[2]
        local object = Tracker:FindObjectForCode(code)

        if object then
            if kind == "toggle" then
                object.Active = false
            elseif kind == "progressive" then
                object.CurrentStage = 0
                object.Active = true
            end
        end
    end
end

function onClear(slotData)
    Tracker.BulkUpdate = true
    CURRENT_ITEM_INDEX = -1

    reset_locations()
    reset_items()
    reset_overview()

    Tracker.BulkUpdate = false
end

function onItem(index, itemId, itemName, playerNumber)
    if index <= CURRENT_ITEM_INDEX then
        return
    end

    CURRENT_ITEM_INDEX = index

    local mapping = ITEM_MAPPING[itemId]
    if not mapping then
        return
    end

    local code = mapping[1]
    local kind = mapping[2]
    local object = Tracker:FindObjectForCode(code)

    if not object then
        print("ACWW PopTracker: item object not found for " .. code)
        return
    end

    if kind == "toggle" then
        object.Active = true
    elseif kind == "progressive" then
        object.Active = true

        local nextStage = object.CurrentStage + 1

        if nextStage > 2 then
            nextStage = 2
        end

        object.CurrentStage = nextStage
    end
end

local function update_overview_for_location(locationId)
    local category = nil

    if locationId >= 2000 and locationId <= 2055 then
        category = "bugs"
    elseif locationId >= 2100 and locationId <= 2155 then
        category = "fish"
    elseif locationId >= 2200 and locationId <= 2251 then
        category = "fossils"
    elseif locationId >= 2300 and locationId <= 2319 then
        category = "art"
    end

    if category then
        completed_counts[category] = completed_counts[category] + 1
        set_overview_stage(category, completed_counts[category])
    end
end

function onLocation(locationId, locationName)
    local paths = LOCATION_MAPPING[locationId]

    if paths then
        for _, path in ipairs(paths) do
            local object = Tracker:FindObjectForCode(path)

            if object and object.AvailableChestCount > 0 then
                object.AvailableChestCount =
                    object.AvailableChestCount - 1
            end
        end
    end

    update_overview_for_location(locationId)
end

Archipelago:AddClearHandler("ACWW Clear", onClear)
Archipelago:AddItemHandler("ACWW Item", onItem)
Archipelago:AddLocationHandler("ACWW Location", onLocation)
