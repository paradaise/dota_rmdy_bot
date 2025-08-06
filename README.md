# 🎮 Rmdy Lobby Stats Bot

<img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python" alt="Python"> 
<img src="https://img.shields.io/badge/Telegram%20Bot-20.0+-green?logo=telegram" alt="Telegram Bot"> 
<img src="https://img.shields.io/github/license/victor_gogolev/rmdy-lobby-bot?color=orange" alt="License">

Бот для отслеживания статистики игрового лобби с функцией назначения MVP/LVP игрокам и развлекательными командами.

![Пример работы бота](https://i.imgur.com/JK7w3E2.png) _(замените на реальный скриншот)_

## ✨ Особенности

- 📊 **Статистика лобби** (победы/поражения, винрейт)
- 🏆 **Система наград** (MVP/LVP с топом игроков)
- 🎪 **Развлекательные команды** (токсичные комментарии, мотивация и др.)
- 🎮 **Простое управление** через команды и инлайн-кнопки
- ⚡ **Быстрая работа** с сохранением данных в памяти

## 🛠 Установка и запуск

1. Клонируйте репозиторий:

```bash
git clone https://github.com/yourusername/rmdy-lobby-bot.git
cd rmdy-lobby-bot
Установите зависимости:

bash
pip install -r requirements.txt
Создайте файл .env:

ini
TELEGRAM_BOT_TOKEN=ваш_токен_бота
Запустите бота:

bash
python main.py
📋 Список команд
Основные команды
Команда	Описание	Пример
/start	Запуск бота с меню	/start
/help	Справка по командам	/help
/stats	Показать статистику лобби	/stats
/win	Записать победу лобби	/win
/lose	Записать поражение лобби	/lose
Награды игрокам
Команда	Описание	Пример
/mvp @user	Назначить MVP игроку	/mvp @pro_player
/lvp @user	Назначить LVP игроку	/lvp @noob
Развлекательные
Команда	Эффект	Пример
/toxic @user	Отправить токсичный комментарий	/toxic @raging_guy
/tip @user	Дать полезный совет	/tip @newbie
/motivate @user	Мотивировать игрока	/motivate @friend
/blame @user	Обвинить игрока в поражении	/blame @leaver
🧩 Структура проекта
text
rmdy-lobby-bot/
├── main.py            # Основной код бота
├── statistics.py      # Логика статистики
├── fun_commands.py    # Развлекательные команды
├── .env               # Конфигурация
├── requirements.txt   # Зависимости
└── README.md          # Документация
📊 Пример вывода
text
📊 Статистика лобби

🎮 Всего игр: 42
🏆 Побед: 25 (59.5%)
💀 Поражений: 17

⭐ Топ-3 MVP:
1. @pro_gamer - 8 раз
2. @team_lead - 5 раз
3. @support - 3 раза

💀 Топ-3 LVP:
1. @angry_noob - 10 раз
2. @afk_player - 7 раз
3. @feeders - 5 раз
🌟 Контакты
✉️ Email: victor@gogolev.com

💬 Telegram: @victor_gogolev

💻 GitHub: victor_gogolev

📜 Лицензия: MIT
👨‍💻 Автор: Виктор Гоголев
🔄 Версия: 1.0.0
📅 Год: 2023

text

Ключевые улучшения:
1. Добавлены разделители между секциями
2. Улучшена таблица команд (разделена на логические группы)
3. Добавлены примеры вывода статистики
4. Исправлены emoji-форматирования
5. Добавлены реальные примеры команд
6. Улучшена структура контактной информации

Для использования:
1. Сохраните как `README.md` в корне проекта
2. Замените `yourusername` на ваш GitHub
3. Добавьте реальные скриншоты вместо примера
4. Обновите контактные данные при необходимости
```
