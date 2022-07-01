# Subreddit colors
from typing import Union

# I looked up the hex colors associated with some of these. For example,
# I gave Goofy's orange to Kingdom Hearts. Other subs were given colors
# somewhat randomly. Also, I'm well aware that I can just set a palette.
__sub_colors = {
    "DevilMayCry": "#ff5555",
    "bloodborne": "#ff0066",
    "MonsterHunter": "#3bd1ff",
    "emulation": "#26ff4a",
    "KingdomHearts": "#f58221",
    "psx": "#df0024",
    "xbox360": "#0e7a0d",
    "yakuzagames": "#d5a08b",
    "smashbros": "#e0f0ff",
    "Fallout": "#fef265",
    "ps2": "#00ac9f",
    "metalgearsolid": "#76858f",
    "PS3": "#665cbe",
    "buildapc": "#5d00ff",
    "MonsterHunterWorld": "#70faff",
    "otomegames": "#ff79c6",
    "xboxone": "#3a3a3a",
    "Doom": "#b45e33",
    "SEGA": "#1c61ac",
    "RocketLeague": "#e97451",
    "pokemon": "#ffcb05",
    "FallGuysGame": "#f1fa8c",
    "PUBATTLEGROUNDS": "#542d1a",
    "nintendo": "#e60012",
    "fireemblem": "#dc143c",
    "Minecraft": "#8fca5c",
    "rpg": "#808284",
    "PS4": "#003087",
    "xbox": "#107c10",
    "gamedesign": "#b80006",
    "linux_gaming": "#54487a",
    "zelda": "#d4ce46",
    "leagueoflegends": "#ff8300",
    "DotA2": "#a72714",
    "pcgaming": "#bd93f9",
    "halo": "#65684c",
    "pcmasterrace": "#7f90b8",
    "demonssouls": "#d4ac2b",
    "JRPG": "#e788da",
    "DarkSouls2": "#981f5c",
    "Steam": "#2a475e",
    "PS5": "#000000",
    "darksouls3": "#aa0e30",
    "DestinyTheGame": "#f0ead0",
    "FreeGamesOnSteam": "#c7d5e0",
    "ShouldIbuythisgame": "#64ce77",
    "IndieGaming": "#8be9fd",
    "NintendoSwitch": "#ff4554",
    "XboxSeriesX": "#7fba00",
    "Overwatch": "#f99e1a",
    "boardgames": "#c73032",
    "witcher": "#586384",
    "Games": "#0137da",
    "truegaming": "#da0110",
    "3DS": "#fe717a",
    "darksouls": "#fed471",
    "StardewValley": "#70c725",
    "GlobalOffensive": "#ccba7c",
    "AnimalCrossing": "#9dffb0",
    "gaming": "#81f1f7",
    "GamePhysics": "#c48d3f",
    "skyrim": "#44475a",
    "wow": "#69ccf0",
    "multiple_subs": "#ffb86c",
    None: "#8b4513",
    "Systems": "#ff79c6",
    "VGames": "#50fa7b",
    "General": "#8be9fd",
    "Sony": "#0112fe",
    "Xbox": "#107c10",
    "Nintendo": "#e60012",
    "PC": "#bd93f9",
    "Multi": "#ffb86c",
    "NonSys": "#f1fa8c",
}


# Yes, this function is misnamed.
def subreddit_colors(subreddit: Union[set, list, str]) -> str:
    """Return a color based on an attribute or subreddit.

    Parameters
    ----------
    subreddit: Union[set, list, str]
        A subreddit or list of subreddits.

    Returns
    -------
    str
        Hex color.
    """
    if isinstance(subreddit, (set, list)) & len(subreddit):
        return (
            __sub_colors["multiple_subs"]
            if len(subreddit) > 1
            else __sub_colors[subreddit.pop()]
        )
    elif isinstance(subreddit, str):
        return __sub_colors[subreddit]
    else:
        return __sub_colors[None]
