"""
Модуль для работы со статистикой игроков и группы
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

# Файл для хранения статистики
STATS_FILE = 'group_stats.json'

# Глобальные переменные для хранения данных
user_data = {}
group_stats = {}

def load_stats():
    """Загрузка статистики из файла"""
    global user_data, group_stats
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                user_data = data.get('users', {})
                group_stats = data.get('group', {})
        except Exception as e:
            print(f"Ошибка загрузки статистики: {e}")
            user_data = {}
            group_stats = {}

def save_stats():
    """Сохранение статистики в файл"""
    data = {
        'users': user_data,
        'group': group_stats
    }
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения статистики: {e}")

def get_user_stats(user_id: str, username: str = None, first_name: str = None) -> Dict[str, Any]:
    """Получение статистики пользователя"""
    if user_id not in user_data:
        user_data[user_id] = {
            'wins': 0, 'losses': 0, 'mvp_count': 0, 'lvm_count': 0,
            'role_stats': {},
            'last_game': None, 'join_date': datetime.now().isoformat(),
            'username': username, 'first_name': first_name
        }
    else:
        # Обновляем информацию пользователя если изменилась
        if username and user_data[user_id].get('username') != username:
            user_data[user_id]['username'] = username
        if first_name and user_data[user_id].get('first_name') != first_name:
            user_data[user_id]['first_name'] = first_name
    
    return user_data[user_id]

def update_user_stats(user_id: str, stat_type: str, value: Any = None, username: str = None, first_name: str = None):
    """Обновление статистики пользователя"""
    stats = get_user_stats(user_id, username, first_name)
    
    if stat_type == 'win':
        stats['wins'] += 1
        stats['last_game'] = datetime.now().isoformat()
        group_stats['group_wins'] = group_stats.get('group_wins', 0) + 1
    elif stat_type == 'loss':
        stats['losses'] += 1
        stats['last_game'] = datetime.now().isoformat()
        group_stats['group_losses'] = group_stats.get('group_losses', 0) + 1
    elif stat_type == 'mvp':
        stats['mvp_count'] += 1
        group_stats['total_mvp'] = group_stats.get('total_mvp', 0) + 1
    elif stat_type == 'lvm':
        stats['lvm_count'] += 1
        group_stats['total_lvm'] = group_stats.get('total_lvm', 0) + 1
    elif stat_type == 'role':
        if value:
            role = value.lower()
            if role not in stats['role_stats']:
                stats['role_stats'][role] = {'wins': 0, 'losses': 0}
            stats['role_stats'][role]['wins'] += 1
    
    save_stats()

def get_user_display_name(user_id: str) -> str:
    """Получение отображаемого имени пользователя"""
    if user_id not in user_data:
        return f"Игрок {user_id}"
    
    user_info = user_data[user_id]
    if user_info.get('username'):
        return f"@{user_info['username']}"
    elif user_info.get('first_name'):
        return user_info['first_name']
    else:
        return f"Игрок {user_id}"

def get_leaderboard() -> List[Tuple[str, Dict[str, Any]]]:
    """Получение таблицы лидеров"""
    users = []
    for user_id, stats in user_data.items():
        total_games = stats['wins'] + stats['losses']
        if total_games > 0:
            winrate = (stats['wins'] / total_games) * 100
            users.append((user_id, {**stats, 'winrate': winrate, 'total_games': total_games}))
    
    # Сортировка по винрейту, затем по количеству игр
    users.sort(key=lambda x: (x[1]['winrate'], x[1]['total_games']), reverse=True)
    return users

def get_lvm_leaderboard() -> List[Tuple[str, Dict[str, Any]]]:
    """Получение таблицы LVM (Least Valuable Players)"""
    users = []
    for user_id, stats in user_data.items():
        total_games = stats['wins'] + stats['losses']
        if total_games > 0 and stats.get('lvm_count', 0) > 0:
            lvm_rate = (stats['lvm_count'] / total_games) * 100
            users.append((user_id, {**stats, 'lvm_rate': lvm_rate, 'total_games': total_games}))
    
    # Сортировка по количеству LVM, затем по общему количеству игр
    users.sort(key=lambda x: (x[1]['lvm_count'], x[1]['total_games']), reverse=True)
    return users

def get_group_summary() -> Dict[str, Any]:
    """Получение сводки по группе"""
    total_wins = sum(stats['wins'] for stats in user_data.values())
    total_losses = sum(stats['losses'] for stats in user_data.values())
    total_games = total_wins + total_losses
    
    return {
        'total_games': total_games,
        'total_wins': total_wins,
        'total_losses': total_losses,
        'group_winrate': (total_wins / total_games * 100) if total_games > 0 else 0,
        'active_players': len([u for u in user_data.values() if u['wins'] + u['losses'] > 0]),
        'total_players': len(user_data),
        'total_mvp': group_stats.get('total_mvp', 0),
        'total_lvm': group_stats.get('total_lvm', 0)
    }

def get_weekly_stats() -> Dict[str, Any]:
    """Получение недельной статистики"""
    week_ago = datetime.now() - timedelta(days=7)
    weekly_wins = 0
    weekly_losses = 0
    
    for stats in user_data.values():
        if stats.get('last_game'):
            last_game = datetime.fromisoformat(stats['last_game'])
            if last_game >= week_ago:
                weekly_wins += stats.get('weekly_wins', 0)
                weekly_losses += stats.get('weekly_losses', 0)
    
    total_weekly = weekly_wins + weekly_losses
    return {
        'weekly_wins': weekly_wins,
        'weekly_losses': weekly_losses,
        'weekly_winrate': (weekly_wins / total_weekly * 100) if total_weekly > 0 else 0
    }

def find_user_by_username(username: str) -> str:
    """Поиск пользователя по username"""
    username = username.replace('@', '')
    for user_id, stats in user_data.items():
        if stats.get('username') == username:
            return user_id
    return None

# Загружаем статистику при импорте модуля
load_stats() 