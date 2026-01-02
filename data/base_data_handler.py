from datetime import date
from typing import Protocol
from mysql.connector import MySQLConnection, connect
from mysql.connector.cursor import MySQLCursor
from utils.bot_utilities import BotUtilities

class BaseDatabaseHandler(Protocol):
    _utils: BotUtilities
    _db: MySQLConnection
    _cur: MySQLCursor
    _arbitrary_date: date
    _arbitrary_date_puzzle: int
    _mysql_host: str
    _mysql_user: str
    _mysql_pass: str
    _mysql_db_name: str

    def __init__(self, utils: BotUtilities) -> None:
        self._utils = utils
        self._db = None
        self._cur = None

    ####################
    # ABSTRACT METHODS #
    ####################

    def add_entry(self, user_id: str, title: str, puzzle: str) -> bool:
        pass

    ####################
    #   BASE METHODS   #
    ####################

    def remove_entry(self, user_id: str, puzzle_id: int) -> bool:
        if not self._db.is_connected():
            self.connect()
        self._cur.execute(f"delete from entries where user_id = {user_id} and puzzle_id = {puzzle_id}")
        self._db.commit()
        return self._cur.rowcount > 0

    def user_exists(self, user_id: str) -> bool:
        if not self._db.is_connected():
            self.connect()
        self._cur.execute(f"select * from users where user_id = {user_id}")
        return self._cur.rowcount > 0

    def entry_exists(self, user_id: str, puzzle_id: int) -> bool:
        if not self._db.is_connected():
            self.connect()
        self._cur.execute(f"select * from entries where user_id = {user_id} and puzzle_id = {puzzle_id}")
        return self._cur.rowcount > 0

    def connect(self) -> None:
        if not self._mysql_host:
            raise Exception("Environment variable for MySQL HOST cannot be empty/null")

        self._db = connect(
            host=self._mysql_host,
            user=self._mysql_user,
            password=self._mysql_pass,
            database=self._mysql_db_name
        )
        self._db.autocommit = True
        self._cur = self._db.cursor(buffered=True)

    ####################
    #  PUZZLE METHODS  #
    ####################

    def get_puzzle_by_date(self, query_date: date) -> int:
        return self._arbitrary_date_puzzle + (query_date - self._arbitrary_date).days

    def get_puzzles_by_week(self, query_date: date) -> list[int]:
        if self._utils.is_sunday(query_date):
            sunday_puzzle_id = self.get_puzzle_by_date(query_date)
            return list(range(sunday_puzzle_id, sunday_puzzle_id + 7))
        return []

    def get_puzzles_by_month(self, query_date: date) -> list[int]:
        thirty_day_months = [4, 6, 9, 11]
        thirty_one_day_months = [1, 3, 5, 7, 8, 10, 12]
        days_in_month = 1
        if(query_date.month == self._utils.get_todays_date().month and query_date.year == self._utils.get_todays_date().year ):
            days_in_month = self._utils.get_todays_date().day
        elif query_date.month == 2:
            if (query_date.year % 4 == 0 and query_date.year % 100 != 0) or (query_date.year % 400 == 0):
                days_in_month = 29
            else:
                days_in_month = 28
        elif query_date.month in thirty_day_months:
            days_in_month = 30
        elif query_date.month in thirty_one_day_months:
            days_in_month = 31
        
        if days_in_month > 0:
            first_day = query_date.replace(day=1)
            puzzle_ids = []
            for day in range(days_in_month):
                current_date = first_day.replace(day=day + 1)
                puzzle_ids.append(self.get_puzzle_by_date(current_date))
            return puzzle_ids
        return []
    
    def get_all_puzzles(self) -> list[int]:
        if not self._db.is_connected():
            self.connect()
        self._cur.execute("select distinct puzzle_id from entries")
        return [row[0] for row in self._cur.fetchall()]

    ####################
    #  PLAYER METHODS  #
    ####################

    def get_all_players(self) -> list[str]:
        if not self._db.is_connected():
            self.connect()
        self._cur.execute("select distinct user_id from users")
        return [str(row[0]) for row in self._cur.fetchall()]

    def get_puzzles_by_player(self, user_id) -> list[int]:
        if not self._db.is_connected():
            self.connect()
        self._cur.execute(f"select distinct puzzle_id from entries where user_id = {user_id}")
        return [row[0] for row in self._cur.fetchall()]

    def get_players_by_puzzle_id(self, puzzle_id: int) -> list[str]:
        if not self._db.is_connected():
            self.connect()
        self._cur.execute(f"select distinct user_id from entries where puzzle_id = {puzzle_id}")
        return [str(row[0]) for row in self._cur.fetchall()]

    def get_entries_by_player(self, user_id: str, puzzle_list: list[int] = []) -> list[object]:
        pass
