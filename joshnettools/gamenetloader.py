import networkx as nx
import numpy as np
import numpy.typing as npt
import pandas as pd
import logging
from typing import Optional
from pathlib import Path

# Shrink the network by removing everyone who doesn't appear as frequently
# as this value.
DEFAULT_N_FREQUENCY: int = 3


def shrink_network_by(
    gamers_df: pd.DataFrame, n_freq: int = DEFAULT_N_FREQUENCY
) -> pd.DataFrame:
    """Remove nodes that appear less than n_freq.

    Parameters
    ----------
    gamers_df: pandas.DataFrame
        Gamers network as a DataFrame.
    n_freq: int
        Positive integer by which to shrink the network. Defaults to 3.

    Returns
    -------
    gamers_df: pandas.DataFrame
        Filtered copy of gamers_df.
    """
    logging.info(f"Shrinking network to authors that appear {n_freq} times.")
    # This could be a one liner, but Python looks a bit messy like that.
    # I'm filtering for authors who appear at least as much as n_freq
    mask: pd.Series = gamers_df.author.value_counts() >= n_freq
    freq_auths: npt.NDArray[np.str_] = gamers_df.author.value_counts()[mask].index
    return gamers_df.loc[gamers_df.author.isin(freq_auths)]


def load_network(path: str | Path, n_freq: int = DEFAULT_N_FREQUENCY) -> pd.DataFrame:
    """Loads and processes gamers network from path.

    Parameters
    ----------
    path: str | Path
        Path to network.
    n_freq: int, optional
        Filter out posters who appear less than n_freq.
        The default is DEFAULT_N_FREQUENCY (3).

    Returns
    -------
    gamers: pandas.DataFrame
        DataFrame of processed gamers network.
    """
    logging.info(f"Loading network data from {path}")
    gamers: pd.DataFrame = pd.read_csv(path, engine="pyarrow")
    gamers = shrink_network_by(gamers, n_freq)

    # ======================================
    # Systems, games, and general subreddits
    # ======================================
    game_subs: list[str] = [
        "DarkSouls2",
        "KingdomHearts",
        "darksouls",
        "fireemblem",
        "MonsterHunter",
        "Doom",
        "bloodborne",
        "DevilMayCry",
        "darksouls3",
        "pokemon",
        "halo",
        "yakuzagames",
        "Fallout",
        "DestinyTheGame",
        "metalgearsolid",
        "skyrim",
        "MonsterHunterWorld",
        "demonssouls",
        "wow",
        "Minecraft",
        "Overwatch",
        "GlobalOffensive",
        "leagueoflegends",
        "zelda",
        "AnimalCrossing",
        "witcher",
        "PUBATTLEGROUNDS",
        "SEGA",
        "smashbros",
        "RocketLeague",
        "FallGuysGame",
        "StardewValley",
        "DotA2",
    ]

    sys_subs: list[str] = [
        "psx",
        "PS3",
        "ps2",
        "pcmasterrace",
        "nintendo",
        "xboxone",
        "pcgaming",
        "PS4",
        "Steam",
        "buildapc",
        "NintendoSwitch",
        "PS5",
        "XboxSeriesX",
        "3DS",
        "xbox",
        "xbox360",
    ]

    gen_subs: list[str] = [
        "JRPG",
        "gamedesign",
        "linux_gaming",
        "otomegames",
        "boardgames",
        "emulation",
        "Games",
        "gaming",
        "GamePhysics",
        "rpg",
        "truegaming",
        "ShouldIbuythisgame",
        "FreeGamesOnSteam",
        "IndieGaming",
    ]

    # VGames avoids clashes with Games
    gamers.loc[gamers.subreddit.isin(game_subs), "SysGamGen"] = "VGames"
    gamers.loc[gamers.subreddit.isin(sys_subs), "SysGamGen"] = "Systems"
    gamers.loc[gamers.subreddit.isin(gen_subs), "SysGamGen"] = "General"
    # Colors for SysGamGem
    # Stolen from: https://github.com/morhetz/gruvbox-contrib
    gamers.loc[gamers.subreddit.isin(game_subs), "SysGamGen_col"] = "#cc241d"
    gamers.loc[gamers.subreddit.isin(sys_subs), "SysGamGen_col"] = "#458588"
    gamers.loc[gamers.subreddit.isin(gen_subs), "SysGamGen_col"] = "#b16286"

    # =========================================================
    # Subreddits reasonably associated with a company/system/PC
    # =========================================================

    # The Yakuzas are recently being ported to PC, but I'll add it to Sony
    # for now anyway.
    sony_subs: list[str] = [
        "psx",
        "ps2",
        "PS3",
        "PS4",
        "PS5",
        "bloodborne",
        "demonssouls",
        "KingdomHearts",
        "yakuzagames",
    ]

    # The Halo Master Chief Collection was ported to PC in 2019.
    # Buuuut the Xbox section seems lonely so I'll include Halo.
    # (This is a limitation based on how I collected the data).
    xbox_subs: list[str] = ["xbox", "xbox360", "xboxone", "XboxSeriesX", "halo"]

    nintendo_subs: list[str] = [
        "nintendo",
        "NintendoSwitch",
        "3DS",
        "fireemblem",
        "pokemon",
        "AnimalCrossing",
        "smashbros",
        "zelda",
    ]

    pc_subs: list[str] = [
        "wow",
        "leagueoflegends",
        "GlobalOffensive",
        "Minecraft",
        "Overwatch",
        "linux_gaming",
        "emulation",
        "Steam",
        "buildapc",
        "pcmasterrace",
        "FreeGamesOnSteam",
        "DotA2",
        "pcgaming",
    ]

    multi_subs: list[str] = [
        "DarkSouls2",
        "darksouls",
        "MonsterHunter",
        "Fallout",
        "DestinyTheGame",
        "skyrim",
        "metalgearsolid",
        "witcher",
        "PUBATTLEGROUNDS",
        "SEGA",
        "RocketLeague",
        "FallGuysGame",
        "StardewValley",
        "otomegames",
        "Doom",
        "DevilMayCry",
        "darksouls3",
        "JRPG",
        "rpg",
        "IndieGaming",
        "MonsterHunterWorld",
    ]

    nonsys_subs: list[str] = [
        "gamedesign",
        "boardgames",
        "Games",
        "gaming",
        "GamePhysics",
        "truegaming",
        "ShouldIbuythisgame",
    ]

    gamers.loc[gamers.subreddit.isin(sony_subs), "Systems"] = "Sony"
    gamers.loc[gamers.subreddit.isin(xbox_subs), "Systems"] = "Xbox"
    gamers.loc[gamers.subreddit.isin(nintendo_subs), "Systems"] = "Nintendo"
    gamers.loc[gamers.subreddit.isin(pc_subs), "Systems"] = "PC"
    gamers.loc[gamers.subreddit.isin(multi_subs), "Systems"] = "Multi"
    gamers.loc[gamers.subreddit.isin(nonsys_subs), "Systems"] = "NonSys"

    return gamers


def load(path: Optional[str | Path] = None) -> pd.DataFrame:
    """Load gamer network from path if specified or try alternative paths.

    Parameters
    ----------
    path: str | Path, optional
        Path to gamers_reddit_medium_2020.csv.

    Returns
    -------
    pandas.DataFrame
        Loaded gamer network.
    """
    # Try the data directory if !path
    if not path:
        try:
            logging.info("Trying to load data from disk")
            path = (
                Path(__file__)
                .parent.resolve()
                .joinpath("data", "gamers_reddit_medium_2020.csv")
            )
        # Catch FileNotFoundError in order to try GitHub next.
        except FileNotFoundError:
            logging.warning("Loading data from GitHub")
            path = "https://github.com/joshuamegnauth54/GamerDistributionThesis2020/raw/master/data/gamers_reddit_medium_2020.csv"

    return load_network(path)
