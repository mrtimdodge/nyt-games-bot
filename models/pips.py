import statistics as stats
from data.base_data_handler import BaseDatabaseHandler
from models.base_game import BasePlayerStats, BasePuzzleEntry
import pandas as pd

class PipsPlayerStats(BasePlayerStats):
    # pips-specific stats
    avg_easy_seconds: float
    avg_medium_seconds: float
    avg_hard_seconds: float
    easy_cookie_rate:float
    medium_cookie_rate:float
    hard_cookie_rate:float
    avg_total_seconds: float


    def __init__(self, user_id: str, puzzle_list: list[int], db: BaseDatabaseHandler) -> None:
        self.user_id = user_id

        player_puzzles = db.get_puzzles_by_player(self.user_id)
        player_entries: list[PipsPuzzleEntry] = db.get_entries_by_player(self.user_id, puzzle_list)

        self.missed_games = len([p for p in puzzle_list if p not in player_puzzles])

        if len(player_entries) > 0:
            easy_entries = [e for e in player_entries if e.easy_seconds != None]
            medium_entries = [e for e in player_entries if e.medium_seconds != None]
            hard_entries = [e for e in player_entries if e.hard_seconds != None]
            self.avg_easy_seconds = stats.mean([e.easy_seconds for e in easy_entries] if len(easy_entries) > 0 else [-1.0])
            self.avg_medium_seconds = stats.mean([e.medium_seconds for e in medium_entries] if len(medium_entries) > 0 else [-1.0])
            self.avg_hard_seconds = stats.mean([e.hard_seconds for e in hard_entries] if len(hard_entries) > 0 else [-1.0])

            self.easy_cookie_rate = stats.mean([1.0 if e.easy_cookie else 0.0 for e in easy_entries] if len(easy_entries) > 0 else [-1.0])
            self.medium_cookie_rate = stats.mean([1.0 if e.medium_cookie else 0.0 for e in medium_entries] if len(medium_entries) > 0 else [-1.0])
            self.hard_cookie_rate = stats.mean([1.0 if e.hard_cookie else 0.0 for e in hard_entries] if len(hard_entries) > 0 else [-1.0])

            avg_total_entries = [e for e in player_entries if e.easy_seconds != None and e.medium_seconds != None and e.hard_seconds != None]

            self.avg_total_seconds = stats.mean([e.easy_seconds + e.medium_seconds + e.hard_seconds for e in avg_total_entries] if len(avg_total_entries) > 0 else [-1.0])
        else:
            self.avg_easy_seconds = -1.0
            self.avg_medium_seconds = -1.0
            self.avg_hard_seconds = -1.0

            self.easy_cookie_rate = -1.0
            self.medium_cookie_rate = -1.0
            self.hard_cookie_rate = -1.0

            self.avg_total_seconds = -1.0
        self.rank = -1

    def get_stat_list(self) -> tuple[float, float, float, float, float, float, float]:
        return self.avg_easy_seconds, self.avg_medium_seconds, self.avg_hard_seconds, self.easy_cookie_rate, self.medium_cookie_rate, self.hard_cookie_rate, self.avg_total_seconds

class PipsPuzzleEntry(BasePuzzleEntry):
    # pips-specific details
    easy_seconds:int
    medium_seconds:int
    hard_seconds:int
    easy_cookie:bool
    medium_cookie:bool
    hard_cookie:bool


    def __init__(self, puzzle_id: int, user_id: str, easy_seconds:int, medium_seconds:int, hard_seconds:int,
                  easy_cookie:bool, medium_cookie:bool, hard_cookie:bool) -> None:
        self.puzzle_id = puzzle_id
        self.user_id = user_id
        self.easy_seconds = easy_seconds
        self.medium_seconds = medium_seconds
        self.hard_seconds = hard_seconds
        self.easy_cookie = easy_cookie
        self.medium_cookie = medium_cookie
        self.hard_cookie = hard_cookie