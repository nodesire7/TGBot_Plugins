"""
Anti Spam Plugin - Multi-layer spam detection and prevention
"""
import re
import time
from typing import Dict, List, Set
from collections import defaultdict

from plugin_sdk import Plugin, Context, Message, Permission
from plugin_sdk.utils import RateLimiter


class AntiSpamPlugin(Plugin):
    """Multi-layer spam detection and prevention"""

    id = "anti_spam"
    name = "Anti Spam"
    version = "1.0.0"
    author = "TGBot Admin"
    description = "Multi-layer spam detection and prevention"
    permissions = [
        Permission.DELETE_MESSAGES,
        Permission.RESTRICT_MEMBERS,
        Permission.KICK_MEMBERS,
    ]

    config_schema = {
        "type": "object",
        "properties": {
            "max_messages_per_minute": {"type": "integer", "default": 5},
            "max_identical_messages": {"type": "integer", "default": 3},
            "action": {"type": "string", "enum": ["delete", "mute", "kick"], "default": "delete"},
            "mute_duration": {"type": "integer", "default": 300},
            "check_new_users": {"type": "boolean", "default": True},
            "new_user_cooldown": {"type": "integer", "default": 300},
            "spam_patterns": {"type": "array", "items": {"type": "string"}, "default": []},
        },
    }

    def __init__(self):
        self.message_history: Dict[int, List[Dict]] = defaultdict(list)
        self.user_message_count: Dict[int, List[float]] = defaultdict(list)
        self.new_users: Dict[int, float] = {}  # user_id -> join_time

    def _is_duplicate(self, user_id: int, text: str, max_identical: int) -> bool:
        """Check for duplicate messages"""
        history = self.message_history.get(user_id, [])
        identical_count = sum(1 for msg in history if msg.get("text") == text)
        return identical_count >= max_identical

    def _is_rate_limited(self, user_id: int, max_per_minute: int) -> bool:
        """Check if user is sending messages too fast"""
        now = time.time()
        window_start = now - 60

        # Clean old entries
        self.user_message_count[user_id] = [
            ts for ts in self.user_message_count[user_id]
            if ts > window_start
        ]

        return len(self.user_message_count[user_id]) >= max_per_minute

    def _matches_spam_pattern(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any spam pattern"""
        for pattern in patterns:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            except re.error:
                continue
        return False

    @Plugin.on_join(priority=5)
    async def on_join(self, ctx: Context, user):
        """Track new users for stricter checking"""
        check_new = ctx.get_config("check_new_users", True)
        if check_new:
            self.new_users[user.id] = time.time()

    @Plugin.on_message(priority=5)
    async def on_message(self, ctx: Context, msg: Message):
        """Check message for spam"""
        if not msg.from_user or not msg.text:
            return

        user_id = msg.from_user.id
        text = msg.text

        # Get config
        max_per_minute = ctx.get_config("max_messages_per_minute", 5)
        max_identical = ctx.get_config("max_identical_messages", 3)
        action = ctx.get_config("action", "delete")
        mute_duration = ctx.get_config("mute_duration", 300)
        spam_patterns = ctx.get_config("spam_patterns", [])
        new_user_cooldown = ctx.get_config("new_user_cooldown", 300)

        # Check new user restrictions
        if user_id in self.new_users:
            join_time = self.new_users[user_id]
            if time.time() - join_time < new_user_cooldown:
                max_per_minute = max(1, max_per_minute // 2)  # Stricter for new users

        is_spam = False
        spam_reason = ""

        # Check rate limit
        if self._is_rate_limited(user_id, max_per_minute):
            is_spam = True
            spam_reason = "Rate limit exceeded"

        # Check duplicate
        if self._is_duplicate(user_id, text, max_identical):
            is_spam = True
            spam_reason = "Duplicate message"

        # Check spam patterns
        if spam_patterns and self._matches_spam_pattern(text, spam_patterns):
            is_spam = True
            spam_reason = "Spam pattern detected"

        if is_spam:
            # Record message in history
            self.message_history[user_id].append({
                "text": text,
                "time": time.time()
            })
            self.user_message_count[user_id].append(time.time())

            # Take action
            if action == "kick":
                await ctx.kick_user(user_id)
            elif action == "mute":
                await ctx.mute_user(user_id, mute_duration)
                await ctx.delete_message(msg.id)
            else:  # delete
                await ctx.delete_message(msg.id)

            # Log the action
            import logging
            logging.info(f"Anti-spam action: {action} for user {user_id} - {spam_reason}")

        else:
            # Update history
            self.message_history[user_id].append({
                "text": text,
                "time": time.time()
            })
            self.user_message_count[user_id].append(time.time())

            # Keep history limited
            if len(self.message_history[user_id]) > 50:
                self.message_history[user_id] = self.message_history[user_id][-20:]


plugin = AntiSpamPlugin
