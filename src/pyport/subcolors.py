# Subreddit colors
from typing import Set, List

__sub_colors = {}

def subreddit_colors(subreddit):
    if isinstance(subreddit, (Set, List)):
        return __sub_colors["multiple_subs"]\
            if len(subreddit) > 1\
            else __sub_colors[subreddit.pop()]
    elif isinstance(subreddit, str):
        return __sub_colors[subreddit]
