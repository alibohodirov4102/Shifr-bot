"""
Ma'lumotlar bazasi — JSON asosida guruh sozlamalarini saqlaydi
"""

import json
import os
import threading
from config import DATABASE_FILE


class Database:
    """
    Guruh sozlamalarini JSON faylda saqlaydi.
    Thread-safe operatsiyalar uchun lock ishlatiladi.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._file = DATABASE_FILE
        self._data = self._load()

    # ── Yuklash / Saqlash ─────────────────────────────────

    def _load(self) -> dict:
        if os.path.exists(self._file):
            try:
                with open(self._file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save(self):
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def _get_chat(self, chat_id: int) -> dict:
        key = str(chat_id)
        if key not in self._data:
            self._data[key] = {
                "mode": "emoji",
                "active": True,
                "custom_text": "Bu xabar shifrlangan 🔒",
                "target_mode": "none",  # "none", "only" (faqat tanlanganlarga ochiq), "hide" (tanlanganlarga yopiq)
                "hidden_users": [],     # hide rejimida yopiq bo'lganlar
                "only_users": []        # only rejimida ochiq bo'lganlar
            }
        # Eskirgan schema bo'lsa to'ldirish
        chat = self._data[key]
        if "target_mode" not in chat:
            chat["target_mode"] = "hide" if chat.get("hidden_users") else "none"
        if "hidden_users" not in chat:
            chat["hidden_users"] = []
        if "only_users" not in chat:
            chat["only_users"] = []
        return chat

    # ── Guruh Rejimi ──────────────────────────────────────

    def get_chat_mode(self, chat_id: int) -> str | None:
        with self._lock:
            return self._get_chat(chat_id).get("mode", "emoji")

    def set_chat_mode(self, chat_id: int, mode: str):
        with self._lock:
            self._get_chat(chat_id)["mode"] = mode
            self._save()

    # ── Faollik holati ────────────────────────────────────

    def is_chat_active(self, chat_id: int) -> bool:
        with self._lock:
            return self._get_chat(chat_id).get("active", False)

    def set_chat_active(self, chat_id: int, active: bool):
        with self._lock:
            self._get_chat(chat_id)["active"] = active
            self._save()

    # ── Custom Matn ───────────────────────────────────────

    def get_custom_text(self, chat_id: int) -> str:
        with self._lock:
            return self._get_chat(chat_id).get("custom_text", "Bu xabar shifrlangan 🔒")

    def set_custom_text(self, chat_id: int, text: str):
        with self._lock:
            self._get_chat(chat_id)["custom_text"] = text
            self._save()

    # ── Target Mode ("only" vs "hide" vs "none") ──────────

    def get_target_mode(self, chat_id: int) -> str:
        with self._lock:
            return self._get_chat(chat_id).get("target_mode", "none")

    def set_target_mode(self, chat_id: int, mode: str):
        with self._lock:
            self._get_chat(chat_id)["target_mode"] = mode
            self._save()

    # ── ONLY (Faqat shu odam(lar)ga ko'rinsin) ─────────────

    def set_only_user(self, chat_id: int, user_id: int | None, username: str | None, name: str):
        with self._lock:
            chat = self._get_chat(chat_id)
            chat["target_mode"] = "only"
            clean_user = {
                "id": user_id,
                "username": username.lstrip("@").lower() if username else "",
                "name": name or (f"@{username}" if username else str(user_id))
            }
            chat["only_users"] = [clean_user]
            self._save()

    def get_only_users(self, chat_id: int) -> list:
        with self._lock:
            return list(self._get_chat(chat_id).get("only_users", []))

    def is_user_in_only_list(self, chat_id: int, user_id: int, username: str | None) -> bool:
        with self._lock:
            users = self._get_chat(chat_id).get("only_users", [])
            clean_username = username.lstrip("@").lower() if username else ""
            for u in users:
                if u.get("id") and u.get("id") == user_id:
                    return True
                if clean_username and u.get("username") and u.get("username").lower() == clean_username:
                    return True
            return False

    # ── HIDE (Shu odam(lar)dan yashirilsin) ─────────────────

    def add_hidden_user(self, chat_id: int, user_id: int | None, username: str | None, name: str) -> bool:
        with self._lock:
            chat = self._get_chat(chat_id)
            chat["target_mode"] = "hide"
            users = chat.setdefault("hidden_users", [])

            for u in users:
                if user_id and u.get("id") == user_id:
                    return False
                if username and u.get("username", "").lower() == username.lower().lstrip("@"):
                    return False

            clean_user = {
                "id": user_id,
                "username": username.lstrip("@").lower() if username else "",
                "name": name or (f"@{username}" if username else str(user_id))
            }
            users.append(clean_user)
            self._save()
            return True

    def remove_hidden_user(self, chat_id: int, identifier: str) -> bool:
        with self._lock:
            chat = self._get_chat(chat_id)
            users = chat.setdefault("hidden_users", [])
            initial_len = len(users)

            clean_id = identifier.lstrip("@").lower()
            chat["hidden_users"] = [
                u for u in users
                if str(u.get("id")) != clean_id and u.get("username", "").lower() != clean_id
            ]

            changed = len(chat["hidden_users"]) < initial_len
            if not chat["hidden_users"] and chat.get("target_mode") == "hide":
                chat["target_mode"] = "none"
            if changed:
                self._save()
            return changed

    def get_hidden_users(self, chat_id: int) -> list:
        with self._lock:
            return list(self._get_chat(chat_id).get("hidden_users", []))

    def is_user_hidden(self, chat_id: int, user_id: int, username: str | None) -> bool:
        with self._lock:
            users = self._get_chat(chat_id).get("hidden_users", [])
            clean_username = username.lstrip("@").lower() if username else ""
            for u in users:
                if u.get("id") and u.get("id") == user_id:
                    return True
                if clean_username and u.get("username") and u.get("username").lower() == clean_username:
                    return True
            return False

    # ── Tozalash (Reset) ──────────────────────────────────

    def clear_targets(self, chat_id: int):
        with self._lock:
            chat = self._get_chat(chat_id)
            chat["target_mode"] = "none"
            chat["only_users"] = []
            chat["hidden_users"] = []
            self._save()

    # ── Statistika ────────────────────────────────────────

    def get_all_chats(self) -> list:
        with self._lock:
            return list(self._data.keys())
