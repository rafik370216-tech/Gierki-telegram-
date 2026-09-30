import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from database import Database


def test_database_creates_user_and_balance(tmp_path):
    db_file = tmp_path / "test_gierki.db"
    db = Database(str(db_file))

    db.add_user(42, "tester")
    assert db.get_balance(42) == 1000

    new_balance = db.update_balance(42, 250)
    assert new_balance == 1250
    assert db.get_balance(42) == 1250

    db.close()


def test_database_daily_bonus_awards_streak(tmp_path):
    db_file = tmp_path / "test_bonus.db"
    db = Database(str(db_file))

    db.add_user(99, "player")
    result = db.give_daily_bonus(99)

    assert result["success"] is True
    assert result["bonus"] >= 50
    assert db.get_balance(99) >= 1000

    db.close()
