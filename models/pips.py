import os
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
    score: float

    EASY_COOKIE_TIME = 20
    MEDIUM_COOKIE_TIME = 40
    HARD_COOKIE_TIME = 60

    MAX_TIME_MULTIPLIER = float(os.getenv("MAX_TIME_MULTIPLIER", 12.0))
    MIN_SCORE_FOR_COMPLETION = float(os.getenv("MIN_SCORE_FOR_COMPLETION", 10.0))

    EASY_MULTIPLIER = float(os.getenv("EASY_MULTIPLIER", 1.0))
    MEDIUM_MULTIPLIER = float(os.getenv("MEDIUM_MULTIPLIER", 1.5))
    HARD_MULTIPLIER = float(os.getenv("HARD_MULTIPLIER", 2.0))
    COMPLETION_BONUS = float(os.getenv("COMPLETION_BONUS", 5.0))


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

            self.score = sum([self.get_entry_score(e) for e in player_entries])
            self.avg_score = self.score / len(player_entries)
            self.rank_score = self.avg_score + self.COMPLETION_BONUS * len(player_entries)
        else:
            self.avg_easy_seconds = -1.0
            self.avg_medium_seconds = -1.0
            self.avg_hard_seconds = -1.0

            self.easy_cookie_rate = -1.0
            self.medium_cookie_rate = -1.0
            self.hard_cookie_rate = -1.0

            self.avg_total_seconds = -1.0
            self.score = 0.0
            self.avg_score = 0.0
            self.rank_score = 0.0
        self.rank = -1

    def get_stat_list(self) -> tuple[float, float, float, float, float, float, float]:
        return self.avg_easy_seconds, self.avg_medium_seconds, self.avg_hard_seconds, self.easy_cookie_rate, self.medium_cookie_rate, self.hard_cookie_rate, self.avg_total_seconds
    
    ####################
    #  Util Methods    #
    ####################

    def get_entry_score(self, entry) -> float:
        total_score = 0.0

        if entry.easy_seconds is not None:
            total_score += self.get_score(entry.easy_seconds, 'easy') * self.EASY_MULTIPLIER
        if entry.medium_seconds is not None:
            total_score += self.get_score(entry.medium_seconds, 'medium') * self.MEDIUM_MULTIPLIER
        if entry.hard_seconds is not None:
            total_score += self.get_score(entry.hard_seconds, 'hard') * self.HARD_MULTIPLIER

        return total_score 


    def get_score(self, time, level) -> float: 
        if level == 'easy':
            cookie_time = self.EASY_COOKIE_TIME
        elif level == 'medium':
            cookie_time = self.MEDIUM_COOKIE_TIME
        elif level == 'hard':
            cookie_time = self.HARD_COOKIE_TIME
        else: 
            return 0

        max_time = cookie_time * self.MAX_TIME_MULTIPLIER
        score = 0.0
        
        if time <= cookie_time:
            score = 100.0
        else:
            score = max(self.MIN_SCORE_FOR_COMPLETION, 100.0 - ((time) / (max_time)) * 100.0)


        return score


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