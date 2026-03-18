"""
Stats Reporter Plugin - Generate statistics reports
"""
import time
from typing import Dict, List
from collections import defaultdict
from datetime import datetime

from plugin_sdk import Plugin, Context, Message, Permission


class StatsReporterPlugin(Plugin):
    """Generate and send periodic statistics reports"""

    id = "stats_reporter"
    name = "Stats Reporter"
    version = "1.0.0"
    author = "TGBot Admin"
    description = "Generate and send periodic statistics reports"
    permissions = [Permission.SEND_MESSAGES]

    config_schema = {
        "type": "object",
        "properties": {
            "report_channel": {"type": "integer"},
            "report_interval_hours": {"type": "integer", "default": 24},
            "include_message_stats": {"type": "boolean", "default": True},
            "include_user_stats": {"type": "boolean", "default": True},
            "include_verification_stats": {"type": "boolean", "default": True},
            "top_users_count": {"type": "integer", "default": 5},
        },
    }

    def __init__(self):
        self.message_counts: Dict[int, int] = defaultdict(int)
        self.user_messages: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self.join_count: Dict[int, int] = defaultdict(int)
        self.leave_count: Dict[int, int] = defaultdict(int)
        self.last_report: Dict[int, float] = {}

    @Plugin.on_message(priority=100)
    async def on_message(self, ctx: Context, msg: Message):
        """Track message statistics"""
        if not msg.from_user:
            return

        chat_id = ctx.chat_id
        user_id = msg.from_user.id

        self.message_counts[chat_id] += 1
        self.user_messages[chat_id][user_id] += 1

    @Plugin.on_join(priority=100)
    async def on_join(self, ctx: Context, user):
        """Track joins"""
        self.join_count[ctx.chat_id] += 1

    @Plugin.on_leave(priority=100)
    async def on_leave(self, ctx: Context, user):
        """Track leaves"""
        self.leave_count[ctx.chat_id] += 1

    @Plugin.on_command("stats")
    async def show_stats(self, ctx: Context, args: List[str]):
        """Show current statistics"""
        chat_id = ctx.chat_id

        lines = [
            f"📊 **Statistics for Chat {chat_id}**",
            "",
            f"📨 Messages: {self.message_counts[chat_id]}",
            f"➕ Joins: {self.join_count[chat_id]}",
            f"➖ Leaves: {self.leave_count[chat_id]}",
        ]

        # Top users
        if ctx.get_config("include_user_stats", True):
            top_count = ctx.get_config("top_users_count", 5)
            user_msgs = self.user_messages[chat_id]
            sorted_users = sorted(user_msgs.items(), key=lambda x: x[1], reverse=True)[:top_count]

            if sorted_users:
                lines.append("")
                lines.append("👤 Top Active Users:")
                for i, (user_id, count) in enumerate(sorted_users, 1):
                    lines.append(f"  {i}. User {user_id}: {count} messages")

        await ctx.reply("\n".join(lines), parse_mode="Markdown")

    @Plugin.on_command("topusers")
    async def show_top_users(self, ctx: Context, args: List[str]):
        """Show most active users"""
        chat_id = ctx.chat_id
        top_count = ctx.get_config("top_users_count", 5)

        user_msgs = self.user_messages[chat_id]
        sorted_users = sorted(user_msgs.items(), key=lambda x: x[1], reverse=True)[:top_count]

        if not sorted_users:
            await ctx.reply("No message statistics available yet.")
            return

        lines = ["👤 **Most Active Users**", ""]
        for i, (user_id, count) in enumerate(sorted_users, 1):
            lines.append(f"{i}. User `{user_id}`: {count} messages")

        await ctx.reply("\n".join(lines), parse_mode="Markdown")

    def _generate_report(self, ctx: Context) -> str:
        """Generate a statistics report"""
        chat_id = ctx.chat_id
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            f"📊 **Daily Statistics Report**",
            f"📅 {now}",
            "",
        ]

        if ctx.get_config("include_message_stats", True):
            lines.extend([
                "📨 **Message Stats**",
                f"  Total messages: {self.message_counts[chat_id]}",
                "",
            ])

        if ctx.get_config("include_user_stats", True):
            top_count = ctx.get_config("top_users_count", 5)
            user_msgs = self.user_messages[chat_id]
            sorted_users = sorted(user_msgs.items(), key=lambda x: x[1], reverse=True)[:top_count]

            lines.append("👤 **Top Users**")
            for i, (user_id, count) in enumerate(sorted_users, 1):
                lines.append(f"  {i}. User {user_id}: {count} msgs")
            lines.append("")

        if ctx.get_config("include_verification_stats", True):
            lines.extend([
                "🔐 **Membership Stats**",
                f"  New joins: {self.join_count[chat_id]}",
                f"  Leaves: {self.leave_count[chat_id]}",
                "",
            ])

        return "\n".join(lines)


plugin = StatsReporterPlugin
