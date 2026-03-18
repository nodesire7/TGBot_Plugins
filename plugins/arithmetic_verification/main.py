"""
Arithmetic Verification Plugin

Provides math-based captcha verification for new group members.
"""

import random
import asyncio
import logging
from typing import Optional
from datetime import datetime

from plugin_sdk import Plugin, Context, User, Message, Permission, CallbackQuery
from plugin_sdk.utils import format_user_mention, escape_markdown, make_inline_keyboard, make_button

logger = logging.getLogger(__name__)


class ArithmeticVerificationPlugin(Plugin):
    """
    Arithmetic Verification Plugin

    Challenges new members with math problems to verify they are human.
    """

    id = "arithmetic_verification"
    name = "Arithmetic Verification"
    version = "1.0.0"
    author = "TGBot Admin"
    description = "Math-based captcha verification for new group members"
    permissions = [
        Permission.SEND_MESSAGES,
        Permission.DELETE_MESSAGES,
        Permission.RESTRICT_MEMBERS,
    ]

    # Difficulty settings
    DIFFICULTY_CONFIG = {
        "easy": {"min": 1, "max": 10, "operations": ["+", "-"]},
        "medium": {"min": 1, "max": 50, "operations": ["+", "-", "*"]},
        "hard": {"min": 1, "max": 100, "operations": ["+", "-", "*", "/"]},
    }

    @Plugin.on_join(priority=10)
    async def on_user_join(self, ctx: Context, user: User):
        """Handle new user joining the group."""
        # Check if plugin is enabled
        if not ctx.get_config("enabled", True):
            return

        # Generate math problem
        problem, answer = self._generate_problem(ctx)

        # Create verification record
        verification_key = f"verify:{user.id}"
        timeout = ctx.get_config("timeout_seconds", 60)

        await ctx.cache_set(verification_key, str(answer), expire=timeout)
        await ctx.cache_set(f"attempts:{user.id}", "0", expire=timeout)

        # Restrict user until verified
        await ctx.restrict_user(
            user.id,
            permissions={
                "can_send_messages": False,
                "can_send_media_messages": False,
                "can_send_polls": False,
                "can_send_other_messages": False,
                "can_add_web_page_previews": False,
            }
        )

        # Send verification message
        welcome_msg = ctx.get_config("welcome_message", "Please solve this math problem:")
        user_mention = format_user_mention(user.id, user.full_name)

        keyboard = self._build_keyboard(user.id, problem)

        message = await ctx.send_message(
            text=f"{user_mention}\n\n{welcome_msg}\n\n**{problem}**",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )

        # Store message info for cleanup
        await ctx.cache_set(f"msg:{user.id}", str(message.get("message_id", 0)), expire=timeout)

        # Schedule timeout check
        asyncio.create_task(self._timeout_check(ctx, user.id, timeout))

    @Plugin.on_callback
    async def handle_callback(self, ctx: Context, callback: CallbackQuery):
        """Handle button callbacks."""
        if not callback.data or not callback.data.startswith("verify:"):
            return

        parts = callback.data.split(":")
        if len(parts) < 3:
            return

        user_id = int(parts[1])
        answer = parts[2]

        # Check if this is the correct user
        if callback.from_user.id != user_id:
            await ctx.answer_callback(callback.id, text="This is not your verification!")
            return

        # Get stored answer
        stored_answer = await ctx.cache_get(f"verify:{user_id}")

        if stored_answer is None:
            await ctx.answer_callback(callback.id, text="Verification expired!", show_alert=True)
            return

        # Check answer
        if answer == stored_answer:
            await self._handle_success(ctx, user_id, callback)
        else:
            await self._handle_failure(ctx, user_id, callback)

    @Plugin.on_message(priority=5)
    async def handle_message(self, ctx: Context, message: Message):
        """Handle text message answers."""
        if not message.text or not message.from_user:
            return

        # Check if user is in verification
        stored_answer = await ctx.cache_get(f"verify:{message.from_user.id}")
        if stored_answer is None:
            return

        # Try to parse answer
        try:
            user_answer = str(int(message.text.strip()))
        except ValueError:
            return  # Not a number, ignore

        # Check answer
        if user_answer == stored_answer:
            await self._handle_success_text(ctx, message.from_user.id, message)
        else:
            await self._handle_failure_text(ctx, message.from_user.id, message)

        # Delete the message
        await ctx.delete_message(message.id)

    def _generate_problem(self, ctx: Context) -> tuple:
        """Generate a math problem and its answer."""
        difficulty = ctx.get_config("difficulty", "easy")
        config = self.DIFFICULTY_CONFIG.get(difficulty, self.DIFFICULTY_CONFIG["easy"])

        operations = config["operations"]
        op = random.choice(operations)

        a = random.randint(config["min"], config["max"])
        b = random.randint(config["min"], config["max"])

        # Ensure valid division
        if op == "/":
            b = random.randint(1, 10)
            a = b * random.randint(1, 10)
            answer = a // b
            problem = f"{a} / {b} = ?"
        elif op == "-":
            # Ensure positive result
            if a < b:
                a, b = b, a
            answer = a - b
            problem = f"{a} - {b} = ?"
        else:
            answer = a + b if op == "+" else a * b
            problem = f"{a} {op} {b} = ?"

        return problem, answer

    def _build_keyboard(self, user_id: int, problem: str) -> dict:
        """Build the verification keyboard with answer options."""
        # Parse the problem to get correct answer
        parts = problem.split()
        a, op, b = int(parts[0]), parts[1], int(parts[2])

        if op == "+":
            correct = a + b
        elif op == "-":
            correct = a - b
        elif op == "*":
            correct = a * b
        else:
            correct = a // b

        # Generate wrong answers
        answers = {correct}
        while len(answers) < 4:
            wrong = correct + random.randint(-10, 10)
            if wrong != correct and wrong >= 0:
                answers.add(wrong)

        answers = list(answers)
        random.shuffle(answers)

        # Build keyboard
        buttons = []
        for ans in answers:
            buttons.append([make_button(str(ans), callback_data=f"verify:{user_id}:{ans}")])

        return make_inline_keyboard(buttons)

    async def _handle_success(self, ctx: Context, user_id: int, callback: CallbackQuery):
        """Handle successful verification via button."""
        # Unrestrict user
        await ctx.unmute_user(user_id)

        # Clean up cache
        await ctx.cache_delete(f"verify:{user_id}")
        await ctx.cache_delete(f"attempts:{user_id}")

        # Delete verification message
        msg_id = await ctx.cache_get(f"msg:{user_id}")
        if msg_id:
            await ctx.delete_message(int(msg_id))

        # Send success message
        success_msg = ctx.get_config("success_message", "Verification successful!")
        await ctx.answer_callback(callback.id, text=success_msg, show_alert=True)

        logger.info(f"User {user_id} passed verification in chat {ctx.chat_id}")

    async def _handle_success_text(self, ctx: Context, user_id: int, message: Message):
        """Handle successful verification via text."""
        await ctx.unmute_user(user_id)
        await ctx.cache_delete(f"verify:{user_id}")
        await ctx.cache_delete(f"attempts:{user_id}")

        success_msg = ctx.get_config("success_message", "Verification successful!")
        await ctx.reply(success_msg)

        logger.info(f"User {user_id} passed verification (text) in chat {ctx.chat_id}")

    async def _handle_failure(self, ctx: Context, user_id: int, callback: CallbackQuery):
        """Handle failed verification via button."""
        attempts_str = await ctx.cache_get(f"attempts:{user_id}") or "0"
        attempts = int(attempts_str) + 1
        max_attempts = ctx.get_config("max_attempts", 3)

        await ctx.cache_set(f"attempts:{user_id}", str(attempts), expire=300)

        remaining = max_attempts - attempts

        if remaining <= 0:
            await self._kick_user(ctx, user_id)
            await ctx.answer_callback(
                callback.id,
                text="Too many failed attempts. You have been removed.",
                show_alert=True
            )
        else:
            await ctx.answer_callback(
                callback.id,
                text=f"Wrong answer! {remaining} attempt(s) remaining.",
                show_alert=True
            )
            # Generate new problem
            problem, answer = self._generate_problem(ctx)
            await ctx.cache_set(f"verify:{user_id}", str(answer), expire=60)

    async def _handle_failure_text(self, ctx: Context, user_id: int, message: Message):
        """Handle failed verification via text."""
        attempts_str = await ctx.cache_get(f"attempts:{user_id}") or "0"
        attempts = int(attempts_str) + 1
        max_attempts = ctx.get_config("max_attempts", 3)

        await ctx.cache_set(f"attempts:{user_id}", str(attempts), expire=300)

        remaining = max_attempts - attempts

        if remaining <= 0:
            await self._kick_user(ctx, user_id)
            await ctx.reply("Too many failed attempts. You have been removed.")
        else:
            await ctx.reply(f"Wrong answer! {remaining} attempt(s) remaining.")
            problem, answer = self._generate_problem(ctx)
            await ctx.cache_set(f"verify:{user_id}", str(answer), expire=60)
            await ctx.reply(f"New problem: **{problem}**", parse_mode="Markdown")

    async def _kick_user(self, ctx: Context, user_id: int):
        """Kick user after failed verification."""
        if ctx.get_config("kick_on_fail", True):
            await ctx.kick_user(user_id)

        # Clean up
        await ctx.cache_delete(f"verify:{user_id}")
        await ctx.cache_delete(f"attempts:{user_id}")
        await ctx.cache_delete(f"msg:{user_id}")

        logger.warning(f"User {user_id} failed verification in chat {ctx.chat_id}")

    async def _timeout_check(self, ctx: Context, user_id: int, timeout: int):
        """Check if verification timed out."""
        await asyncio.sleep(timeout)

        # Check if still pending
        stored = await ctx.cache_get(f"verify:{user_id}")
        if stored is not None:
            await self._kick_user(ctx, user_id)
            await ctx.send_message("Verification timed out. User has been removed.")


# Export plugin
plugin = ArithmeticVerificationPlugin
