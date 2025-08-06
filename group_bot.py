"""
Главный файл группового бота для Dota 2
Использует модульную архитектуру
"""
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import TELEGRAM_TOKEN
from statistics import (
    get_user_stats, update_user_stats, get_leaderboard, get_lvm_leaderboard,
    get_group_summary, get_user_display_name, find_user_by_username
)
from fun_commands import get_funny_response

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
CHOOSING_PARTY_SIZE, CHOOSING_LANE = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    keyboard = [
        [InlineKeyboardButton("📊 Статистика группы", callback_data="stats")],
        [InlineKeyboardButton("🎯 Случайный вызов", callback_data="challenge")],
        [InlineKeyboardButton("🎪 Забавные команды", callback_data="fun")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "🎮 *Добро пожаловать в Dota 2 Group Bot!*\n\n"
        "Выберите, что хотите сделать:"
    )
    
    # Проверяем, откуда вызвана функция
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "stats":
        await show_group_stats(query)
    elif query.data == "challenge":
        await show_random_challenge(query)
    elif query.data == "fun":
        await show_fun_menu(query)
    elif query.data.startswith("fun_"):
        await handle_fun_command(query)
    elif query.data == "back":
        # Просто вызываем start с правильным контекстом
        await start(update, context)

async def show_group_stats(query):
    """Показать статистику группы"""
    try:
        logger.info("Начинаем загрузку статистики...")
        summary = get_group_summary()
        logger.info(f"Сводка получена: {summary}")
        
        leaderboard = get_leaderboard()
        logger.info(f"Лидерборд получен: {len(leaderboard)} игроков")
        
        lvm_leaderboard = get_lvm_leaderboard()
        logger.info(f"LVM лидерборд получен: {len(lvm_leaderboard)} игроков")
        
        # Формируем текст статистики (используем обычный Markdown)
        stats_text = (
            f"📊 *Статистика группы:*\n\n"
            f"🎮 Всего игр: {summary['total_games']}\n"
            f"🏆 Побед: {summary['total_wins']}\n"
            f"😔 Поражений: {summary['total_losses']}\n"
            f"📈 Винрейт группы: {summary['group_winrate']:.1f}%\n"
            f"👥 Активных игроков: {summary['active_players']}\n"
            f"⭐ Всего MVP: {summary['total_mvp']}\n"
            f"💀 Всего LVM: {summary['total_lvm']}\n\n"
        )
        
        logger.info("Базовый текст статистики сформирован")
        
        # Добавляем топ игроков
        if leaderboard:
            stats_text += "🏆 *Топ игроков:*\n"
            for i, (user_id, stats) in enumerate(leaderboard[:5], 1):
                display_name = get_user_display_name(user_id)
                logger.info(f"Обрабатываем игрока {i}: {display_name}")
                # Простое отображение без сложного экранирования
                stats_text += f"{i}. {display_name}: {stats['winrate']:.1f}% ({stats['total_games']} игр)\n"
        
        logger.info("Топ игроков добавлен")
        
        # Добавляем LVM список
        if lvm_leaderboard:
            stats_text += "\n💀 *LVM список:*\n"
            for i, (user_id, stats) in enumerate(lvm_leaderboard[:5], 1):
                display_name = get_user_display_name(user_id)
                logger.info(f"Обрабатываем LVM игрока {i}: {display_name}")
                # Простое отображение без сложного экранирования
                stats_text += f"{i}. {display_name}: {stats['lvm_count']} LVM ({stats['total_games']} игр)\n"
        
        logger.info("LVM список добавлен")
        logger.info(f"Итоговый текст: {stats_text[:200]}...")
        
        keyboard = [
            [InlineKeyboardButton("🔄 Обновить", callback_data="stats")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.info("Статистика успешно отправлена")
    except Exception as e:
        logger.error(f"Ошибка при показе статистики: {e}")
        logger.error(f"Тип ошибки: {type(e).__name__}")
        import traceback
        logger.error(f"Полный traceback: {traceback.format_exc()}")
        await query.edit_message_text(
            "❌ Произошла ошибка при загрузке статистики. Попробуйте еще раз.",
            parse_mode='Markdown'
        )

async def show_random_challenge(query):
    """Показать случайный вызов для Dota 2"""
    challenges = [
        "🎯 **Вызов: Только поддержка!**\nИграйте только героями поддержки. Никаких керри!",
        "⚡ **Вызов: Быстрая игра!**\nПопробуйте закончить игру до 20 минуты. Агрессивный стиль!",
        "🛡️ **Вызов: Танк-команда!**\nВыберите только героев с высоким HP и броней. Никаких стеков!",
        "🎪 **Вызов: Рандом герои!**\nКаждый выбирает случайного героя. Никаких претензий!",
        "🔥 **Вызов: Только магический урон!**\nИграйте героями с магическим уроном. Никаких физических атак!",
        "⚔️ **Вызов: Дуэли!**\nКаждый должен взять героя-дуэлянта (PA, Jugg, LC, etc.)",
        "🌙 **Вызов: Ночные герои!**\nИграйте только героями, которые лучше работают ночью",
        "☀️ **Вызов: Дневные герои!**\nИграйте только героями, которые лучше работают днем",
        "🎭 **Вызов: Один стиль!**\nВсе берут героев одного стиля (gank, push, farm, etc.)",
        "🔄 **Вызов: Смена ролей!**\nКерри играет поддержкой, саппорт играет керри!",
        "🎲 **Вызов: Случайная линия!**\nКаждый играет на случайной линии, не своей обычной",
        "💎 **Вызов: Редкие герои!**\nИграйте только героями, которых редко выбирают",
        "🏆 **Вызов: Популярные герои!**\nИграйте только самыми популярными героями",
        "⚡ **Вызов: Быстрый фарм!**\nПопробуйте набрать 1000 GPM к 15 минуте",
        "🛡️ **Вызов: Защитная игра!**\nИграйте максимально безопасно, минимум смертей"
    ]
    
    import random
    challenge = random.choice(challenges)
    
    keyboard = [
        [InlineKeyboardButton("🎯 Новый вызов", callback_data="challenge")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        challenge,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_fun_menu(query):
    """Показать меню забавных команд"""
    keyboard = [
        [InlineKeyboardButton("🔥 Роуст", callback_data="fun_roast")],
        [InlineKeyboardButton("🌟 Похвала", callback_data="fun_praise")],
        [InlineKeyboardButton("💪 Мотивация", callback_data="fun_motivate")],
        [InlineKeyboardButton("😤 Обвинение", callback_data="fun_blame")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎪 *Забавные команды:*\n\nВыберите тип реакции:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_fun_command(query):
    """Обработка забавных команд"""
    command_type = query.data.split("_")[1]
    response = get_funny_response(command_type)
    
    keyboard = [
        [InlineKeyboardButton("🔄 Еще раз", callback_data=f"fun_{command_type}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="fun")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"{response}",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Команды для статистики
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для показа статистики"""
    try:
        summary = get_group_summary()
        leaderboard = get_leaderboard()
        lvm_leaderboard = get_lvm_leaderboard()
        
        # Формируем текст статистики
        stats_text = (
            f"📊 *Статистика группы:*\n\n"
            f"🎮 Всего игр: {summary['total_games']}\n"
            f"🏆 Побед: {summary['total_wins']}\n"
            f"😔 Поражений: {summary['total_losses']}\n"
            f"📈 Винрейт группы: {summary['group_winrate']:.1f}%\n"
            f"👥 Активных игроков: {summary['active_players']}\n"
            f"⭐ Всего MVP: {summary['total_mvp']}\n"
            f"💀 Всего LVM: {summary['total_lvm']}\n\n"
        )
        
        # Добавляем топ игроков
        if leaderboard:
            stats_text += "🏆 *Топ игроков:*\n"
            for i, (user_id, stats) in enumerate(leaderboard[:5], 1):
                display_name = get_user_display_name(user_id)
                stats_text += f"{i}. {display_name}: {stats['winrate']:.1f}% ({stats['total_games']} игр)\n"
        
        # Добавляем LVM список
        if lvm_leaderboard:
            stats_text += "\n💀 *LVM список:*\n"
            for i, (user_id, stats) in enumerate(lvm_leaderboard[:5], 1):
                display_name = get_user_display_name(user_id)
                stats_text += f"{i}. {display_name}: {stats['lvm_count']} LVM ({stats['total_games']} игр)\n"
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Ошибка при показе статистики: {e}")
        await update.message.reply_text("❌ Произошла ошибка при загрузке статистики. Попробуйте еще раз.")

async def win_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для записи победы"""
    user = update.effective_user
    user_id = str(user.id)
    username = user.username
    first_name = user.first_name
    
    update_user_stats(user_id, 'win', username=username, first_name=first_name)
    
    response = "🏆 Победа записана! Отличная игра!"
    
    await update.message.reply_text(response)

async def lose_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /lose"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    
    update_user_stats(user_id, 'loss', username=username, first_name=first_name)
    
    response = "😔 Поражение записано. Не расстраивайтесь, в следующий раз повезет!"
    
    await update.message.reply_text(response)

async def mvp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /mvp"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    
    # Проверяем, есть ли аргумент @username
    if context.args and context.args[0].startswith('@'):
        target_username = context.args[0]
        target_user_id = find_user_by_username(target_username)
        if target_user_id:
            user_id = target_user_id
            target_user_stats = get_user_stats(target_user_id)
            username = target_user_stats.get('username')
            first_name = target_user_stats.get('first_name')
            response = f"⭐ MVP назначен игроку {target_username}! Отличная игра!"
        else:
            response = f"❌ Пользователь {target_username} не найден в статистике."
            await update.message.reply_text(response)
            return
    else:
        response = "⭐ Вы получили MVP! Отличная игра!"
    
    update_user_stats(user_id, 'mvp', username=username, first_name=first_name)
    await update.message.reply_text(response)

async def lvm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /lvm"""
    user_id = str(update.effective_user.id)
    username = update.effective_user.username
    first_name = update.effective_user.first_name
    
    # Проверяем, есть ли аргумент @username
    if context.args and context.args[0].startswith('@'):
        target_username = context.args[0]
        target_user_id = find_user_by_username(target_username)
        if target_user_id:
            user_id = target_user_id
            target_user_stats = get_user_stats(target_user_id)
            username = target_user_stats.get('username')
            first_name = target_user_stats.get('first_name')
            response = f"💀 LVM назначен игроку {target_username}. Попробуйте лучше в следующий раз!"
        else:
            response = f"❌ Пользователь {target_username} не найден в статистике."
            await update.message.reply_text(response)
            return
    else:
        response = "💀 Вы получили LVM. Попробуйте лучше в следующий раз!"
    
    update_user_stats(user_id, 'lvm', username=username, first_name=first_name)
    await update.message.reply_text(response)

# Забавные команды с поддержкой @username
async def roast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда роуста с поддержкой @username"""
    if context.args:
        target_username = context.args[0].replace("@", "")
        response = get_funny_response("roast", target_username)
    else:
        response = get_funny_response("roast")
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def praise_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда похвалы с поддержкой @username"""
    if context.args:
        target_username = context.args[0].replace("@", "")
        response = get_funny_response("praise", target_username)
    else:
        response = get_funny_response("praise")
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def motivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда мотивации с поддержкой @username"""
    if context.args:
        target_username = context.args[0].replace("@", "")
        response = get_funny_response("motivate", target_username)
    else:
        response = get_funny_response("motivate")
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def blame_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда обвинения с поддержкой @username"""
    if context.args:
        target_username = context.args[0].replace("@", "")
        response = get_funny_response("blame", target_username)
    else:
        response = get_funny_response("blame")
    
    await update.message.reply_text(response, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
🎮 *Dota 2 Group Bot - Справка*

*Основные команды:*
/start - Главное меню
/help - Эта справка
/stats - Показать статистику группы

*Статистика:*
/win - Записать победу
/lose - Записать поражение
/mvp [@username] - Назначить MVP (себе или другому игроку)
/lvm [@username] - Назначить LVM (себе или другому игроку)

*Забавные команды:*
/roast [@username] - Роуст (себя или другого игрока)
/praise [@username] - Похвала (себя или другого игрока)
/motivate [@username] - Мотивация (себя или другого игрока)
/blame [@username] - Обвинение (себя или другого игрока)

*Примеры:*
/mvp @username - назначить MVP другому игроку
/roast @username - роустнуть конкретного игрока
/stats - посмотреть статистику группы

🎯 Используйте кнопки в меню для быстрого доступа к функциям!
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

def main():
    """Главная функция"""
    if not TELEGRAM_TOKEN:
        logger.error("Не установлен TELEGRAM_TOKEN!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("win", win_command))
    application.add_handler(CommandHandler("lose", lose_command))
    application.add_handler(CommandHandler("mvp", mvp_command))
    application.add_handler(CommandHandler("lvm", lvm_command))
    
    # Забавные команды
    application.add_handler(CommandHandler("roast", roast_command))
    application.add_handler(CommandHandler("praise", praise_command))
    application.add_handler(CommandHandler("motivate", motivate_command))
    application.add_handler(CommandHandler("blame", blame_command))
    
    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main() 