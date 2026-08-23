ENABLE_DEBUG_LOG = true

ScriptHost:LoadScript("scripts/logic/logic.lua")

Tracker:AddItems("items/items.json")
Tracker:AddMaps("maps/maps.json")
Tracker:AddLocations("locations/locations.json")

if string.find(Tracker.ActiveVariantUID, "a_standard") then
    Tracker:AddLayouts("layouts/items.json")
    Tracker:AddLayouts("layouts/museum_overview.json")
    Tracker:AddLayouts("layouts/bug_donations.json")
    Tracker:AddLayouts("layouts/fish_donations.json")
    Tracker:AddLayouts("layouts/tracker.json")
end

print("ACWW PopTracker loaded")

if PopVersion and PopVersion >= "0.18.0" then
    ScriptHost:LoadScript("scripts/autotracking.lua")
end
