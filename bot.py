"""
╔══════════════════════════════════════════════════════════╗
║              SHIFR BOT - Guruh Shifrlash Boti            ║
║   1) Faqat bitta odamga ko'rinishi (/only)              ║
║   2) Bitta odamga ko'rinmasligi (/hide)                  ║
║   3) Umumiy shifrlash                                    ║
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

    if chat_type == "private":
        text = (
            f"👋 Salom, <b>{user.first_name}</b>!\n\n"
            "🔐 Men <b>Shifr Bot</b>man — guruhda xabarlaringizni faqat kerakli odamga ko'rsatib, "
            "boshqalarga smaylik/soxta matn qilib ko'rsatuvchi aqlli botman!\n\n"
            "✨ <b>2 ta eng asosiy imkoniyat:</b>\n"
            "1️⃣ <b>Faqat bitta odamga ko'rinsin:</b>\n"
            "   <code>/only @username</code> (yoki xabariga reply qilib <code>/only</code>)\n"
            "   <i>(Xabarni FAQAT shu odam va siz o'qiysiz, qolgan hamma bolalarga smaylik ko'rinadi!)</i>\n\n"
            "2️⃣ <b>Bitta odamdan yashirilsin:</b>\n"
            "   <code>/hide @username</code> (yoki xabariga reply qilib <code>/hide</code>)\n"
            "   <i>(Qolgan hamma bolalar o'qiydi, FAQAT shu odamga smaylik ko'rinadi!)</i>\n\n"
            "📋 <b>Boshqa buyruqlar:</b>\n"
            "• <code>/clear</code> — Barcha cheklovlarni o'chirish\n"
            "• <code>/status</code> — Guruhdagi joriy holat\n"
            "• <code>/setmode</code> — Soxta matn turi (Emoji, Zalgo, Morse, Meow...)"
        )
        keyboard = [[
            InlineKeyboardButton("➕ Guruhga qo'shish", url=f"https://t.me/{context.bot.username}?startgroup=start"),
            InlineKeyboardButton("📋 Yordam", callback_data="help")
        ]]
        await update.message.reply_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "✅ <b>Shifr Bot</b> guruhda tayyor!\n\n"
            "🎯 <b>Faqat bitta bolaga ko'rinishi uchun:</b> unga reply qilib <code>/only</code> yoki <code>/only @username</code> yozing.\n"
            "🚫 <b>Bitta boladan yashirish uchun:</b> unga reply qilib <code>/hide</code> yozing.",
            parse_mode="HTML"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam."""
    text = (
        "🆘 <b>QANDAY ISHLATILADI?</b>\n\n"
        "🎯 <b>1. Faqat 1 kishiga ko'rinsin (qolganlarga ko'rinmasin):</b>\n"
        "• <code>/only @username</code>\n"
        "• Yoki o'sha odamning xabariga reply qilib <code>/only</code>\n"
        "<i>Guruhdagi 5 kishidan faqat shu odam va siz o'qiysiz, qolgan 3-4 kishiga smaylik ko'rinadi!</i>\n\n"
        "🚫 <b>2. Bitta odamga ko'rinmasin (qolganlarga ko'rinsin):</b>\n"
        "• <code>/hide @username</code>\n"
        "• Yoki o'sha odamning xabariga reply qilib <code>/hide</code>\n"
        "<i>Qolgan hamma o'qiydi, faqat shu odamga smaylik ko'rinadi!</i>\n\n"
        "🔄 <b>3. Cheklovni tozalash:</b>\n"
        "• <code>/clear</code> yoki <code>/reset</code> — normal holatga qaytarish\n\n"
        "⚙️ <b>Sozlamalar:</b>\n"
        "• <code>/status</code> — Kim tanlangani va joriy rejim\n"
        "• <code>/setmode</code> — Smaylik/soxta matn turini tanlash"
    )
    await update.message.reply_text(text, parse_mode="HTML")


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
            "1️⃣ Xabar faqat kimga ko'rinishi kerak bo'lsa, o'sha odamning xabariga reply qilib <code>/only</code> deb yozing\n"
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
        f"Guruhdagi qolgan barcha bolalarga esa <b>faqat smaylik/soxta matn</b> ko'rinadi! 🔒\n\n"
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
        "Guruh odatiy holatga qaytdi. Yangi cheklov qo'yish uchun:\n"
        "• <code>/only @username</code> — Faqat 1 kishiga ko'rsatish\n"
        "• <code>/hide @username</code> — 1 kishidan yashirish",
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
        holat_target = f"🎯 <b>Faqat {u_names} ga ko'rinadi</b> (boshqalarga smaylik)"
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
#  CALLBACK QUERY HANDLER (Tugmalar & Maxfiy Xabarlar)
# ══════════════════════════════════════════════════════════

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tugma bosilganda ishlaydi."""
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    username = query.from_user.username

    # ── 1. Maxfiy xabarni ochish ──
    if data.startswith("read:"):
        secret_id = data.split(":", 1)[1]
        secret = SECRET_MESSAGES.get(secret_id)

        if not secret:
            await query.answer("⚠️ Bu xabar eskirgan.", show_alert=True)
            return

        target_mode = secret.get("target_mode", "none")
        sender_id = secret.get("sender_id")
        is_sender = (user_id == sender_id)

        # Ruxsat tekshiruvi:
        can_read = False

        if is_sender:
            can_read = True
        elif target_mode == "only":
            # Faqat tanlangan odamga ochiq
            can_read = db.is_user_in_only_list(chat_id, user_id, username)
        elif target_mode == "hide":
            # Tanlangan odamdan boshqa hammaga ochiq
            can_read = not db.is_user_hidden(chat_id, user_id, username)
        else:
            can_read = True

        if can_read:
            # Haqiqiy xabar ochiladi!
            await query.answer(
                f"📩 Asl xabar:\n\n{secret['text']}",
                show_alert=True
            )
            logger.info(f"[{chat_id}] {query.from_user.first_name} asl xabarni o'qidi.")
        else:
            # Soxta smaylik / matn ko'rsatiladi!
            mode = db.get_chat_mode(chat_id) or "emoji"
            fake_content = mode_manager.transform(secret["text"], mode, chat_id, db)
            await query.answer(
                f"🎭 Siz uchun bu xabar:\n\n{fake_content}",
                show_alert=True
            )
            logger.info(f"[{chat_id}] {query.from_user.first_name} ga soxta xabar ko'rsatildi.")
        return

    # ── 2. Admin Rejim sozlamalari ──
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
            "• <code>/hide @username</code> — Shu odamga ko'rinmasin!\n"
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
            "target_mode": target_mode
        })

        keyboard = [[
            InlineKeyboardButton("📩 Xabarni o'qish", callback_data=f"read:{secret_id}")
        ]]

        if target_mode == "only":
            users = db.get_only_users(chat_id)
            u_names = ", ".join([f"@{u['username']}" if u.get('username') else u.get('name', '') for u in users])
            caption = f"🔒 <i>Maxfiy xabar (Faqat {u_names} uchun)</i>"
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
