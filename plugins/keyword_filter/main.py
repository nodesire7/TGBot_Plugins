"""
Keyword Filter Plugin

Automatically deletes messages containing blocked keywords or patterns.
"""

import re
import logging
from typing import List, Optional

from plugin_sdk import Plugin, Context, Message, Permission
from plugin_sdk.utils import format_user_mention

logger = logging.getLogger(__name__)


class KeywordFilterPlugin(Plugin):
    """
    Keyword Filter Plugin

    Filters messages based on keywords and regex patterns.
    """

    id = "keyword_filter"
    name = "Keyword Filter"
    version = "1.0.0"
    author = "TGBot Admin"
    description = "Auto-delete messages with blocked keywords"
    permissions = [Permission.DELETE_MESSAGES, Permission.RESTRICT_MEMBERS]

    @Plugin.on_message(priority=10)
    async def on_message(self, ctx: Context, message: Message):
        """Check message for blocked content."""
        if not ctx.get_config("enabled", True):
            return

        # Skip if no text content
        text = message.text or message.caption
        if not text:
            return

        # Check exemption
        if await self._is_exempt(ctx, message):
            return

        # Check for violations
        violation = await self._check_violation(ctx, text)
        if violation:
            await self._handle_violation(ctx, message, violation)

    @Plugin.on_message(priority=10)
    async def on_edited_message(self, ctx: Context, message: Message):
        """Check edited messages if configured."""
        if not ctx.get_config("check_edits", True):
            return

        await self.on_message(ctx, message)

    @Plugin.on_command("addword")
    async def add_word(self, ctx: Context, args: List[str]):
        """Add word to blocklist."""
        if not args:
            await ctx.reply("Usage: /addword <word>")
            return

        word = args[0].lower()
        blocked = ctx.get_config("blocked_words", [])

        if word in blocked:
            await ctx.reply(f"'{word}' is already blocked.")
            return

        blocked.append(word)
        # In real implementation, save to database
        await ctx.reply(f"Added '{word}' to blocklist.")

    @Plugin.on_command("removeword")
    async def remove_word(self, ctx: Context, args: List[str]):
        """Remove word from blocklist."""
        if not args:
            await ctx.reply("Usage: /removeword <word>")
            return

        word = args[0].lower()
        blocked = ctx.get_config("blocked_words", [])

        if word not in blocked:
            await ctx.reply(f"'{word}' is not in the blocklist.")
            return

        blocked.remove(word)
        await ctx.reply(f"Removed '{word}' from blocklist.")

    @Plugin.on_command("listwords")
    async def list_words(self, ctx: Context, args: List[str]):
        """List blocked words."""
        blocked = ctx.get_config("blocked_words", [])
        patterns = ctx.get_config("blocked_patterns", [])

        msg_parts = []

        if blocked:
            msg_parts.append("Blocked words:\n" + "\n".join(f"- {w}" for w in blocked))

        if patterns:
            msg_parts.append("Blocked patterns:\n" + "\n".join(f"- {p}" for p in patterns))

        if not msg_parts:
            await ctx.reply("No words or patterns are blocked.")
            return

        await ctx.reply("\n\n".join(msg_parts))

    @Plugin.on_command("addpattern")
    async def add_pattern(self, ctx: Context, args: List[str]):
        """Add regex pattern to blocklist."""
        if not args:
            await ctx.reply("Usage: /addpattern <regex>")
            return

        pattern = args[0]

        # Validate regex
        try:
            re.compile(pattern)
        except re.error as e:
            await ctx.reply(f"Invalid regex pattern: {e}")
            return

        patterns = ctx.get_config("blocked_patterns", [])
        patterns.append(pattern)
        await ctx.reply(f"Added pattern: `{pattern}`", parse_mode="Markdown")

    async def _is_exempt(self, ctx: Context, message: Message) -> bool:
        """Check if message is exempt from filtering."""
        if not message.from_user:
            return True

        # Check admin exemption
        if ctx.get_config("exempt_admins", True):
            try:
                admins = await ctx.get_chat_administrators()
                admin_ids = [a.get("user", {}).get("id") for a in admins]
                if message.from_user.id in admin_ids:
                    return True
            except Exception:
                pass

        return False

    async def _check_violation(self, ctx: Context, text: str) -> Optional[str]:
        """Check if text contains blocked content."""
        text_lower = text.lower()

        # Check blocked words
        blocked_words = ctx.get_config("blocked_words", [])
        for word in blocked_words:
            if word.lower() in text_lower:
                return f"blocked word: {word}"

        # Check blocked patterns
        blocked_patterns = ctx.get_config("blocked_patterns", [])
        for pattern in blocked_patterns:
            try:
                if re.search(pattern, text, re.IGNORECASE):
                    return f"blocked pattern: {pattern}"
            except re.error:
                continue

        return None

    async def _handle_violation(self, ctx: Context, message: Message, violation: str):
        """Handle a content violation."""
        action = ctx.get_config("action", "delete")
        warn_before = ctx.get_config("warn_before_action", True)
        warn_msg = ctx.get_config("warn_message", "Message removed.")

        user = message.from_user
        user_mention = format_user_mention(user.id, user.full_name) if user else "Unknown"

        # Delete the message
        try:
            await ctx.delete_message(message.id)
        except Exception as e:
            logger.warning(f"Could not delete message: {e}")
            return

        # Log the deletion
        if ctx.get_config("log_deletions", True):
            logger.info(
                f"Deleted message from {user.id} in {ctx.chat_id}: {violation}"
            )

        # Take action
        if action == "warn" or warn_before:
            await ctx.send_message(f"{user_mention} {warn_msg}")

        if action == "mute" and user:
            duration = ctx.get_config("mute_duration", 300)
            await ctx.mute_user(user.id, duration=duration)
            await ctx.send_message(
                f"{user_mention} has been muted for {duration} seconds."
            )

        elif action == "kick" and user:
            await ctx.kick_user(user.id)
            await ctx.send_message(f"{user_mention} has been removed.")


# Export plugin
plugin = KeywordFilterPlugin
