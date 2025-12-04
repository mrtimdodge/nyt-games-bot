import os, re
from datetime import date
from data.base_data_handler import BaseDatabaseHandler
from models.pips import PipsPuzzleEntry
from utils.bot_utilities import BotUtilities
from enum import Enum, auto


class PipsLevel(Enum):
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    UNKNOWN = 'unknown'

class PipsDatabaseHandler(BaseDatabaseHandler):
    def __init__(self, utils: BotUtilities) -> None:
        # init
        super().__init__(utils)

        # puzzles
        self._arbitrary_date = date(2025, 12, 4)
        self._arbitrary_date_puzzle = 109

        # mysql connection
        self._mysql_host = os.environ.get('PIPS_MYSQL_HOST', None)
        self._mysql_user = os.environ.get('PIPS_MYSQL_USER', "root")
        self._mysql_pass = os.environ.get('PIPS_MYSQL_PASS', "")
        self._mysql_db_name = os.environ.get('PIPS_MYSQL_DB_NAME', "pips")

    ####################
    #  PUZZLE METHODS  #
    ####################

    def add_entry(self, user_id: str, title: str, puzzle: str) -> bool:
        puzzle_id_title = re.findall(r'[\d,]+', title)
        cookie = puzzle.find('🍪') != -1
        level = self.__get_level_from_title(title).value
        seconds = self.__mm_ss_to_seconds(puzzle.replace('🍪', '').strip())

        if(level == PipsLevel.UNKNOWN.value):
            return False

        if puzzle_id_title:
            puzzle_id = int(str(puzzle_id_title[0]).replace(',', ''))
        else:
            return False

        if not self._db.is_connected():
            self.connect()

        if not self.user_exists(user_id):
            user_name = self._utils.get_nickname(user_id)
            self._cur.execute("insert into users (user_id, name) values ('{}', '{}')".format(user_id, user_name))

        if self.entry_exists(user_id, puzzle_id):
            self._cur.execute(
                f"update entries set {level}_cookie = {cookie}, {level}_seconds = {seconds} "
                    + f"where user_id = '{user_id}' and puzzle_id = '{puzzle_id}'"
            )
            self._db.commit()
            return True
        else:
            self._cur.execute(
                f"insert into entries (puzzle_id, user_id, {level}_cookie, {level}_seconds) "
                    + f"values ({puzzle_id}, {user_id}, {cookie}, {seconds})"
            )
            self._db.commit()
            return self._cur.rowcount > 0

    ####################
    #  PLAYER METHODS  #
    ####################

    def get_entries_by_player(self, user_id: str, puzzle_list: list[int] = []) -> list[PipsPuzzleEntry]:
        if not self._db.is_connected():
            self.connect()
        if not puzzle_list or len(puzzle_list) == 0:
            query = f"select puzzle_id, easy_seconds, medium_seconds, hard_seconds, easy_cookie, medium_cookie, hard_cookie from entries where user_id = {user_id}"
        else:
            puzzle_list_str = ','.join([str(p_id) for p_id in puzzle_list])
            query = f"select puzzle_id, easy_seconds, medium_seconds, hard_seconds, easy_cookie, medium_cookie, hard_cookie from entries where user_id = {user_id} and puzzle_id in ({puzzle_list_str})"
        self._cur.execute(query)
        entries: list[PipsPuzzleEntry] = []
        for row in self._cur.fetchall():
            entries.append(PipsPuzzleEntry(row[0], user_id, row[1], row[2], row[3], row[4], row[5], row[6]))
        return entries
    
    ####################
    #  HELPER METHODS  #
    ####################

    def __get_level_from_title(self, title: str) -> PipsLevel:
        if 'easy' in title.lower():
            return PipsLevel.EASY
        elif 'medium' in title.lower():
            return PipsLevel.MEDIUM
        elif 'hard' in title.lower():
            return PipsLevel.HARD
        else:         
            return PipsLevel.UNKNOWN
    
    def __mm_ss_to_seconds(self, time_string):
        """
        Converts a time string in "MM:SS" format to total seconds.

        Args:
            time_string (str): The time string in "MM:SS" format.

        Returns:
            int: The total number of seconds.
        """
        try:
            minutes_str, seconds_str = time_string.split(':')
            minutes = int(minutes_str)
            seconds = int(seconds_str)
            total_seconds = (minutes * 60) + seconds
            return total_seconds
        except ValueError:
            print(F"Error: Invalid time string {time_string}. Please use 'MM:SS'.")
            return None