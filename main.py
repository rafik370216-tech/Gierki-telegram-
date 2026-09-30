import os
import random
import logging

from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from database import Database

# --- bezpieczna konfiguracja ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_TOKEN")
if not TOKEN:
    raise RuntimeError("Brak zmiennej środowiskowej TELEGRAM_API_TOKEN. Ustaw ją w .env lub w środowisku.")

BOT_USERNAME = os.getenv("BOT_USERNAME", "YOUR_BOT_USERNAME")
db = Database()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---- HELPER FUNCTIONS ----
def get_user(update: Update):
    user = update.effective_user
    if user:
        db.add_user(user.id, user.username or user.first_name)
    return user


def require_bet(context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 1:
        return None
    try:
        bet = int(context.args[0])
        if bet <= 0:
            return None
        return bet
    except ValueError:
        return None


def check_balance(user_id: int, bet: int) -> bool:
    return db.get_balance(user_id) >= bet


def format_balance_message(user_id: int) -> str:
    balance = db.get_balance(user_id)
    rank = db.get_user_rank(user_id)
    vip = db.get_vip_level(user_id)
    return f"💰 Saldo: {balance} monet\n🏆 Pozycja: #{rank}\n👑 VIP: Poziom {vip}"


# ---- KOMENDY GŁÓWNE ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)

    keyboard = [
        [
            InlineKeyboardButton("🎮 Gry", callback_data="games"),
            InlineKeyboardButton("💰 Saldo", callback_data="balance"),
        ],
        [
            InlineKeyboardButton("🏆 Ranking", callback_data="leaderboard"),
            InlineKeyboardButton("🎁 Bonus", callback_data="bonus"),
        ],
        [
            InlineKeyboardButton("📋 Misje", callback_data="missions"),
            InlineKeyboardButton("🔗 Zaproszenie", callback_data="referral"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = (
        "🎰 Witaj w kasynie Telegram!\n\n"
        f"{format_balance_message(user.id)}\n\n"
        "Wybierz opcję poniżej lub wpisz komendy:\n"
        "/dice 50 - Gra w kości\n"
        "/slots 50 - Automaty\n"
        "/roulette 50 - Ruletka\n"
        "/blackjack 50 - Blackjack\n"
        "/crash 50 - Crash"
    )
    await update.message.reply_text(message, reply_markup=reply_markup)

    if context.args and context.args[0].startswith("ref_"):
        try:
            referrer_id = int(context.args[0].split("_")[1])
            if user.id != referrer_id:
                db.add_referral(referrer_id, user.id)
                await update.message.reply_text(
                    "🎉 Zaproszenie aktywne!\n"
                    "Dostałeś +100 monet\n"
                    "Polecający otrzymał +150 monet"
                )
        except Exception:
            pass


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🎮 DOSTĘPNE GRY:\n"
        "/dice <stawka> - Rzut kostką\n"
        "/slots <stawka> - Automaty\n"
        "/roulette <stawka> - Ruletka\n"
        "/blackjack <stawka> - Blackjack\n"
        "/crash <stawka> - Crash\n\n"
        "💰 KOMENDY:\n"
        "/balance - saldo\n"
        "/bonus - bonus dzienny\n"
        "/leaderboard - ranking\n"
        "/missions - misje\n"
        "/ref - link polecający\n"
    )
    await update.message.reply_text(help_text)


async def balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    await update.message.reply_text(format_balance_message(user.id))


# ---- CALLBACK HANDLERS ----
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = get_user(update)

    if query.data == "balance":
        await query.edit_message_text(text=format_balance_message(user.id))

    elif query.data == "games":
        keyboard = [
            [
                InlineKeyboardButton("🎲 Kości", callback_data="game_dice"),
                InlineKeyboardButton("🎰 Automaty", callback_data="game_slots"),
            ],
            [
                InlineKeyboardButton("🎯 Ruletka", callback_data="game_roulette"),
                InlineKeyboardButton("🂡 Blackjack", callback_data="game_blackjack"),
            ],
            [
                InlineKeyboardButton("🚀 Crash", callback_data="game_crash"),
                InlineKeyboardButton("◀️ Powrót", callback_data="back"),
            ],
        ]
        await query.edit_message_text(
            text="🎮 Wybierz grę. Użyj komendy: /dice 50, /slots 50, /roulette 50, /blackjack 50, /crash 50",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "game_dice":
        await query.edit_message_text("🎲 Użyj: /dice <stawka>\nPrzykład: /dice 50")
    elif query.data == "game_slots":
        await query.edit_message_text("🎰 Użyj: /slots <stawka>\nPrzykład: /slots 50")
    elif query.data == "game_roulette":
        await query.edit_message_text("🎯 Użyj: /roulette <stawka>\nPrzykład: /roulette 50")
    elif query.data == "game_blackjack":
        await query.edit_message_text("🂡 Użyj: /blackjack <stawka>\nPrzykład: /blackjack 50")
    elif query.data == "game_crash":
        await query.edit_message_text("🚀 Użyj: /crash <stawka>\nPrzykład: /crash 50")

    elif query.data == "leaderboard":
        leaders = db.get_leaderboard()
        text = "🏆 TOP 10 graczy:\n\n"
        for i, (username, balance) in enumerate(leaders, 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            text += f"{medal} {username} - {balance} monet\n"
        await query.edit_message_text(text=text)

    elif query.data == "bonus":
        result = db.give_daily_bonus(user.id)
        if result["success"]:
            await query.edit_message_text(f"🎁 Bonus dzienny\n\n✅ {result['message']}")
        else:
            await query.edit_message_text(f"🎁 Bonus dzienny\n\n❌ {result['message']}")

    elif query.data == "missions":
        db.update_missions(user.id)
        mission_list = db.get_missions(user.id)
        text = "📋 Twoje misje:\n\n"
        for mission in mission_list:
            status = "✅" if mission["completed"] == 1 else "⏳"
            text += f"{status} {mission['title']}\n_{mission['requirement']}_\n💰 {mission['reward']} monet\n\n"
        claimed = db.claim_completed_missions(user.id)
        if claimed > 0:
            text += f"🎉 Odczytano nagrody: +{claimed} monet!"
        await query.edit_message_text(text=text)

    elif query.data == "referral":
        count = db.cursor.execute('SELECT referrals FROM users WHERE id = ?', (user.id,)).fetchone()[0]
        link = f"https://t.me/{BOT_USERNAME}?start=ref_{user.id}"
        text = (
            "🔗 Zaproszenie znajomych\n\n"
            f"Twój link:\n`{link}`\n\n"
            f"👥 Zaproszeni: {count}\n"
            "💰 Za każdego: +150 monet\n"
            "Zaproszony otrzyma: +100 monet"
        )
        await query.edit_message_text(text=text)

    elif query.data == "back":
        keyboard = [
            [
                InlineKeyboardButton("🎮 Gry", callback_data="games"),
                InlineKeyboardButton("💰 Saldo", callback_data="balance"),
            ],
            [
                InlineKeyboardButton("🏆 Ranking", callback_data="leaderboard"),
                InlineKeyboardButton("🎁 Bonus", callback_data="bonus"),
            ],
            [
                InlineKeyboardButton("📋 Misje", callback_data="missions"),
                InlineKeyboardButton("🔗 Zaproszenie", callback_data="referral"),
            ],
        ]
        await query.edit_message_text(
            text="🎰 Menu główne",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# ---- GRY ----
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    bet = require_bet(context)
    if bet is None:
        await update.message.reply_text("❗ Użyj: /dice <stawka>\nPrzykład: /dice 50")
        return

    if not check_balance(user.id, bet):
        balance = db.get_balance(user.id)
        await update.message.reply_text(f"❌ Brak środków! Masz: {balance}, potrzebujesz: {bet}")
        return

    db.spend_balance(user.id, bet)
    roll = random.randint(1, 6)

    if roll >= 4:
        winnings = int(bet * 1.8)
        db.update_balance(user.id, winnings)
        db.record_game(user.id, "dice", bet, f"roll={roll}", winnings)
        db.update_missions(user.id)
        await update.message.reply_text(f"🎲 Wyrzuciłeś: {roll}\n✅ Wygrywasz {winnings} monet!")
    else:
        db.record_game(user.id, "dice", bet, f"roll={roll}", 0)
        db.update_missions(user.id)
        await update.message.reply_text(f"🎲 Wyrzuciłeś: {roll}\n❌ Przegrywasz {bet} monet.")


async def slots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    bet = require_bet(context)
    if bet is None:
        await update.message.reply_text("❗ Użyj: /slots <stawka>\nPrzykład: /slots 50")
        return

    if not check_balance(user.id, bet):
        balance = db.get_balance(user.id)
        await update.message.reply_text(f"❌ Brak środków! Masz: {balance}, potrzebujesz: {bet}")
        return

    db.spend_balance(user.id, bet)
    symbols = ["🍒", "🍋", "🍊", "7️⃣", "💎"]
    result = [random.choice(symbols) for _ in range(3)]
    message = "🎰 " + " | ".join(result)

    if result[0] == result[1] == result[2]:
        winnings = int(bet * 4.5)
        db.update_balance(user.id, winnings)
        db.record_game(user.id, "slots", bet, str(result), winnings)
        db.update_missions(user.id)
        await update.message.reply_text(f"{message}\n🎉 JACKPOT! Wygrywasz {winnings} monet!")
    elif result[0] == result[1] or result[1] == result[2]:
        winnings = int(bet * 1.8)
        db.update_balance(user.id, winnings)
        db.record_game(user.id, "slots", bet, str(result), winnings)
        db.update_missions(user.id)
        await update.message.reply_text(f"{message}\n✨ Dwie takie same! Wygrywasz {winnings} monet!")
    else:
        db.record_game(user.id, "slots", bet, str(result), 0)
        db.update_missions(user.id)
        await update.message.reply_text(f"{message}\n❌ Przegrywasz {bet} monet.")


async def roulette(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    bet = require_bet(context)
    if bet is None:
        await update.message.reply_text("❗ Użyj: /roulette <stawka>\nPrzykład: /roulette 50")
        return

    if not check_balance(user.id, bet):
        balance = db.get_balance(user.id)
        await update.message.reply_text(f"❌ Brak środków! Masz: {balance}, potrzebujesz: {bet}")
        return

    db.spend_balance(user.id, bet)
    colors = ["🔴", "⚫"]
    result = random.choice(colors)

    if random.random() > 0.05:
        winnings = int(bet * 1.9)
        db.update_balance(user.id, winnings)
        db.record_game(user.id, "roulette", bet, result, winnings)
        db.update_missions(user.id)
        await update.message.reply_text(f"🎯 Ruletka: {result}\n✅ Wygrywasz {winnings} monet!")
    else:
        db.record_game(user.id, "roulette", bet, result, 0)
        db.update_missions(user.id)
        await update.message.reply_text(f"🎯 Ruletka: {result}\n❌ Przegrywasz {bet} monet.")


async def blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    bet = require_bet(context)
    if bet is None:
        await update.message.reply_text("❗ Użyj: /blackjack <stawka>\nPrzykład: /blackjack 50")
        return

    if not check_balance(user.id, bet):
        balance = db.get_balance(user.id)
        await update.message.reply_text(f"❌ Brak środków! Masz: {balance}, potrzebujesz: {bet}")
        return

    db.spend_balance(user.id, bet)

    def card_value():
        return random.randint(1, 11)

    player = [card_value(), card_value()]
    dealer = [card_value()]

    player_total = sum(player)
    dealer_total = sum(dealer)

    if player_total == 21:
        winnings = int(bet * 2.2)
        db.update_balance(user.id, winnings)
        db.record_game(user.id, "blackjack", bet, f"player={player_total}", winnings)
        db.update_missions(user.id)
        await update.message.reply_text(f"🂡 Blackjack! [{player}] = {player_total}\n✅ Wygrywasz {winnings} monet!")
        return

    while player_total < 17:
        player.append(card_value())
        player_total = sum(player)

    while dealer_total < 17:
        dealer.append(card_value())
        dealer_total = sum(dealer)

    if player_total > 21:
        db.record_game(user.id, "blackjack", bet, "bust", 0)
        db.update_missions(user.id)
        await update.message.reply_text(f"🂡 [{player}] = {player_total}\n❌ Przegrywasz {bet} monet (BUST).")
    elif dealer_total > 21 or player_total > dealer_total:
        winnings = int(bet * 2)
        db.update_balance(user.id, winnings)
        db.record_game(user.id, "blackjack", bet, "win", winnings)
        db.update_missions(user.id)
        await update.message.reply_text(f"🂡 [{player}] = {player_total} vs [{dealer}] = {dealer_total}\n✅ Wygrywasz {winnings} monet!")
    elif player_total == dealer_total:
        db.update_balance(user.id, bet)
        db.record_game(user.id, "blackjack", bet, "push", bet)
        db.update_missions(user.id)
        await update.message.reply_text(f"🂡 Remis! [{player}] = {player_total}\n✅ Zwracamy stawkę: {bet} monet")
    else:
        db.record_game(user.id, "blackjack", bet, "loss", 0)
        db.update_missions(user.id)
        await update.message.reply_text(f"🂡 [{player}] = {player_total} vs [{dealer}] = {dealer_total}\n❌ Przegrywasz {bet} monet.")


async def crash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    bet = require_bet(context)
    if bet is None:
        await update.message.reply_text("❗ Użyj: /crash <stawka>\nPrzykład: /crash 50")
        return

    if not check_balance(user.id, bet):
        balance = db.get_balance(user.id)
        await update.message.reply_text(f"❌ Brak środków! Masz: {balance}, potrzebujesz: {bet}")
        return

    db.spend_balance(user.id, bet)
    crash_at = round(random.uniform(1.1, 7.0), 2)
    max_multiplier = round(random.uniform(1.5, 4.0), 2)

    if max_multiplier < crash_at:
        winnings = int(bet * max_multiplier)
        db.update_balance(user.id, winnings)
        db.record_game(user.id, "crash", bet, f"cashout={max_multiplier}x", winnings)
        db.update_missions(user.id)
        await update.message.reply_text(f"🚀 Crash: {crash_at}x\n✅ Cashout: {max_multiplier}x → Wygrywasz {winnings} monet!")
    else:
        db.record_game(user.id, "crash", bet, f"crash={crash_at}x", 0)
        db.update_missions(user.id)
        await update.message.reply_text(f"💥 Crash: {crash_at}x\n❌ Przegrywasz {bet} monet.")


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    leaders = db.get_leaderboard()
    if not leaders:
        await update.message.reply_text("Brak graczy w rankingu.")
        return

    text = "🏆 TOP 10 graczy:\n\n"
    for i, (username, balance) in enumerate(leaders, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {username} — {balance} monet\n"
    await update.message.reply_text(text)


async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    result = db.give_daily_bonus(user.id)
    if result["success"]:
        await update.message.reply_text(f"🎁 Bonus dzienny\n\n✅ {result['message']}")
    else:
        await update.message.reply_text(f"🎁 Bonus dzienny\n\n❌ {result['message']}")


async def missions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    db.update_missions(user.id)
    mission_list = db.get_missions(user.id)
    if not mission_list:
        await update.message.reply_text("Brak misji.")
        return

    text = "📋 Twoje misje:\n\n"
    for mission in mission_list:
        status = "✅" if mission["completed"] == 1 else "⏳"
        text += f"{status} {mission['title']}\n_{mission['requirement']}_\n💰 {mission['reward']} monet\n\n"

    claimed = db.claim_completed_missions(user.id)
    if claimed > 0:
        text += f"🎉 Odczytano nagrody: +{claimed} monet!"
    await update.message.reply_text(text)


async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = get_user(update)
    count = db.cursor.execute('SELECT referrals FROM users WHERE id = ?', (user.id,)).fetchone()[0]
    link = f"https://t.me/{BOT_USERNAME}?start=ref_{user.id}"
    text = (
        "🔗 Zaproszenie znajomych\n\n"
        f"Twój link:\n`{link}`\n\n"
        f"👥 Zaproszeni: {count}\n"
        "💰 Za każdego: +150 monet\n"
        "Zaproszony otrzyma: +100 monet"
    )
    await update.message.reply_text(text)


# ---- MAIN ----
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("balance", balance_cmd))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("slots", slots))
    app.add_handler(CommandHandler("roulette", roulette))
    app.add_handler(CommandHandler("blackjack", blackjack))
    app.add_handler(CommandHandler("crash", crash))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("bonus", bonus))
    app.add_handler(CommandHandler("missions", missions))
    app.add_handler(CommandHandler("ref", referral))
    app.add_handler(CallbackQueryHandler(button_callback))

    logger.info("Bot uruchamiany...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
