# 🎰 Gierki-telegram- | Crypto Casino Games

Platforma gier kasynowych zintegrowana z Telegramem, umożliwiająca graczom zarabianie i wymianę kryptowalut.

## 🎯 Funkcjonalności

### 🎮 Dostępne Gry
- **Dice Roll** - Klasyczna gra w kości z mnożnikami
- **Slots** - Automaty do gry z różnymi symbolami
- **BlackJack** - Gra w karty na żywo
- **Roulette** - Europejska ruletka kasynowa
- **Crash Game** - Gra w rosnący mnożnik z risky/safe opcjami

### 💰 System Kryptowalut
- Wsparcie dla Bitcoin (BTC), Ethereum (ETH), USDT
- Szybkie depozyty i wypłaty
- Portfel wbudowany w Telegramie
- Kursy wymiany w czasie rzeczywistym

### 📊 System Punktów & Statystyk
- Zbieranie punktów za każdą grę
- Ranking globalny graczy
- Historia transakcji
- Statystyki wygranych/przegranych

### 🏆 Dodatkowe Funkcje
- Daily Bonus - Dzienne bonusy za login
- Referral Program - Zarabiaj na zaproszeniach
- Tournaments - Turnieje z nagrodami
- VIP Levels - Poziomy członkostwa z benefitami

## 🚀 Szybki Start

### Wymagania
- Python 3.8+
- Telegram Bot API Token
- Crypto Exchange API (CoinGecko/Binance)
- Database (MongoDB/PostgreSQL)

### Instalacja
```bash
git clone https://github.com/rafik370216-tech/Gierki-telegram-.git
cd Gierki-telegram-
pip install -r requirements.txt
```

### Konfiguracja
```bash
cp .env.example .env
# Uzupełnij: TELEGRAM_TOKEN, CRYPTO_API_KEY, DB_URL
```

### Uruchomienie
```bash
python main.py
```

## 📱 Komendy Bota

- `/start` - Rejestracja i wyświetlenie menu
- `/play [gra]` - Rozpoczęcie gry
- `/balance` - Wyświetlenie salda kryptowalut
- `/deposit` - Wpłata do portfela
- `/withdraw` - Wypłata z portfela
- `/stats` - Twoje statystyki
- `/leaderboard` - Top 10 graczy
- `/bonus` - Codzienny bonus

## ⚠️ Disclaimer

Gry hazardowe niosą ryzyko finansowe. Gracz sam ponosi odpowiedzialność za swoje decyzje. Platforma nie jest odpowiedzialna za straty finansowe. **Graj odpowiedzialnie!**

## 📄 Licencja

MIT License - patrz `LICENSE` w repozytorium

---

**Autor:** [@rafik370216-tech](https://github.com/rafik370216-tech)
**Status:** 🔨 W Rozwoju