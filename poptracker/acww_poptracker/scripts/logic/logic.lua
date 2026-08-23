-- ACWW PopTracker catchability logic
-- Generated from the Archipelago world's availability.py.

function has(code)
    return Tracker:ProviderCountForCode(code) > 0
end

function canCatchBugCommonButterfly()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_september"))
end

function canCatchBugYellowButterfly()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_september"))
end

function canCatchBugTigerButterfly()
    return (
        has("month_march")
        or has("month_april")
        or has("month_may")
        or has("month_june")
        or has("month_july")
        or has("month_august")
        or has("month_september")
    )
end

function hasTigerButterflyResource()
    return has("resource_red_roses")
end

function canCatchBugPeacockButterfly()
    return (
        has("month_march")
        or has("month_april")
        or has("month_may")
        or has("month_june")
        or has("month_july")
        or has("month_august")
        or has("month_september")
    )
end

function hasPeacockButterflyResource()
    return (
        has("resource_black_roses")
        or has("resource_blue_roses")
        or has("resource_purple_roses")
    )
end

function canCatchBugMonarchButterfly()
    return (has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugEmperorButterfly()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugAgriasButterfly()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugBirdwingButterfly()
    return (has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugMoth()
    return (has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugOakSilkMoth()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugHoneybee()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august"))
end

function canCatchBugBee()
    return true
end

function canCatchBugLongLocust()
    return (has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugMigratoryLocust()
    return (has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugMantis()
    return (has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugOrchidMantis()
    return (
        has("month_august")
        or has("month_september")
        or has("month_october")
        or has("month_november")
    )
end

function hasOrchidMantisResource()
    return has("resource_white_roses")
end

function canCatchBugBrownCicada()
    return (has("month_july") or has("month_august"))
end

function canCatchBugRobustCicada()
    return (has("month_july") or has("month_august"))
end

function canCatchBugWalkerCicada()
    return (has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugEveningCicada()
    return (has("month_july") or has("month_august"))
end

function canCatchBugLanternFly()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugRedDragonfly()
    return (has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugDarnerDragonfly()
    return (has("month_june") or has("month_july") or has("month_august"))
end

function canCatchBugBandedDragonfly()
    return (has("month_july") or has("month_august"))
end

function canCatchBugAnt()
    return true
end

function hasAntResource()
    return has("resource_spoiled_turnips")
end

function canCatchBugPondskater()
    return (has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugSnail()
    return (has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugCricket()
    return (has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugBellCricket()
    return (has("month_september") or has("month_october"))
end

function canCatchBugGrasshopper()
    return (has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugMoleCricket()
    return (has("month_january") or has("month_february") or has("month_march") or has("month_april") or has("month_may") or has("month_november") or has("month_december"))
end

function canCatchBugWalkingstick()
    return (has("month_july") or has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugLadybug()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_october"))
end

function canCatchBugFruitBeetle()
    return (has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugScarabBeetle()
    return (has("month_july") or has("month_august"))
end

function canCatchBugDungBeetle()
    return (has("month_january") or has("month_february") or has("month_december"))
end

function canCatchBugGoliathBeetle()
    return (
        has("month_june")
        or has("month_july")
        or has("month_august")
        or has("month_september")
    )
end

function hasCoconutResource()
    return has("resource_coconut")
end

function canCatchBugFirefly()
    return (has("month_june"))
end

function canCatchBugJewelBeetle()
    return (has("month_july") or has("month_august"))
end

function canCatchBugLonghornBeetle()
    return (has("month_june") or has("month_july") or has("month_august"))
end

function canCatchBugSawStagBeetle()
    return (has("month_july") or has("month_august"))
end

function canCatchBugStagBeetle()
    return (has("month_june") or has("month_july") or has("month_august"))
end

function canCatchBugGiantBeetle()
    return (has("month_july") or has("month_august"))
end

function canCatchBugRainbowStagBeetle()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugDynastidBeetle()
    return (has("month_july") or has("month_august"))
end

function canCatchBugAtlasBeetle()
    return (
        has("month_june")
        or has("month_july")
        or has("month_august")
    )
end

function canCatchBugElephantBeetle()
    return (
        has("month_june")
        or has("month_july")
        or has("month_august")
    )
end

function canCatchBugHerculesBeetle()
    return (
        has("month_june")
        or has("month_july")
        or has("month_august")
    )
end

function canCatchBugFlea()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugPillBug()
    return true
end

function canCatchBugMosquito()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchBugFly()
    return true
end

function hasFlyResource()
    return has("resource_spoiled_turnips")
end

function canCatchBugCockroach()
    return true
end

function canCatchBugSpider()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchBugTarantula()
    return (has("month_june") or has("month_july") or has("month_august"))
end

function canCatchBugScorpion()
    return (has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishBitterling()
    return (has("month_january") or has("month_february") or has("month_november") or has("month_december"))
end

function canCatchFishPaleChub()
    return true
end

function canCatchFishCrucianCarp()
    return true
end

function canCatchFishDace()
    return true
end

function canCatchFishBarbelSteed()
    return true
end

function canCatchFishCarp()
    return true
end

function canCatchFishKoi()
    return true
end

function canCatchFishGoldfish()
    return true
end

function canCatchFishPopeyedGoldfish()
    return true
end

function canCatchFishKillifish()
    return (has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august"))
end

function canCatchFishCrawfish()
    return (has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishFrog()
    return (has("month_may") or has("month_june") or has("month_july") or has("month_august"))
end

function canCatchFishFreshwaterGoby()
    return true
end

function canCatchFishLoach()
    return (has("month_march") or has("month_april") or has("month_may"))
end

function canCatchFishCatfish()
    return (has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september") or has("month_october"))
end

function canCatchFishEel()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishGiantSnakehead()
    return (has("month_june") or has("month_july") or has("month_august"))
end

function canCatchFishBluegill()
    return true
end

function canCatchFishYellowPerch()
    return (has("month_january") or has("month_february") or has("month_march") or has("month_october") or has("month_november") or has("month_december"))
end

function canCatchFishBlackBass()
    return true
end

function canCatchFishPondSmelt()
    return (has("month_january") or has("month_february") or has("month_december"))
end

function canCatchFishSweetfish()
    return (has("month_july") or has("month_august"))
end

function canCatchFishCherrySalmon()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchFishChar()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchFishRainbowTrout()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchFishStringfish()
    return (has("month_january") or has("month_february") or has("month_december"))
end

function canCatchFishSalmon()
    return (has("month_september"))
end

function canCatchFishKingSalmon()
    return (has("month_september"))
end

function canCatchFishGuppy()
    return (has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchFishAngelfish()
    return (has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september") or has("month_october"))
end

function canCatchFishPiranha()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishArowana()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishDorado()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishGar()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishArapaima()
    return (has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishSeaButterfly()
    return (has("month_january") or has("month_february") or has("month_december"))
end

function canCatchFishJellyfish()
    return (has("month_august"))
end

function canCatchFishSeahorse()
    return (has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchFishClownfish()
    return (has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishZebraTurkeyfish()
    return (has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchFishPufferfish()
    return (has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishHorseMackerel()
    return true
end

function canCatchFishBarredKnifejaw()
    return (has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_september") or has("month_october") or has("month_november"))
end

function canCatchFishSeaBass()
    return true
end

function canCatchFishRedSnapper()
    return true
end

function canCatchFishDab()
    return (has("month_january") or has("month_february") or has("month_march") or has("month_april") or has("month_october") or has("month_november") or has("month_december"))
end

function canCatchFishOliveFlounder()
    return true
end

function canCatchFishSquid()
    return (has("month_january") or has("month_february") or has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_august") or has("month_december"))
end

function canCatchFishOctopus()
    return (has("month_january") or has("month_march") or has("month_april") or has("month_may") or has("month_june") or has("month_july") or has("month_september") or has("month_october") or has("month_november") or has("month_december"))
end

function canCatchFishFootballFish()
    return (has("month_january") or has("month_february") or has("month_march") or has("month_november") or has("month_december"))
end

function canCatchFishTuna()
    return (has("month_january") or has("month_february") or has("month_march") or has("month_november") or has("month_december"))
end

function canCatchFishBlueMarlin()
    return (has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishOceanSunfish()
    return (has("month_june") or has("month_july") or has("month_august"))
end

function canCatchFishHammerheadShark()
    return (has("month_june") or has("month_july") or has("month_august"))
end

function canCatchFishShark()
    return (has("month_june") or has("month_july") or has("month_august") or has("month_september"))
end

function canCatchFishCoelacanth()
    return true
end
