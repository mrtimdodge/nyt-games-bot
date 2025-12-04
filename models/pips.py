import statistics as stats
from data.base_data_handler import BaseDatabaseHandler
from models.base_game import BasePlayerStats, BasePuzzleEntry

# class PipsPlayerStats(BasePlayerStats):
#     # strands-specific stats
#     avg_hints: float
#     avg_spangram_index: float
#     avg_rating_raw: float
#     avg_rating_adj: float

#     def __init__(self, user_id: str, puzzle_list: list[int], db: BaseDatabaseHandler) -> None:
#         self.user_id = user_id

#         player_puzzles = db.get_puzzles_by_player(self.user_id)
#         player_entries: list[PipsPuzzleEntry] = db.get_entries_by_player(self.user_id, puzzle_list)

#         self.missed_games = len([p for p in puzzle_list if p not in player_puzzles])

#         if len(player_entries) > 0:
#             self.avg_hints = stats.mean([e.hints for e in player_entries])
#             self.avg_spangram_index = stats.mean([e.spangram_index for e in player_entries if e.spangram_index > 0])
#             self.avg_rating_raw = stats.mean([e.rating for e in player_entries])
#             self.avg_rating_adj = stats.mean([e.rating for e in player_entries] + ([2.0] * self.missed_games))
#         else:
#             self.avg_hints = 0.0
#             self.avg_spangram_index = 0.0
#             self.avg_rating_raw = 0.0
#             self.avg_rating_adj = 0.0
#         self.rank = -1

#     def get_stat_list(self) -> tuple[float, float, float, float]:
#         return self.avg_rating_raw, self.avg_rating_adj, self.avg_hints, self.avg_spangram_index

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