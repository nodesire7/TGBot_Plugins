"""
Welcome Message Plugin

Sends customizable welcome messages to new group members.
"""

import asyncio
import logging
from datetime import datetime
from typing import List

from plugin_sdk import Plugin, Context, User, Message, Permission, CallbackQuery
from plugin_sdk.utils import format_user_mention, escape_markdown, make_inline_keyboard, make_button

logger = logging.getLogger(__name__)


class WelcomeMessagePlugin(Plugin):
    """
    Welcome Message Plugin

    Sends customizable welcome messages with template support.
    """

    id = "welcome_message"
    name = "Welcome Message"
    version = "1.0.0"
    author = "TGBot Admin"
    description = "Customizable welcome messages for new members"
    permissions = [Permission.SEND_MESSAGES, Permission.DELETE_MESSAGES]

    @Plugin.on_join(priority=5)
    async def on_user_join(self, ctx: Context, user: User):
        """Handle new user joining."""
        # Check if enabled
        if not ctx.get_config("enabled", True):
            return

        # Ignore bots if configured
        if user.is_bot and ctx.get_config("ignore_bots", True):
            return

        # Get configuration
        template = ctx.get_config(
            "message_template",
            "Welcome {user} to {chat_title}!"
        )
        parse_mode = ctx.get_config("parse_mode", "Markdown")
        mention_user = ctx.get_config("mention_user", True)
        show_rules = ctx.get_config("show_rules_button", False)
        delete_after = ctx.get_config("delete_after", 0)
        silent = ctx.get_config("silent", False)

        # Build message
        user_display = format_user_mention(user.id, user.full_name) if mention_user else user.full_name

        message_text = self._format_template(
            template,
            user=user_display,
            user_id=str(user.id),
            username=user.username or "N/A",
            chat_title=f"the group",
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        # Build keyboard
        keyboard = None
        if show_rules:
            keyboard = make_inline_keyboard([[
                make_button("View Rules", callback_data=f"welcome_rules:{user.id}")
            ]])

        # Send message
        try:
            msg = await ctx.send_message(
                text=message_text,
                parse_mode=parse_mode if parse_mode != "None" else None,
                disable_notification=silent,
                reply_markup=keyboard,
            )

            # Schedule deletion if configured
            if delete_after > 0:
                asyncio.create_task(
                    self._delete_after(ctx, msg.get("message_id"), delete_after)
                )

            logger.info(f"Sent welcome message for user {user.id} in chat {ctx.chat_id}")

        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")

    @Plugin.on_callback
    async def handle_callback(self, ctx: Context, callback: CallbackQuery):
        """Handle rules button callback."""
        if not callback.data or not callback.data.startswith("welcome_rules:"):
            return

        rules_text = ctx.get_config("rules_text", "No rules have been set.")

        await ctx.answer_callback(
            callback.id,
            text=rules_text[:200] if len(rules_text) > 200 else rules_text,
            show_alert=True
        )

    @Plugin.on_command("setwelcome")
    async def set_welcome(self, ctx: Context, args: List[str]):
        """Set welcome message template."""
        if not args:
            current = ctx.get_config("message_template", "Default welcome message")
            await ctx.reply(
                f"Current welcome message:\n\n{current}\n\n"
                "Use /setwelcome <message> to update.\n"
                "Variables: {user}, {user_id}, {username}, {chat_title}, {date}"
            )
            return

        new_message = " ".join(args)
        # In a real implementation, this would save to database
        await ctx.reply(
            f"Welcome message updated!\n\nPreview:\n{new_message}"
        )
        logger.info(f"Welcome message updated in chat {ctx.chat_id}")

    @Plugin.on_command("setrules")
    async def set_rules(self, ctx: Context, args: List[str]):
        """Set group rules."""
        if not args:
            current = ctx.get_config("rules_text", "No rules set")
            await ctx.reply(f"Current rules:\n\n{current}")
            return

        new_rules = " ".join(args)
        await ctx.reply("Rules have been updated!")
        logger.info(f"Rules updated in chat {ctx.chat_id}")

    @Plugin.on_command("welcome")
    async def preview_welcome(self, ctx: Context, args: List[str]):
        """Preview the welcome message."""
        template = ctx.get_config("message_template", "Welcome {user}!")

        # Use the sender as example
        user_display = format_user_mention(123456789, "Example User")

        preview = self._format_template(
            template,
            user=user_display,
            user_id="123456789",
            username="example_user",
            chat_title="Example Group",
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )

        await ctx.reply(f"Welcome message preview:\n\n{preview}", parse_mode="Markdown")

    def _format_template(self, template: str, **kwargs) -> str:
        """Format template with variables."""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return template

    async def _delete_after(self, ctx: Context, message_id: int, delay: int):
        """Delete message after delay."""
        await asyncio.sleep(delay)
        try:
            await ctx.delete_message(message_id)
        except Exception as e:
            logger.debug(f"Could not delete welcome message: {e}")


# Export plugin
plugin = WelcomeMessagePlugin
