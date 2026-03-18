"""
Flood Protection Plugin

Protects groups from message flooding with rate limiting.
"""

import time
import hashlib
import logging
from collections import defaultdict
from typing import List, Dict, Deque
from collections import deque

from plugin_sdk import Plugin, Context, Message, Permission
from plugin_sdk.utils import format_user_mention

logger = logging.getLogger(__name__)


class FloodProtectionPlugin(Plugin):
    """
    Flood Protection Plugin

    Implements rate limiting and duplicate detection.
    """

    id = "flood_protection"
    name = "Flood Protection"
    version = "1.0.0"
    author = "TGBot Admin"
    description = "Rate limiting and flood prevention"
    permissions = [Permission.DELETE_MESSAGES, Permission.RESTRICT_MEMBERS]

    def __init__(self):
        super().__init__()
        # Message tracking: {chat_id: {user_id: deque of timestamps}}
        self._message_times: Dict[int, Dict[int, Deque[float]]] = defaultdict(
            lambda: defaultdict(lambda: deque(maxlen=100))
        )
        # Duplicate tracking: {chat_id: {user_id: {hash: count}}}
        self._duplicate_tracker: Dict[int, Dict[int, Dict[str, int]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(int))
        )
        # Statistics
        self._stats = {
            "total_checked": 0,
            "flood_detected": 0,
            "duplicates_blocked": 0,
        }

    @Plugin.on_message(priority=15)
    async def on_message(self, ctx: Context, message: Message):
        """Check for flooding."""
        if not ctx.get_config("enabled", True):
            return

        if not message.from_user:
            return

        user_id = message.from_user.id
        chat_id = ctx.chat_id

        # Check admin exemption
        if ctx.get_config("exempt_admins", True):
            try:
                admins = await ctx.get_chat_administrators()
                admin_ids = [a.get("user", {}).get("id") for a in admins]
                if user_id in admin_ids:
                    return
            except Exception:
                pass

        self._stats["total_checked"] += 1

        # Check rate limit
        if await self._check_rate_limit(ctx, user_id):
            await self._handle_flood(ctx, message)
            return

        # Check duplicates
        if ctx.get_config("check_duplicates", True):
            if await self._check_duplicate(ctx, message, user_id):
                await self._handle_duplicate(ctx, message)
                return

        # Record message
        self._record_message(chat_id, user_id, message)

    @Plugin.on_command("floodstats")
    async def show_stats(self, ctx: Context, args: List[str]):
        """Show flood protection statistics."""
        stats_msg = (
            "Flood Protection Statistics:\n"
            f"- Messages checked: {self._stats['total_checked']}\n"
            f"- Flood detected: {self._stats['flood_detected']}\n"
            f"- Duplicates blocked: {self._stats['duplicates_blocked']}"
        )
        await ctx.reply(stats_msg)

    @Plugin.on_command("resetflood")
    async def reset_flood(self, ctx: Context, args: List[str]):
        """Reset flood counter for a user."""
        if not args:
            await ctx.reply("Usage: /resetflood <user_id>")
            return

        try:
            user_id = int(args[0])
        except ValueError:
            await ctx.reply("Invalid user ID")
            return

        chat_id = ctx.chat_id

        # Reset tracking
        if chat_id in self._message_times and user_id in self._message_times[chat_id]:
            self._message_times[chat_id][user_id].clear()

        if chat_id in self._duplicate_tracker and user_id in self._duplicate_tracker[chat_id]:
            self._duplicate_tracker[chat_id][user_id].clear()

        await ctx.reply(f"Flood counter reset for user {user_id}")

    async def _check_rate_limit(self, ctx: Context, user_id: int) -> bool:
        """Check if user is flooding."""
        max_messages = ctx.get_config("max_messages", 5)
        time_window = ctx.get_config("time_window", 10)
        chat_id = ctx.chat_id

        now = time.time()
        window_start = now - time_window

        # Get user's message times
        times = self._message_times[chat_id][user_id]

        # Remove old entries
        while times and times[0] < window_start:
            times.popleft()

        # Check if limit exceeded
        return len(times) >= max_messages

    async def _check_duplicate(self, ctx: Context, message: Message, user_id: int) -> bool:
        """Check for duplicate messages."""
        text = message.text or message.caption
        if not text:
            return False

        threshold = ctx.get_config("duplicate_threshold", 3)
        chat_id = ctx.chat_id

        # Generate hash of message
        msg_hash = hashlib.md5(text.encode()).hexdigest()[:16]

        # Track duplicates
        self._duplicate_tracker[chat_id][user_id][msg_hash] += 1

        return self._duplicate_tracker[chat_id][user_id][msg_hash] >= threshold

    def _record_message(self, chat_id: int, user_id: int, message: Message):
        """Record a message for tracking."""
        now = time.time()
        self._message_times[chat_id][user_id].append(now)

    async def _handle_flood(self, ctx: Context, message: Message):
        """Handle flood detection."""
        self._stats["flood_detected"] += 1

        user = message.from_user
        user_mention = format_user_mention(user.id, user.full_name) if user else "User"

        # Delete message if configured
        if ctx.get_config("delete_flood_messages", True):
            try:
                await ctx.delete_message(message.id)
            except Exception:
                pass

        # Take action
        action = ctx.get_config("action", "mute")
        warn_msg = ctx.get_config("warn_message", "Please slow down!")

        if action == "warn":
            await ctx.send_message(f"{user_mention} {warn_msg}")

        elif action == "mute":
            duration = ctx.get_config("mute_duration", 300)
            await ctx.mute_user(user.id, duration=duration)
            await ctx.send_message(
                f"{user_mention} has been muted for flooding ({duration}s)"
            )

        elif action == "kick":
            await ctx.kick_user(user.id)
            await ctx.send_message(f"{user_mention} has been removed for flooding")

        logger.info(f"Flood detected from user {user.id} in chat {ctx.chat_id}")

    async def _handle_duplicate(self, ctx: Context, message: Message):
        """Handle duplicate detection."""
        self._stats["duplicates_blocked"] += 1

        user = message.from_user

        # Delete duplicate
        if ctx.get_config("delete_flood_messages", True):
            try:
                await ctx.delete_message(message.id)
            except Exception:
                pass

        logger.info(f"Duplicate message from user {user.id} in chat {ctx.chat_id}")


# Export plugin
plugin = FloodProtectionPlugin
