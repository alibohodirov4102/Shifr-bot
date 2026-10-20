"""
╔══════════════════════════════════════════════════════════╗
║              SHIFR BOT - Guruh Shifrlash Boti            ║
║   1) Faqat bitta odamga ko'rinishi (/only)              ║
║   2) Bitta odamga ko'rinmasligi (/hide)                  ║
║   3) Savol-javoblar & Viktorina (/quiz)                  ║
║   4) Coinga maxfiy xabarni sotib olish (2-odam)          ║
╚══════════════════════════════════════════════════════════╝
"""

import logging
import random
import uuid
import asyncio
from collections import OrderedDict
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.error import BadRequest, Forbidden
from config import BOT_TOKEN, ADMIN_IDS
from database import Database
from modes import ModeManager
import quiz as quiz_module

# ─── Logging ──────────────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ─── Global ob'yektlar ────────────────────────────────────
db = Database()
mode_manager = ModeManager()

# Maxfiy xabarlar keshi
class MessageCache(OrderedDict):
    def __init__(self, maxsize=2000):
        super().__init__()
        self.maxsize = maxsize

    def set(self, key, value):
        if len(self) >= self.maxsize:
            self.popitem(last=False)
        self[key] = value

SECRET_MESSAGES = MessageCache()
ACTIVE_QUIZZES = MessageCache(maxsize=500)


# ══════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR
# ══════════════════════════════════════════════════════════

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Foydalanuvchi guruh admini ekanligini tekshiradi."""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if user_id in ADMIN_IDS:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except Exception:
        return False


async def delete_original(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asl xabarni o'chiradi (agar bot admin bo'lsa)."""
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
    except (BadRequest, Forbidden):
        pass


def _extract_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Buyruqdan yoki Reply dan foydalanuvchini ajratib oladi."""
    target_id = None
    target_username = None
    target_name = ""

    if update.message.reply_to_message and update.message.reply_to_message.from_user:
        u = update.message.reply_to_message.from_user
        target_id = u.id
        target_username = u.username
        target_name = u.first_name or ""
    elif context.args:
        arg = context.args[0].strip()
        if arg.isdigit():
            target_id = int(arg)
            target_name = f"ID: {arg}"
        else:
            target_username = arg.lstrip("@")
            target_name = f"@{target_username}"

    return target_id, target_username, target_name


# ══════════════════════════════════════════════════════════
#  BUYRUQLAR
# ══════════════════════════════════════════════════════════

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot boshlanganda /start buyrug'i."""
    chat_type = update.effective_chat.type
    user = update.effective_user

    # Yangi foydalanuvchiga boshlang'ich coin berish
    user_coins = db.get_user_coins(user.id)

    if chat_type == "private":
        text = (
            f"👋 Salom, <b>{user.first_name}</b>!\n\n"
            "🔐 Men <b>Shifr Bot</b>man — guruhda maxfiy xabarlar va qiziqarli viktorinalar boti!\n\n"
            f"🪙 Sizning balansingiz: <b>{user_coins} Coin</b>\n\n"
            "✨ <b>Asosiy Imkoniyatlar:</b>\n"
            "1️⃣ <b>Faqat 1 kishiga ko'rinishi:</b>\n"
            "   <code>/only @username</code> — Xabar faqat unga ko'rinadi, qolganlarga smaylik!\n\n"
            "2️⃣ <b>Coinga ochish (Ayg'oqchilik 🕵️‍♂️):</b>\n"
            "   Guruhdagi boshqa bola xabarni <b>10 Coin</b> evaziga sotib olib o'qishi mumkin!\n"
            "   <i>(Natijada faqat 2 kishi ko'radi: 1-si siz tanlagan odam, 2-si esa coinga sotib olgan odam!)</i>\n\n"
            "3️⃣ <b>Futbol & Mantiq Viktorinalari:</b>\n"
            "   <code>/quiz</code> — Qiyin savollarga javob berib, coin ishlang!\n\n"
            "📋 <b>Barcha buyruqlar:</b>\n"
            "• <code>/quiz</code> — Viktorina boshlash\n"
            "• <code>/balans</code> — Coiningizni tekshirish\n"
            "• <code>/top</code> — Eng ko'p coin to'plaganlar reytingi\n"
            "• <code>/only @username</code> — Faqat 1 kishiga ko'rsatish\n"
            "• <code>/hide @username</code> — 1 kishidan yashirish\n"
            "• <code>/clear</code> — Cheklovlarni bekor qilish\n"
            "• <code>/setmode</code> — Smaylik/soxta matn turini tanlash"
        )
        keyboard = [[
            InlineKeyboardButton("➕ Guruhga qo'shish", url=f"https://t.me/{context.bot.username}?startgroup=start"),
            InlineKeyboardButton("⚽ Viktorina o'ynash", callback_data="btn_quiz")
        ]]
        await update.message.reply_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "✅ <b>Shifr Bot</b> guruhda tayyor!\n\n"
            "🎯 <b>Faqat 1 kishiga ko'rsatish:</b> <code>/only @username</code> (yoki reply)\n"
            "⚽ <b>Futbol & Mantiq viktorinasi:</b> <code>/quiz</code>\n"
            "💰 <b>Balansni ko'rish:</b> <code>/balans</code>",
            parse_mode="HTML"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam."""
    text = (
        "🆘 <b>BOT YO'RIQNOMASI</b>\n\n"
        "⚽ <b>Savol-Javoblar & Coinlar:</b>\n"
        "• <code>/quiz</code> yoki <code>/savol</code> — Qiyin futbol va mantiq savoli chiqarish\n"
        "• <code>/balans</code> — Sizning coinlaringiz\n"
        "• <code>/top</code> — Guruhdagi eng zo'r bilimdonlar reytingi\n"
        "• <code>/pay @username miqdor</code> — Do'stingizga coin o'tkazish\n\n"
        "🔒 <b>Maxfiy Xabar & Sotib Olish:</b>\n"
        "• <code>/only @username</code> — Faqat 1 kishiga ko'rinsin!\n"
        "• Qolgan bolalar bu xabarni <b>10 Coin</b> evaziga sotib olib o'qishi mumkin!\n"
        "• Shunda xabar faqat 2 kishiga ko'rinadi: biri siz tanlagan odam, biri coinga sotib olgan odam!\n\n"
        "🚫 <b>Boshqa buyruqlar:</b>\n"
        "• <code>/hide @username</code> — Shu odamdan yashirish\n"
        "• <code>/clear</code> — Barcha cheklovlarni tozalash\n"
        "• <code>/setmode</code> — Smaylik / soxta matn turini o'zgartirish"
    )
    await update.message.reply_text(text, parse_mode="HTML")


# ══════════════════════════════════════════════════════════
#  VIKTORINA (QUIZ) & COIN TIZIMI
# ══════════════════════════════════════════════════════════

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guruhga yoki shaxsiyga qiziqarli va qiyin savol chiqaradi."""
    chat_id = update.effective_chat.id
    q = quiz_module.get_random_question()

    quiz_id = uuid.uuid4().hex[:8]
    ACTIVE_QUIZZES.set(quiz_id, {
        "question": q,
        "answered_users": set(),
        "solved": False,
        "winner": None,
        "chat_id": chat_id
    })

    options_text = ""
    letters = ["A", "B", "C", "D"]
    for i, opt in enumerate(q["options"]):
        options_text += f"<b>{letters[i]})</b> {opt}\n"

    text = (
        f"🏆 <b>SAVOL-JAVOB VIKTORINA</b>\n"
        f"Kategoriya: <b>{q['category']}</b>\n"
        f"Mukofot: <b>+{q['reward']} 🪙 Coin</b>\n\n"
        f"❓ <b>{q['question']}</b>\n\n"
        f"{options_text}\n"
        f"<i>To'g'ri javobni birinchi bo'lib toping va coin yuting! 👇</i>"
    )

    buttons = [
        [
            InlineKeyboardButton("A", callback_data=f"quiz:{quiz_id}:0"),
            InlineKeyboardButton("B", callback_data=f"quiz:{quiz_id}:1"),
            InlineKeyboardButton("C", callback_data=f"quiz:{quiz_id}:2"),
            InlineKeyboardButton("D", callback_data=f"quiz:{quiz_id}:3"),
        ]
    ]

    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi balansini ko'rsatadi."""
    user = update.effective_user
    coins = db.get_user_coins(user.id)
    text = (
        f"👤 <b>{user.first_name}</b>\n"
        f"💰 Balansingiz: <b>{coins} 🪙 Coin</b>\n\n"
        f"💡 <i>Coinlarni qanday ishlatish mumkin?</i>\n"
        f"Guruhdagi maxfiy xabarlarni <b>10 Coin</b> evaziga sotib olib, nima yozilganini bilib olishingiz mumkin! 🕵️‍♂️\n"
        f"Coin ishlash uchun: <code>/quiz</code>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Eng ko'p coin egalari reytingi."""
    leaders = db.get_leaderboard(limit=10)
    if not leaders:
        await update.message.reply_text("Hali hech kim coin yutmadi. /quiz buyrug'ini bering!")
        return

    text = "🏆 <b>ENG KO'P COIN EGALARI REYTINGI:</b>\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, lead in enumerate(leaders):
        icon = medals[i] if i < len(medals) else f"{i+1}."
        text += f"{icon} <b>{lead['name']}</b> — {lead['coins']} 🪙 ({lead['solved']} ta savol)\n"

    text += "\n💡 <i>Siz ham /quiz orqali savollarga javob berib, peshqadamlar safiga kiring!</i>"
    await update.message.reply_text(text, parse_mode="HTML")


async def pay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Do'stiga coin o'tkazish: /pay @username 10"""
    sender = update.effective_user
    sender_coins = db.get_user_coins(sender.id)

    target_id, target_username, target_name = _extract_target(update, context)
    amount = 0

    for arg in context.args:
        if arg.isdigit():
            amount = int(arg)
            break

    if (not target_id and not target_username) or amount <= 0:
        await update.message.reply_text(
            "💡 <b>Qanday ishlatiladi?</b>\n"
            "<code>/pay @username 10</code> (yoki uning xabariga reply qilib <code>/pay 10</code>)",
            parse_mode="HTML"
        )
        return

    if sender_coins < amount:
        await update.message.reply_text(
            f"❌ Coiningiz yetarli emas! Sizda {sender_coins} 🪙 bor, o'tkazmoqchi bo'lganingiz: {amount} 🪙.",
            parse_mode="HTML"
        )
        return

    # Coin o'tkazish
    db.spend_user_coins(sender.id, amount)

    # Qabul qiluvchi
    target_disp = f"@{target_username}" if target_username else (target_name or f"ID: {target_id}")
    # Agar target_id bo'lsa darhol qo'shamiz
    if target_id:
        db.add_user_coins(target_id, amount, target_username or "", target_name or "")

    await update.message.reply_text(
        f"💸 <b>{sender.first_name}</b> foydalanuvchisi <b>{target_disp}</b> ga <b>{amount} 🪙 Coin</b> o'tkazdi!\n"
        f"Sizning qolgan balansingiz: <b>{sender_coins - amount} 🪙</b>",
        parse_mode="HTML"
    )


# ══════════════════════════════════════════════════════════
#  MAXFIY REJIM BUYRUQLARI (/only, /hide, /clear)
# ══════════════════════════════════════════════════════════

async def only_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Faqat bitta odamga ko'rinadigan rejim."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("Bu buyruq guruhda ishlatiladi!")
        return

    chat_id = update.effective_chat.id
    target_id, target_username, target_name = _extract_target(update, context)

    if not target_id and not target_username:
        await update.message.reply_text(
            "💡 <b>Qanday ishlatiladi?</b>\n\n"
            "1️⃣ Xabar faqat kimga ko'rinishi kerak bo'lsa, unga reply qilib <code>/only</code> deb yozing\n"
            "<i>yoki</i>\n"
            "2️⃣ <code>/only @foydalanuvchi</code> deb yozing.",
            parse_mode="HTML"
        )
        return

    db.set_only_user(chat_id, target_id, target_username, target_name)
    disp = f"@{target_username}" if target_username else (target_name or f"ID: {target_id}")

    await update.message.reply_text(
        f"🎯 <b>Tanlandi: {disp}</b>\n\n"
        f"Endi siz guruhda yozgan xabarlarni <b>FAQAT {disp}</b> va siz o'qiy olasiz!\n"
        f"Guruhdagi qolgan bolalarga esa <b>smaylik/soxta matn</b> ko'rinadi.\n\n"
        f"💡 <i>Lekin qolgan bolalar bu xabarni <b>10 Coin</b> evaziga sotib olib ochishi mumkin! "
        f"Shunda xabar faqat 2 kishiga ko'rinadi (1-si {disp}, 2-si sotib olgan kishi).</i> 🕵️‍♂️\n\n"
        f"<i>(Bekor qilish uchun: <code>/clear</code>)</i>",
        parse_mode="HTML"
    )


async def hide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bitta odamdan yashirish rejimi."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("Bu buyruq guruhda ishlatiladi!")
        return

    chat_id = update.effective_chat.id
    target_id, target_username, target_name = _extract_target(update, context)

    if not target_id and not target_username:
        await update.message.reply_text(
            "💡 <b>Qanday ishlatiladi?</b>\n\n"
            "1️⃣ Kimdan yashirmoqchi bo'lsangiz, uning xabariga reply qilib <code>/hide</code> yozing\n"
            "<i>yoki</i>\n"
            "2️⃣ <code>/hide @foydalanuvchi</code> deb yozing.",
            parse_mode="HTML"
        )
        return

    db.add_hidden_user(chat_id, target_id, target_username, target_name)
    disp = f"@{target_username}" if target_username else (target_name or f"ID: {target_id}")

    await update.message.reply_text(
        f"🚫 <b>Tanlandi: {disp}</b>\n\n"
        f"Endi xabarlar <b>{disp}</b> ga ko'rinmaydi (unga faqat smaylik/soxta matn ko'rinadi).\n"
        f"Guruhdagi qolgan barcha bolalar esa xabarni bemalol o'qiy oladi! 🔒\n\n"
        f"<i>(Bekor qilish uchun: <code>/clear</code>)</i>",
        parse_mode="HTML"
    )


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha cheklovlarni tozalash."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("Bu buyruq guruhda ishlatiladi!")
        return

    chat_id = update.effective_chat.id
    db.clear_targets(chat_id)
    await update.message.reply_text(
        "🔄 <b>Barcha cheklovlar bekor qilindi!</b>\n"
        "Guruh odatiy holatga qaytdi.\n"
        "• <code>/only @username</code> — Faqat 1 kishiga ko'rsatish\n"
        "• <code>/hide @username</code> — 1 kishidan yashirish\n"
        "• <code>/quiz</code> — Viktorina o'ynash",
        parse_mode="HTML"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guruh holati."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("Bu buyruq guruhda ishlaydi.")
        return

    chat_id = update.effective_chat.id
    mode = db.get_chat_mode(chat_id) or "emoji"
    active = db.is_chat_active(chat_id)
    target_mode = db.get_target_mode(chat_id)

    if target_mode == "only":
        users = db.get_only_users(chat_id)
        u_names = ", ".join([f"@{u['username']}" if u.get('username') else u.get('name', '') for u in users])
        holat_target = f"🎯 <b>Faqat {u_names} ga ko'rinadi</b> (boshqalar 10 coinga sotib oladi)"
    elif target_mode == "hide":
        users = db.get_hidden_users(chat_id)
        u_names = ", ".join([f"@{u['username']}" if u.get('username') else u.get('name', '') for u in users])
        holat_target = f"🚫 <b>{u_names} dan yashirilgan</b> (unga smaylik)"
    else:
        holat_target = "🌐 Cheklov yo'q (Umumiy shifrlash)"

    bot_holat = "Faol 🟢" if active else "O'chirilgan 🔴"
    text = (
        f"📊 <b>Guruh holati:</b>\n\n"
        f"• Bot: <b>{bot_holat}</b>\n"
        f"• Xabar ko'rinishi: {holat_target}\n"
        f"• Soxta matn turi: <b>{mode.upper()}</b> (/setmode)\n"
        f"• Guruh ID: <code>{chat_id}</code>\n\n"
        f"<i>Tozalash uchun: <code>/clear</code></i>"
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def setmode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rejim tanlash paneli."""
    if update.effective_chat.type == "private":
        await update.message.reply_text("Bu buyruq faqat guruhda ishlaydi.")
        return

    if not await is_admin(update, context):
        await update.message.reply_text("❌ Bu buyruq faqat adminlar uchun!")
        return

    chat_id = update.effective_chat.id
    keyboard = _build_mode_keyboard(chat_id)
    await update.message.reply_text(
        "🎭 <b>Soxta ko'rinish rejimini tanlang:</b>\n\n"
        "<i>(Ruxsati bo'lmagan odamlar xabarni bosganda ularga shu narsa ko'rinadi)</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def _build_mode_keyboard(chat_id: int) -> list:
    current = db.get_chat_mode(chat_id)
    modes = [
        ("🔀 Random",   "random"),
        ("😀 Emoji",    "emoji"),
        ("🔡 Morse",    "morse"),
        ("🔢 Binary",   "binary"),
        ("🔃 Reverse",  "reverse"),
        ("🌀 Zalgo",    "zalgo"),
        ("👻 Ghost",    "ghost"),
        ("🔠 Leet",     "leet"),
        ("🐱 Meow",     "meow"),
        ("✏️ Custom",   "custom"),
    ]
    keyboard = []
    row = []
    for label, mode_key in modes:
        check = "✅ " if current == mode_key else ""
        row.append(InlineKeyboardButton(
            f"{check}{label}", callback_data=f"mode:{mode_key}"
        ))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton("🔴 O'chirish", callback_data="mode:off"),
        InlineKeyboardButton("🟢 Yoqish", callback_data="mode:on"),
    ])
    return keyboard


async def on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Faqat adminlar uchun!")
        return
    db.set_chat_active(update.effective_chat.id, True)
    await update.message.reply_text("🟢 Shifrlash <b>yoqildi</b>!", parse_mode="HTML")


async def off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ Faqat adminlar uchun!")
        return
    db.set_chat_active(update.effective_chat.id, False)
    await update.message.reply_text("🔴 Shifrlash <b>o'chirildi</b>!", parse_mode="HTML")


# ══════════════════════════════════════════════════════════
#  CALLBACK QUERY HANDLER
#  (Viktorina javoblari, Xabar o'qish & Coinga sotib olish)
# ══════════════════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugmalar bosilganda ishlaydi."""
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    username = query.from_user.username
    user_name = query.from_user.first_name or "Foydalanuvchi"

    # ── 1. Viktorina tugmasi (Start menyusi orqali) ──
    if data == "btn_quiz":
        await query.answer()
        await quiz_command(update, context)
        return

    # ── 2. Viktorina javobini tekshirish ──
    if data.startswith("quiz:"):
        _, quiz_id, chosen_idx = data.split(":")
        chosen_idx = int(chosen_idx)
        quiz_data = ACTIVE_QUIZZES.get(quiz_id)

        if not quiz_data:
            await query.answer("⚠️ Bu savol eskirgan yoki muddati tugagan.", show_alert=True)
            return

        # Foydalanuvchi oldin javob berganmi?
        if user_id in quiz_data["answered_users"]:
            await query.answer("⚠️ Siz bu savolga allaqachon javob berdingiz!", show_alert=True)
            return

        quiz_data["answered_users"].add(user_id)
        q = quiz_data["question"]

        if chosen_idx == q["correct"]:
            # To'g'ri javob!
            if quiz_data.get("solved"):
                await query.answer(
                    f"👏 Javobingiz to'g'ri!\nLekin sizdan oldinroq boshqa birov topib bo'ldi.\n\n💡 {q['explanation']}",
                    show_alert=True
                )
            else:
                quiz_data["solved"] = True
                quiz_data["winner"] = user_name
                reward = q["reward"]
                total_coins = db.add_user_coins(user_id, reward, username or "", user_name)

                await query.answer(
                    f"🎉 TO'G'RI JAVOB!\n\n+{reward} 🪙 Coin yutdingiz!\nJami balansingiz: {total_coins} 🪙\n\n💡 {q['explanation']}",
                    show_alert=True
                )

                # Guruhga tabriklash
                correct_letter = ["A", "B", "C", "D"][q["correct"]]
                correct_answer_str = q["options"][q["correct"]]
                announce_text = (
                    f"🏆 <b>G'OLIB TOPIB BO'LINDI!</b>\n\n"
                    f"👤 <b>{user_name}</b> birinchi bo'lib to'g'ri javob berdi!\n"
                    f"✅ To'g'ri javob: <b>{correct_letter}) {correct_answer_str}</b>\n"
                    f"💰 Mukofot: <b>+{reward} 🪙 Coin</b>\n\n"
                    f"💡 <i>{q['explanation']}</i>\n\n"
                    f"Yangi savol uchun: <code>/quiz</code>"
                )
                try:
                    await query.message.edit_text(announce_text, parse_mode="HTML")
                except Exception:
                    pass
        else:
            # Noto'g'ri javob
            await query.answer(
                "❌ Noto'g'ri javob! Omad keyingi safar.",
                show_alert=True
            )
        return

    # ── 3. Maxfiy xabarni bepul o'qish (faqat ruxsat berilganlar) ──
    if data.startswith("read:"):
        secret_id = data.split(":", 1)[1]
        secret = SECRET_MESSAGES.get(secret_id)

        if not secret:
            await query.answer("⚠️ Bu xabar eskirgan.", show_alert=True)
            return

        target_mode = secret.get("target_mode", "none")
        sender_id = secret.get("sender_id")
        buyers = secret.get("buyers", set())
        is_sender = (user_id == sender_id)
        has_bought = (user_id in buyers)

        # Ruxsat tekshiruvi:
        can_read = False

        if is_sender or has_bought:
            can_read = True
        elif target_mode == "only":
            can_read = db.is_user_in_only_list(chat_id, user_id, username)
        elif target_mode == "hide":
            can_read = not db.is_user_hidden(chat_id, user_id, username)
        else:
            can_read = True

        if can_read:
            prefix = "📩 Asl xabar (10 🪙 evaziga ochilgan):" if has_bought else "📩 Asl xabar:"
            await query.answer(
                f"{prefix}\n\n{secret['text']}",
                show_alert=True
            )
            logger.info(f"[{chat_id}] {user_name} asl xabarni o'qidi.")
        else:
            # Soxta smaylik / matn ko'rsatiladi!
            mode = db.get_chat_mode(chat_id) or "emoji"
            fake_content = mode_manager.transform(secret["text"], mode, chat_id, db)
            await query.answer(
                f"🎭 Siz uchun bu xabar:\n\n{fake_content}\n\n"
                f"💡 Bu xabarni 10 Coin evaziga sotib olib o'qishingiz mumkin! ('🔓 10 🪙 ga ochish' tugmasini bosing)",
                show_alert=True
            )
            logger.info(f"[{chat_id}] {user_name} ga soxta xabar ko'rsatildi.")
        return

    # ── 4. Maxfiy xabarni 10 Coinga sotib olish (Ayg'oqchilik) ──
    if data.startswith("buy:"):
        secret_id = data.split(":", 1)[1]
        secret = SECRET_MESSAGES.get(secret_id)

        if not secret:
            await query.answer("⚠️ Bu xabar eskirgan.", show_alert=True)
            return

        sender_id = secret.get("sender_id")
        target_mode = secret.get("target_mode", "none")
        buyers = secret.setdefault("buyers", set())

        # Agar yozgan odam bo'lsa
        if user_id == sender_id:
            await query.answer("Siz bu xabarning muallifisiz, sizga shundoq ham ochiq!", show_alert=True)
            return

        # Agar allaqachon /only da tanlangan odam bo'lsa
        if target_mode == "only" and db.is_user_in_only_list(chat_id, user_id, username):
            await query.answer("Sizga bu xabar bepul ochiq! '📩 Xabarni o'qish' tugmasini bosing.", show_alert=True)
            return

        # Agar foydalanuvchi allaqachon sotib olgan bo'lsa
        if user_id in buyers:
            await query.answer("Siz bu xabarni allaqachon sotib olgansiz! '📩 Xabarni o'qish' tugmasini bosing.", show_alert=True)
            return

        # Limit tekshiruvi: Faqat 1 kishi sotib olishi mumkin!
        # Shunda jami 2 kishi ko'radi: 1-si tanlangan odam, 2-si sotib olgan kishi!
        if len(buyers) >= 1:
            await query.answer(
                "⚠️ Kech qoldingiz! Bu xabarni boshqa bir kishi allaqachon sotib olib bo'ldi.\n"
                "Faqat 1 kishi sotib olishiga ruxsat bor edi!",
                show_alert=True
            )
            return

        # Coini yetarlimi?
        price = 10
        user_coins = db.get_user_coins(user_id)
        if user_coins < price:
            await query.answer(
                f"❌ Coiningiz yetarli emas!\n\n"
                f"Sizda: {user_coins} 🪙\n"
                f"Ochish narxi: {price} 🪙\n\n"
                f"Savol-javob o'ynab coin ishlang: /quiz",
                show_alert=True
            )
            return

        # Xaridni amalga oshirish!
        success = db.spend_user_coins(user_id, price)
        if not success:
            await query.answer("❌ Xatolik yuz berdi.", show_alert=True)
            return

        buyers.add(user_id)
        remain_coins = user_coins - price

        await query.answer(
            f"🎉 TABRIKLAYMIZ! Xabar ochildi! (-{price} 🪙)\n"
            f"Qolgan balansingiz: {remain_coins} 🪙\n\n"
            f"📩 Asl xabar:\n\n{secret['text']}",
            show_alert=True
        )

        logger.info(f"[{chat_id}] {user_name} maxfiy xabarni 10 coinga sotib oldi!")

        # Tugmani yangilaymiz: endi sotib olindi deb ko'rinadi
        buyer_disp = f"@{username}" if username else user_name
        new_keyboard = [
            [InlineKeyboardButton("📩 Xabarni o'qish", callback_data=f"read:{secret_id}")],
            [InlineKeyboardButton(f"🔒 Sotib olindi ({buyer_disp})", callback_data=f"bought:{secret_id}")]
        ]
        try:
            await query.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(new_keyboard))
        except Exception:
            pass
        return

    if data.startswith("bought:"):
        await query.answer(
            "Bu xabarni boshqa kishi sotib olib bo'ldi. Limit tugagan (faqat 1 kishi sotib olishi mumkin edi)!",
            show_alert=True
        )
        return

    # ── 5. Admin Rejim sozlamalari ──
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        user_is_admin = member.status in ["administrator", "creator"] or user_id in ADMIN_IDS
    except Exception:
        user_is_admin = user_id in ADMIN_IDS

    if data == "help":
        await query.answer()
        text = (
            "🆘 <b>Yordam</b>\n\n"
            "• <code>/only @username</code> — Faqat shu odamga ko'rinsin!\n"
            "• <code>/quiz</code> — Viktorina o'ynab coin ishlash\n"
            "• <code>/balans</code> — Coiningizni ko'rish\n"
            "• <code>/clear</code> — Barcha cheklovlarni o'chirish"
        )
        await query.message.edit_text(text, parse_mode="HTML")
        return

    if not user_is_admin:
        await query.answer("❌ Faqat adminlar o'zgartira oladi!", show_alert=True)
        return

    if data.startswith("mode:"):
        mode_key = data.split(":", 1)[1]

        if mode_key == "off":
            db.set_chat_active(chat_id, False)
            await query.answer("🔴 Shifrlash o'chirildi!")
        elif mode_key == "on":
            db.set_chat_active(chat_id, True)
            await query.answer("🟢 Shifrlash yoqildi!")
        else:
            db.set_chat_mode(chat_id, mode_key)
            db.set_chat_active(chat_id, True)
            if mode_key == "custom":
                context.chat_data["awaiting_custom"] = True
                await query.answer()
                await query.message.edit_text(
                    "✏️ <b>Custom rejim</b>\n\n"
                    "Matn yozing — shu matn ruxsati bo'lmagan odamga ko'rinadi:\n"
                    "<i>(Masalan: Bu xabar sizga yopiq 🔒)</i>",
                    parse_mode="HTML"
                )
                return
            await query.answer(f"✅ Rejim o'rnatildi: {mode_key}")

        try:
            keyboard = _build_mode_keyboard(chat_id)
            active = db.is_chat_active(chat_id)
            current = db.get_chat_mode(chat_id)
            kb_status = "🟢 Faol" if active else "🔴 O'chirilgan"
            await query.message.edit_text(
                f"🎭 <b>Soxta ko'rinish rejimini tanlang:</b>\n\n"
                f"{kb_status} | Joriy: <b>{current or 'Emoji'}</b>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════════
#  XABAR HANDLER — Asosiy Logika
# ══════════════════════════════════════════════════════════

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guruhdagi xabarlarni tutib qayta ishlaydi."""
    msg = update.message
    if not msg or not msg.text:
        return

    chat_id = update.effective_chat.id
    user = update.effective_user
    text = msg.text

    if text.startswith("/"):
        return

    # Custom matn o'rnatish
    if context.chat_data.get("awaiting_custom"):
        db.set_custom_text(chat_id, text)
        context.chat_data["awaiting_custom"] = False
        await msg.reply_text(
            f"✅ Custom matn saqlandi:\n\n<b>{text}</b>\n\n"
            "Endi ruxsat berilmagan odamga shu matn ko'rinadi!",
            parse_mode="HTML"
        )
        return

    if not db.is_chat_active(chat_id):
        return

    sender_name = user.first_name or "Foydalanuvchi"
    target_mode = db.get_target_mode(chat_id)

    # ── Agar Target Mode faol bo'lsa (ONLY yoki HIDE) ──
    if target_mode in ["only", "hide"]:
        # Asl xabarni guruhdan o'chirish
        await delete_original(update, context)

        secret_id = uuid.uuid4().hex[:8]
        SECRET_MESSAGES.set(secret_id, {
            "text": text,
            "sender_name": sender_name,
            "sender_id": user.id,
            "chat_id": chat_id,
            "target_mode": target_mode,
            "buyers": set()
        })

        # Ikkita tugma: O'qish va Coinga ochish!
        keyboard = [
            [InlineKeyboardButton("📩 Xabarni o'qish", callback_data=f"read:{secret_id}")],
            [InlineKeyboardButton("🔓 10 🪙 ga sotib olish (1 kishi)", callback_data=f"buy:{secret_id}")]
        ]

        if target_mode == "only":
            users = db.get_only_users(chat_id)
            u_names = ", ".join([f"@{u['username']}" if u.get('username') else u.get('name', '') for u in users])
            caption = f"🔒 <i>Maxfiy xabar (Faqat {u_names} uchun)</i>\n💡 <i>Boshqa bir kishi 10 coinga sotib olishi mumkin!</i>"
        else:
            caption = "🔒 <i>Maxfiy xabar (Cheklangan xabar)</i>"

        sent_text = (
            f"👤 <b>{sender_name}</b> xabar yubordi:\n"
            f"{caption}"
        )

        await context.bot.send_message(
            chat_id=chat_id,
            text=sent_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        logger.info(f"[{chat_id}] Maxfiy xabar yuborildi [{target_mode}] ({secret_id}): {sender_name}")
        return

    # ── Agar hech qanday cheklov qo'yilmagan bo'lsa (Oddiy shifrlash) ──
    mode = db.get_chat_mode(chat_id) or "emoji"
    transformed = mode_manager.transform(text, mode, chat_id, db)
    if transformed is None:
        return

    await delete_original(update, context)

    emoji_prefix = _get_random_emoji()
    final_text = (
        f"👤 <b>{sender_name}</b> yozdi:\n"
        f"{emoji_prefix} {transformed}"
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=final_text,
        parse_mode="HTML"
    )
    logger.info(f"[{chat_id}] {sender_name}: '{text}' → '{transformed}' (rejim: {mode})")


def _get_random_emoji() -> str:
    emojis = ["🔐", "🌀", "🎭", "🔮", "✨", "🎲", "🔄", "💫", "🌈", "🎪"]
    return random.choice(emojis)


# ══════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════

async def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN topilmadi! config.py faylini tekshiring.")
        return

    logger.info("🚀 Shifr Bot ishga tushmoqda...")

    from proxy_manager import get_working_proxy
    from telegram.request import HTTPXRequest

    proxy_url = await get_working_proxy(BOT_TOKEN)
    builder = Application.builder().token(BOT_TOKEN)
    if proxy_url:
        logger.info(f"🔗 Bot {proxy_url} orqali ulanmoqda...")
        req = HTTPXRequest(proxy=proxy_url, connect_timeout=15.0, read_timeout=25.0, write_timeout=25.0)
        builder = builder.request(req)
    else:
        logger.info("🔗 Bot to'g'ridan-to'g'ri ulanmoqda...")

    app = builder.build()

    # Buyruqlar
    app.add_handler(CommandHandler("start",     start_command))
    app.add_handler(CommandHandler("help",      help_command))
    app.add_handler(CommandHandler("quiz",      quiz_command))
    app.add_handler(CommandHandler("savol",     quiz_command))
    app.add_handler(CommandHandler("balans",    balance_command))
    app.add_handler(CommandHandler("coin",      balance_command))
    app.add_handler(CommandHandler("top",       top_command))
    app.add_handler(CommandHandler("pay",       pay_command))

    app.add_handler(CommandHandler("only",      only_command))
    app.add_handler(CommandHandler("hide",      hide_command))
    app.add_handler(CommandHandler("clear",     clear_command))
    app.add_handler(CommandHandler("reset",     clear_command))
    app.add_handler(CommandHandler("status",    status_command))
    app.add_handler(CommandHandler("setmode",   setmode_command))
    app.add_handler(CommandHandler("on",        on_command))
    app.add_handler(CommandHandler("off",       off_command))

    # Callback
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Xabarlar
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        message_handler
    ))

    logger.info("✅ Bot tayyor! Polling boshlanmoqda...")

    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
