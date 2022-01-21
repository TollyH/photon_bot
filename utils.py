"""Utility functions provided to make repeated actions easier."""
import collections
from configparser import ConfigParser

import mysql.connector

ExpInfo = collections.namedtuple(
    'ExpInfo', ['exp', 'level', 'remaining', 'rank', 'next_level', 'color']
)
GuildConfig = collections.namedtuple(
    'GuildConfig', [
        "exp_active",
        "exp_levelup_channel"
    ], defaults=(None,) * 2
)


def get_all_words():
    """Get a list of almost every word in the English language."""
    with open("resources/text/words_alpha.txt", encoding="utf8") as file:
        return file.read().splitlines()


class Database:
    """
    A basic wrapper for mysql.connector with context manager support,
    designed for use with PhotonBot.
    """
    def __init__(self, database_config: ConfigParser):
        """
        Opens a connection to a database with the details specified in the
        `DatabaseConnection` section of the config file.
        """
        self._database = mysql.connector.connect(
            host=database_config['Host'],
            user=database_config['Username'],
            password=database_config['Password'],
            database=database_config['DatabaseName'], charset='utf8mb4'
        )
        self._cursor = self._database.cursor(buffered=True)

    def __enter__(self):
        return self

    def __exit__(self, _, __, ___):
        self.close()
        return False

    def fetch(self, *args, **kwargs) -> list[tuple]:
        """
        Execute an SQL statement and return the result. Designed for statements
        using `SELECT`.
        """
        self._cursor.execute(*args, **kwargs)
        return self._cursor.fetchall()

    def modify(self, *args, **kwargs) -> int:
        """
        Execute an SQL statement and return the number of rows modified.
        Designed for statements such as `UPDATE`, `INSERT` and `DELETE`.
        Modifications are automatically committed to the database server.
        """
        self._cursor.execute(*args, **kwargs)
        self._database.commit()
        return self._cursor.rowcount

    def close(self):
        """Close the connection to the database."""
        self._cursor.close()
        self._database.close()


def get_guild_config(database_config: ConfigParser, guild_id: int):
    """Get the configuration for a guild with a specified ID."""
    with Database(database_config) as database:
        try:
            response = database.fetch(
                f"SELECT {','.join(GuildConfig._fields)} FROM guild_config "
                + "WHERE guild_id = %s;", (guild_id,)
            )[0]
        except IndexError:
            return GuildConfig()
    return GuildConfig(*response)


def single_level_exp(level: int):
    """
    Get the amount of EXP needed to progress to a level from the previous one.
    """
    return 5 * level ** 2 + 50 * level + 100


def calculate_level(exp: int):
    """
    Calculate a user's level based off of the amount of EXP they have.
    Also returns the amount of "excess" EXP the user has progressing them
    toward the next level.
    """
    remainder = exp
    level = 0
    while remainder >= single_level_exp(level + 1):
        level += 1
        remainder -= single_level_exp(level)
    return level, remainder


def total_exp_for_level(level: int):
    """Calculate the minimum EXP required for a particular level."""
    return sum(single_level_exp(x) for x in range(1, level + 1))


def get_exp_info(database_config: ConfigParser, guild_id: int, user_id: int):
    """
    Get a user's EXP in a particular guild.
    Also calculates level, amount of EXP gained toward the next level,
    numeric rank compared to other guild members, EXP needed to progress from
    the current level to the next, and rank card color.
    """
    with Database(database_config) as database:
        exp_response = database.fetch(
            "SELECT exp FROM user_exp WHERE guild_id = %s AND user_id = %s;",
            (guild_id, user_id)
        )
        if len(exp_response) == 0:
            exp = 0
        else:
            exp = exp_response[0][0]
        level, remaining = calculate_level(exp)
        rank = database.fetch(
            "SELECT COUNT(*) FROM user_exp WHERE guild_id = %s AND exp >= %s;",
            (guild_id, exp)
        )[0][0]
        card_response = database.fetch(
            "SELECT red, green, blue FROM user_exp_card WHERE user_id = %s;",
            (user_id,)
        )
    if len(card_response) == 0:
        color = (None,) * 3
    else:
        color = card_response[0]
    return ExpInfo(
        exp, level, remaining, rank, single_level_exp(level + 1), color
    )
