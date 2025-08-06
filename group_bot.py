from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from statistics import *
from fun_commands import get_fun_response
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contacts")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    await update.message.reply_text(
        "🎮 <b>Rmdy Lobby Stats Bot</b>\n\n"
        "<i>Пока я отслеживать статистику вашего лобби и назначать MVP/LVP игрокам!</i>\n\n"
        "<b>Используйте /help для списка команд</b>\n",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def win_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    record_game_result(is_win=True)
    await update.message.reply_text(
        "🏆 <b>Легенды! Поздравляю!</b>\n\n"
        "<b>Победа лобби записана!</b>",
        parse_mode='HTML'
    )

async def lose_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    record_game_result(is_win=False)
    await update.message.reply_text(
        "💀 <b>Не расстраивайся!</b>\n\n"
        "<i>MMR приходит и уходит. Самое главное - люди здесь, в этом чате!</i>\n\n"
        "<b>Поражение лобби записано!</b>",
        parse_mode='HTML'
    )

async def handle_award_command(update: Update, context: ContextTypes.DEFAULT_TYPE, award_type: str):
    if not context.args or not context.args[0].startswith('@'):
        await update.message.reply_text(
            f"❌ Укажите ник игрока через @ (например: /{award_type} @username)",
            parse_mode='HTML'
        )
        return
    
    username = context.args[0]
    if award_type == 'mvp':
        add_mvp(username)
        message = f"⭐ <b>MVP назначен {username}!Так держать!</b>"
    else:
        add_lvp(username)
        message = f"💀 <b>LVP назначен {username}!Ебать ты лох xD!</b>"
    
    await update.message.reply_text(message, parse_mode='HTML')

async def mvp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_award_command(update, context, 'mvp')

async def lvp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_award_command(update, context, 'lvp')

async def handle_fun_command(update: Update, context: ContextTypes.DEFAULT_TYPE, cmd_type: str):
    if not context.args or not context.args[0].startswith('@'):
        await update.message.reply_text(
            f"❌ Укажите ник игрока через @ (например: /{cmd_type} @username)",
            parse_mode='HTML'
        )
        return
    
    target = context.args[0]
    response = get_fun_response(cmd_type, target)
    await update.message.reply_text(response, parse_mode='HTML')

async def toxic_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_fun_command(update, context, 'toxic')

async def tip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_fun_command(update, context, 'tip')

async def motivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_fun_command(update, context, 'motivate')

async def blame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_fun_command(update, context, 'blame')

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lobby = get_lobby_stats()
    mvp = get_mvp_leaderboard()
    lvp = get_lvp_leaderboard()
    
    text = (
        "📊 <b>Статистика лобби</b>\n\n"
        "🎮 <i>Всего игр:</i> <b>{}</b>\n"
        "🏆 <i>Побед:</i> <b>{}</b>\n"
        "💀 <i>Поражений:</i> <b>{}</b>\n"
        "📈 <i>Винрейт:</i> <b>{:.1f}%</b>\n"
    ).format(
        lobby['total_games'],
        lobby['wins'],
        lobby['losses'],
        lobby['winrate']
    )
    
    if mvp:
        text += "\n⭐ <b>Топ MVP:</b>\n" + "\n".join(
            "▫️ {}: <b>{}</b>".format(name, count) 
            for name, count in mvp
        )
    
    if lvp:
        text += "\n\n💀 <b>Топ LVP:</b>\n" + "\n".join(
            "▫️ {}: <b>{}</b>".format(name, count) 
            for name, count in lvp
        )
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, parse_mode='HTML')
    else:
        await update.message.reply_text(text, parse_mode='HTML')

async def contacts_command(message, context: ContextTypes.DEFAULT_TYPE):
    contacts_text = (
        "📞 <b>Мои контакты:</b>\n\n"
        "🔹 <a href='https://t.me/victor_gogolev'>Telegram</a>\n"
        "🔹 <a href='https://github.com/paradaise'>GitHub</a>\n"
        "🔹 <a href='https://vk.com/victor_gogolev'>VK</a>\n"
        "🔹 <a href='mailto:vgogolev.business@mail.ru'>Email</a>\n\n"
        "💡 Пишите по любым вопросам!"
    )
    await message.reply_text(contacts_text, parse_mode='HTML', disable_web_page_preview=True)

async def help_command(message, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 <b>Доступные команды:</b>\n\n"
        "🏆 <b>/win</b> - Записать победу лобби\n"
        "💀 <b>/lose</b> - Записать поражение лобби\n\n"
        "⭐ <b>/mvp @ник</b> - Назначить MVP игроку\n"
        "💀 <b>/lvp @ник</b> - Назначить LVP игроку\n\n"
        "🎪 <b>Развлекательные:</b>\n"
        "▫️ <b>/tip @ник</b> - Дать совет игроку\n"
        "▫️ <b>/toxic @ник</b> - Токсичный комментарий\n"
        "▫️ <b>/motivate @ник</b> - Мотивировать игрока\n"
        "▫️ <b>/blame @ник</b> - Обвинить игрока\n\n"
        "📊 <b>/stats</b> - Показать статистику\n"
        "❓ <b>/help</b> - Эта справка"
    )
    await message.reply_text(help_text, parse_mode='HTML')  # Исправлено update.message на message

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):  # Исправлено Update на update
    query = update.callback_query
    await query.answer()
    
    try:
        if query.data == "stats":
            await show_stats(update, context)
        elif query.data == "help":
            await help_command(query.message, context)
        elif query.data == "contacts":
            await contacts_command(query.message, context)
        elif query.data == "back":
            await start(update, context)
    except Exception as e:
        logger.error(f"Ошибка в обработчике кнопок: {e}")
        await query.edit_message_text("❌ Произошла ошибка. Попробуйте еще раз.")

def main():
    load_dotenv()
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        raise ValueError("Не указан TELEGRAM_TOKEN в .env файле")
    
    app = Application.builder().token(token).build()
    
    # Основные команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", lambda u, c: help_command(u.message, c)))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CommandHandler("contacts", lambda u, c: contacts_command(u.message, c)))
    
    # Статистика лобби
    app.add_handler(CommandHandler("win", win_command))
    app.add_handler(CommandHandler("lose", lose_command))
    
    # Награды игрокам
    app.add_handler(CommandHandler("mvp", mvp_command))
    app.add_handler(CommandHandler("lvp", lvp_command))
    
    # Развлекательные команды
    app.add_handler(CommandHandler("toxic", toxic_command))
    app.add_handler(CommandHandler("tip", tip_command))
    app.add_handler(CommandHandler("motivate", motivate_command))
    app.add_handler(CommandHandler("blame", blame_command))
    
    # Обработчики кнопок
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")
    if update.callback_query:
        await update.callback_query.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")
    elif update.message:
        await update.message.reply_text("❌ Произошла ошибка. Попробуйте еще раз.")

if __name__ == '__main__':
    main()