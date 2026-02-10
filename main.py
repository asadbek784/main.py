# Ushbu kodni ishga tushirishdan oldin `python-telegram-bot` kutubxonasini o'rnating:
# pip install python-telegram-bot
import logging
import os
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# --- YAXSHILANISH: Xabarlar uchun konstantalar ---
# Matnlarni koddan ajratish ularni boshqarishni osonlashtiradi.
START_MESSAGE = (
    fr'Salom, {{user_mention}}\! Men sizning xabarlaringizni qaytarib yuboradigan '
    fr'va ba\'zi qo\'shimcha buyruqlarga ega botman\. '
    fr'Mavjud buyruqlarni ko\'rish uchun /help buyrug\'ini yuboring\.'
)

HELP_MESSAGE = (
    "Mavjud buyruqlar:\n"
    "/start - Bot bilan ishlashni boshlash\n"
    "/help - Ushbu yordam xabarini ko'rsatish\n"
    "/time - Hozirgi server vaqtini ko'rsatish\n"
    "/info - Siz haqingizda ma'lumot berish\n\n"
    "Har qanday matnli xabarni yuborsangiz, men uni qaytaraman."
)

# Loggingni sozlash (bu qism yaxshi edi, o'zgarishsiz qoldirildi)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- YAXSHILANISH: Funksiyalarga docstring va type hintlar qo'shildi ---
def start(update: Update, context: CallbackContext) -> None:
    """/start buyrug'i yuborilganda chaqiriladi."""
    user = update.effective_user
    # Xabarni formatlash uchun f-string va `format` metodidan foydalanish
    message = START_MESSAGE.format(user_mention=user.mention_markdown_v2())
    update.message.reply_markdown_v2(message)


def help_command(update: Update, context: CallbackContext) -> None:
    """/help buyrug'i yuborilganda yordam xabarini ko'rsatadi."""
    update.message.reply_text(HELP_MESSAGE)


def echo(update: Update, context: CallbackContext) -> None:
    """Matnli xabarlarni qaytaradi va xabarlar sonini sanaydi."""
    # --- YAXSHILANISH: context.user_data dan foydalanish ---
    # `user_data` - har bir foydalanuvchi uchun ma'lumot saqlaydigan lug'at.
    if 'message_count' not in context.user_data:
        context.user_data['message_count'] = 0

    context.user_data['message_count'] += 1
    count = context.user_data['message_count']

    message_text = update.message.text
    logger.info(f"User '{update.effective_user.first_name}' sent: {message_text}")

    # Foydalanuvchiga boyitilgan javob yuborish
    response_text = f"Sizning xabaringiz: \"{message_text}\"\nSiz menga {count} ta xabar yubordingiz."
    update.message.reply_text(response_text)


def unknown_command(update: Update, context: CallbackContext) -> None:
    """Noma'lum buyruqlar uchun javob beradi."""
    update.message.reply_text("Kechirasiz, men bunday buyruqni tushunmadim. Yordam uchun /help deb yozing.")


# --- YANGI FUNKSIYALAR ---
def show_time(update: Update, context: CallbackContext) -> None:
    """Hozirgi server vaqtini ko'rsatadi."""
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    update.message.reply_text(f"Hozirgi server vaqti: {current_time}")


def user_info(update: Update, context: CallbackContext) -> None:
    """Foydalanuvchi haqida ma'lumot beradi."""
    user = update.effective_user
    info_text = (
        f"<b>Foydalanuvchi ma'lumotlari:</b>\n"
        f"ID: <code>{user.id}</code>\n"
        f"Ism: {user.first_name}\n"
        f"Familiya: {user.last_name or 'Noma\'lum'}\n"
        f"Username: @{user.username or 'Noma\'lum'}\n"
        f"Til kodi: {user.language_code or 'Noma\'lum'}"
    )
    # --- YAXSHILANISH: ParseMode dan foydalanish ---
    # Matnni formatlash uchun HTML teglardan foydalanish imkonini beradi.
    update.message.reply_html(info_text)


# --- YAXSHILANISH: Xatoliklarni boshqaruvchi (error handler) ---
def error_handler(update: Update, context: CallbackContext) -> None:
    """Botda yuz bergan barcha xatoliklarni log faylga yozadi."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    # Ixtiyoriy: xatolik yuz berganda foydalanuvchiga xabar berish
    # if update and update.effective_message:
    #     update.effective_message.reply_text("Kechirasiz, xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")


def main() -> None:
    """Botni ishga tushiradi."""
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        logger.error("Xatolik: TELEGRAM_BOT_TOKEN nomli muhit o'zgaruvchisi topilmadi.")
        return

    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Buyruqlar uchun handler'lar
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("time", show_time))
    dispatcher.add_handler(CommandHandler("info", user_info))

    # Matnli xabarlar uchun handler
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Noma'lum buyruqlar uchun handler (oxirida turishi kerak)
    dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

    # Xatoliklarni ushlab qolish uchun handler
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    logger.info("Bot ishga tushdi...")
    updater.idle()
    logger.info("Bot to'xtatildi.")


if __name__ == '__main__':
    main()
