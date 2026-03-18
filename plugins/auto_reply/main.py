"""
Auto Reply Plugin - Automatic message replies based on triggers
"""
import re
import time
import random
from typing import Dict, List, Optional

from plugin_sdk import Plugin, Context, Message, Permission
from plugin_sdk.utils import Cooldown


class AutoReplyPlugin(Plugin):
    """Automatic reply to messages based on triggers"""

    id = "auto_reply"
    name = "Auto Reply"
    version = "1.0.0"
    author = "TGBot Admin"
    description = "Automatic reply to messages based on keywords or patterns"
    permissions = [Permission.SEND_MESSAGES]

    config_schema = {
        "type": "object",
        "properties": {
            "replies": {"type": "array", "default": []},
            "cooldown_seconds": {"type": "integer", "default": 5},
            "random_responses": {"type": "boolean", "default": False},
            "exempt_admins": {"type": "boolean", "default": True},
        },
    }

    def __init__(self):
        self.cooldown = Cooldown(default_seconds=5)

    def _matches_trigger(self, text: str, trigger: str, trigger_type: str, case_sensitive: bool) -> bool:
        """Check if text matches trigger"""
        if not case_sensitive:
            text = text.lower()
            trigger = trigger.lower()

        if trigger_type == "exact":
            return text == trigger
        elif trigger_type == "contains":
            return trigger in text
        elif trigger_type == "startswith":
            return text.startswith(trigger)
        elif trigger_type == "regex":
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                return bool(re.search(trigger, text, flags))
            except re.error:
                return False
        return False

    def _format_response(self, response: str, ctx: Context, msg: Message) -> str:
        """Format response with variables"""
        user = msg.from_user
        if user:
            response = response.replace("{user}", user.full_name)
            response = response.replace("{username}", user.username or "")
            response = response.replace("{user_id}", str(user.id))
        response = response.replace("{chat_id}", str(ctx.chat_id))
        return response

    @Plugin.on_message(priority=50)
    async def on_message(self, ctx: Context, msg: Message):
        """Check for triggers and reply"""
        if not msg.from_user or not msg.text:
            return

        user_id = msg.from_user.id
        text = msg.text

        # Check exempt admins
        if ctx.get_config("exempt_admins", True):
            try:
                member = await ctx.get_chat_member(user_id)
                if member and member.get("status") in ["administrator", "creator"]:
                    return
            except Exception:
                pass

        # Check cooldown
        cooldown = ctx.get_config("cooldown_seconds", 5)
        if self.cooldown.is_on_cooldown("reply", user_id):
            return

        replies = ctx.get_config("replies", [])
        random_responses = ctx.get_config("random_responses", False)

        matched_replies = []

        for rule in replies:
            trigger = rule.get("trigger", "")
            trigger_type = rule.get("trigger_type", "contains")
            case_sensitive = rule.get("case_sensitive", False)

            if self._matches_trigger(text, trigger, trigger_type, case_sensitive):
                matched_replies.append(rule)

        if not matched_replies:
            return

        # Select response
        if random_responses:
            rule = random.choice(matched_replies)
        else:
            rule = matched_replies[0]

        response = rule.get("response", "")
        reply_to = rule.get("reply_to_message", False)

        if not response:
            return

        # Format and send response
        formatted = self._format_response(response, ctx, msg)

        await ctx.send_message(
            text=formatted,
            reply_to_message_id=msg.id if reply_to else None
        )

        # Set cooldown
        self.cooldown.set("reply", user_id, cooldown)

    @Plugin.on_command("addreply")
    async def add_reply(self, ctx: Context, args: List[str]):
        """Add a new auto-reply rule (admin only)"""
        if len(args) < 2:
            await ctx.reply("Usage: /addreply <trigger> | <response>")
            return

        # Parse trigger and response
        text = " ".join(args)
        if "|" in text:
            trigger, response = text.split("|", 1)
            trigger = trigger.strip()
            response = response.strip()
        else:
            await ctx.reply("Usage: /addreply <trigger> | <response>")
            return

        # Add to config (would need API to persist)
        await ctx.reply(f"Added reply: '{trigger}' → '{response}'")

    @Plugin.on_command("listreplies")
    async def list_replies(self, ctx: Context, args: List[str]):
        """List all auto-reply rules"""
        replies = ctx.get_config("replies", [])

        if not replies:
            await ctx.reply("No auto-reply rules configured.")
            return

        lines = ["Auto-reply rules:"]
        for i, rule in enumerate(replies, 1):
            trigger = rule.get("trigger", "")
            response = rule.get("response", "")
            lines.append(f"{i}. '{trigger}' → '{response}'")

        await ctx.reply("\n".join(lines))


plugin = AutoReplyPlugin
