import sqlite3
from datetime import datetime, timedelta, date

class Database:
    def __init__(self, db_name='gierki.db'):
        self.connection = sqlite3.connect(db_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                balance REAL DEFAULT 1000,
                last_bonus_date TEXT,
                bonus_streak INTEGER DEFAULT 0,
                referrals INTEGER DEFAULT 0,
                vip_level INTEGER DEFAULT 0
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id INTEGER,
                game_name TEXT,
                bet REAL,
                result TEXT,
                winnings REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(player_id) REFERENCES users(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                type TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                requirement TEXT,
                reward REAL,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')

        self.connection.commit()

    def ensure_user(self, user_id, username=None):
        row = self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if row is None:
            self.cursor.execute(
                'INSERT INTO users (id, username, balance, last_bonus_date, bonus_streak, referrals, vip_level) VALUES (?, ?, 1000, NULL, 0, 0, 0)',
                (user_id, username or f'user_{user_id}')
            )
            self.connection.commit()
        elif username and row['username'] != username:
            self.cursor.execute('UPDATE users SET username = ? WHERE id = ?', (username, user_id))
            self.connection.commit()

    def add_user(self, user_id, username=None):
        self.ensure_user(user_id, username)

    def get_balance(self, user_id):
        self.ensure_user(user_id)
        row = self.cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,)).fetchone()
        return row['balance'] if row else 0

    def update_balance(self, user_id, amount):
        self.ensure_user(user_id)
        current = self.get_balance(user_id)
        new_balance = current + amount
        self.cursor.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
        self.cursor.execute('INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, ?)', (user_id, amount, 'update'))
        self.connection.commit()
        return new_balance

    def spend_balance(self, user_id, amount):
        self.ensure_user(user_id)
        current = self.get_balance(user_id)
        if current < amount:
            return False
        self.update_balance(user_id, -amount)
        return True

    def record_game(self, player_id, game_name, bet, result, winnings):
        self.ensure_user(player_id)
        self.cursor.execute(
            'INSERT INTO games (player_id, game_name, bet, result, winnings) VALUES (?, ?, ?, ?, ?)',
            (player_id, game_name, bet, result, winnings)
        )
        self.connection.commit()

    def get_leaderboard(self):
        self.cursor.execute('SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10')
        return self.cursor.fetchall()

    def get_last_bonus_date(self, user_id):
        self.ensure_user(user_id)
        row = self.cursor.execute('SELECT last_bonus_date FROM users WHERE id = ?', (user_id,)).fetchone()
        if row and row['last_bonus_date']:
            return datetime.strptime(row['last_bonus_date'], '%Y-%m-%d').date()
        return None

    def get_bonus_streak(self, user_id):
        self.ensure_user(user_id)
        row = self.cursor.execute('SELECT bonus_streak FROM users WHERE id = ?', (user_id,)).fetchone()
        return row['bonus_streak'] if row else 0

    def set_bonus_streak(self, user_id, value):
        self.cursor.execute('UPDATE users SET bonus_streak = ? WHERE id = ?', (value, user_id))
        self.connection.commit()

    def give_daily_bonus(self, user_id):
        self.ensure_user(user_id)
        today = date.today()
        last_bonus = self.get_last_bonus_date(user_id)
        streak = self.get_bonus_streak(user_id)

        if last_bonus == today:
            return {'success': False, 'bonus': 0, 'message': 'Bonus już został odebrany dzisiaj.'}

        if last_bonus is not None and last_bonus == today - timedelta(days=1):
            streak += 1
        else:
            streak = 1

        bonus = 50 + (streak * 10)
        self.update_balance(user_id, bonus)
        self.cursor.execute(
            'UPDATE users SET last_bonus_date = ?, bonus_streak = ? WHERE id = ?',
            (today.isoformat(), streak, user_id)
        )
        self.connection.commit()

        return {'success': True, 'bonus': bonus, 'message': f'Bonus dzienny: +{bonus} monet!'}

    def get_vip_level(self, user_id):
        self.ensure_user(user_id)
        row = self.cursor.execute('SELECT vip_level FROM users WHERE id = ?', (user_id,)).fetchone()
        return row['vip_level'] if row else 0

    def set_vip_level(self, user_id, level):
        self.cursor.execute('UPDATE users SET vip_level = ? WHERE id = ?', (level, user_id))
        self.connection.commit()

    def get_user_rank(self, user_id):
        self.ensure_user(user_id)
        row = self.cursor.execute(
            'SELECT COUNT(*) + 1 AS rank FROM users WHERE balance > (SELECT balance FROM users WHERE id = ?)',
            (user_id,)
        ).fetchone()
        return row['rank'] if row else 1

    def add_referral(self, referrer_id, invited_user_id):
        self.ensure_user(referrer_id)
        self.ensure_user(invited_user_id)
        self.cursor.execute(
            'UPDATE users SET referrals = referrals + 1 WHERE id = ?',
            (referrer_id,)
        )
        self.update_balance(referrer_id, 150)
        self.update_balance(invited_user_id, 100)
        self.connection.commit()

    def ensure_missions(self, user_id):
        self.ensure_user(user_id)
        defaults = [
            ('Pierwsza gra', 'Zagraj 1 raz', 50),
            ('Gracz', 'Zagraj 5 gier', 100),
            ('Szczęściarz', 'Wygraj 3 gry', 200),
            ('Bogacz', 'Zdobądź 2000 monet', 500),
        ]

        for title, requirement, reward in defaults:
            existing = self.cursor.execute(
                'SELECT id FROM missions WHERE user_id = ? AND title = ?',
                (user_id, title)
            ).fetchone()
            if existing is None:
                self.cursor.execute(
                    'INSERT INTO missions (user_id, title, requirement, reward, completed) VALUES (?, ?, ?, ?, 0)',
                    (user_id, title, requirement, reward)
                )
        self.connection.commit()

    def update_missions(self, user_id):
        self.ensure_missions(user_id)

        total_games = self.cursor.execute(
            'SELECT COUNT(*) AS total FROM games WHERE player_id = ?',
            (user_id,)
        ).fetchone()['total']

        total_wins = self.cursor.execute(
            'SELECT COUNT(*) AS total FROM games WHERE player_id = ? AND winnings > 0',
            (user_id,)
        ).fetchone()['total']

        balance = self.get_balance(user_id)

        mission_rules = [
            ('Pierwsza gra', total_games >= 1),
            ('Gracz', total_games >= 5),
            ('Szczęściarz', total_wins >= 3),
            ('Bogacz', balance >= 2000),
        ]

        for title, completed in mission_rules:
            if completed:
                self.cursor.execute(
                    'UPDATE missions SET completed = 1 WHERE user_id = ? AND title = ?',
                    (user_id, title)
                )
        self.connection.commit()

    def get_missions(self, user_id):
        self.ensure_missions(user_id)
        return self.cursor.execute(
            'SELECT * FROM missions WHERE user_id = ? ORDER BY id',
            (user_id,)
        ).fetchall()

    def claim_completed_missions(self, user_id):
        total_claimed = 0
        missions = self.get_missions(user_id)
        for mission in missions:
            if mission['completed'] == 1:
                total_claimed += mission['reward']
                self.cursor.execute(
                    'UPDATE missions SET completed = 2 WHERE id = ?',
                    (mission['id'],)
                )
                self.update_balance(user_id, mission['reward'])
        self.connection.commit()
        return total_claimed

    def close(self):
        self.connection.close()


if __name__ == '__main__':
    db = Database()
    db.add_user(1, 'player1')
    db.update_balance(1, 100)
    print(db.get_leaderboard())
    db.close()
