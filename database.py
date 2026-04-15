import sqlite3

class Database:
    def __init__(self, db_name='gierki.db'):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            balance REAL DEFAULT 0
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            player_id INTEGER,
            score INTEGER,
            FOREIGN KEY(player_id) REFERENCES users(id)
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            type TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )''')
        self.connection.commit()

    def add_user(self, username):
        self.cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
        self.connection.commit()

    def record_game(self, player_id, score):
        self.cursor.execute('INSERT INTO games (player_id, score) VALUES (?, ?)', (player_id, score))
        self.connection.commit()

    def update_balance(self, user_id, amount):
        self.cursor.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (amount, user_id))
        self.cursor.execute('INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, ?)', (user_id, amount, 'update'))
        self.connection.commit()

    def get_leaderboard(self):
        self.cursor.execute('SELECT username, balance FROM users ORDER BY balance DESC')
        return self.cursor.fetchall()

    def close(self):
        self.connection.close()  

# Example usage:
if __name__ == '__main__':
    db = Database()
    db.add_user('player1')
    db.update_balance(1, 100)
    db.record_game(1, 50)
    print(db.get_leaderboard())
    db.close()