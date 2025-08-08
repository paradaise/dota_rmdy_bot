import json
import os
from datetime import datetime
from typing import Dict, Any, List, Tuple

STATS_FILE = "group_stats.json"

# Глобальные данные
lobby_stats = {"total_games": 0, "wins": 0, "losses": 0}

player_stats = {}  # {user_id: {mvp_count: X, lvp_count: Y, username: str}}


def load_stats():
    global lobby_stats, player_stats
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                lobby_stats = data.get(
                    "lobby_stats", {"total_games": 0, "wins": 0, "losses": 0}
                )
                player_stats = data.get("player_stats", {})
        except Exception as e:
            print(f"Ошибка загрузки: {e}")


def save_stats():
    data = {"lobby_stats": lobby_stats, "player_stats": player_stats}
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def register_player(user_id: str, username: str):
    if user_id not in player_stats:
        player_stats[user_id] = {
            "mvp_count": 0,
            "lvp_count": 0,
            "username": username,
            "first_seen": datetime.now().isoformat(),
        }
    elif username and player_stats[user_id]["username"] != username:
        player_stats[user_id]["username"] = username
    return player_stats[user_id]


def record_game_result(is_win: bool):
    lobby_stats["total_games"] += 1
    if is_win:
        lobby_stats["wins"] += 1
    else:
        lobby_stats["losses"] += 1
    save_stats()


def add_mvp(username: str):
    user_id = find_player_by_username(username)
    if not user_id:
        user_id = f"user_{len(player_stats)+1}"
        register_player(user_id, username)
    player_stats[user_id]["mvp_count"] += 1
    save_stats()


def add_lvp(username: str):
    user_id = find_player_by_username(username)
    if not user_id:
        user_id = f"user_{len(player_stats)+1}"
        register_player(user_id, username)

    player_stats[user_id]["lvp_count"] += 1
    save_stats()


def find_player_by_username(username: str) -> str:
    username = username.lower().strip("@")
    for user_id, data in player_stats.items():
        if data.get("username", "").lower().strip("@") == username:
            return user_id
    return None


def get_player_display_name(user_id: str) -> str:
    player = player_stats.get(user_id, {})
    return f"@{player['username']}" if player.get("username") else f"Игрок {user_id}"


def get_mvp_leaderboard() -> List[Tuple[str, int]]:
    return sorted(
        [
            (data["username"], data["mvp_count"])
            for data in player_stats.values()
            if data.get("mvp_count", 0) > 0
        ],
        key=lambda x: x[1],
        reverse=True,
    )[:10]


def get_lvp_leaderboard() -> List[Tuple[str, int]]:
    return sorted(
        [
            (data["username"], data["lvp_count"])
            for data in player_stats.values()
            if data.get("lvp_count", 0) > 0
        ],
        key=lambda x: x[1],
        reverse=True,
    )[:10]


def get_lobby_stats() -> Dict[str, Any]:
    winrate = (
        (lobby_stats["wins"] / lobby_stats["total_games"] * 100)
        if lobby_stats["total_games"] > 0
        else 0
    )
    return {**lobby_stats, "winrate": winrate}


load_stats()  # type: ignore
