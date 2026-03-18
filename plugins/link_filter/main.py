"""
Link Filter Plugin - Filter links in group messages
"""
import re
from typing import List, Optional
from urllib.parse import urlparse

from plugin_sdk import Plugin, Context, Message, Permission
from plugin_sdk.utils import extract_urls


class LinkFilterPlugin(Plugin):
    """Filter links based on whitelist/blacklist rules"""

    id = "link_filter"
    name = "Link Filter"
    version = "1.0.0"
    author = "TGBot Admin"
    description = "Filter links in group messages with whitelist/blacklist support"
    permissions = [
        Permission.DELETE_MESSAGES,
        Permission.RESTRICT_MEMBERS,
    ]

    config_schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ["whitelist", "blacklist"], "default": "blacklist"},
            "allowed_domains": {"type": "array", "items": {"type": "string"}, "default": []},
            "blocked_domains": {"type": "array", "items": {"type": "string"}, "default": []},
            "delete_message": {"type": "boolean", "default": True},
            "warn_user": {"type": "boolean", "default": True},
            "warning_message": {"type": "string", "default": "Links are not allowed in this group."},
            "exempt_admins": {"type": "boolean", "default": True},
        },
    }

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url if url.startswith('http') else f'https://{url}')
            return parsed.netloc.lower().replace('www.', '')
        except Exception:
            return url.lower()

    def _is_link_allowed(self, url: str, mode: str, allowed: List[str], blocked: List[str]) -> bool:
        """Check if link is allowed based on mode"""
        domain = self._extract_domain(url)

        if mode == "whitelist":
            return any(domain == d or domain.endswith(f'.{d}') for d in allowed)
        else:  # blacklist
            return not any(domain == d or domain.endswith(f'.{d}') for d in blocked)

    @Plugin.on_message(priority=10)
    async def on_message(self, ctx: Context, msg: Message):
        """Check message for filtered links"""
        if not msg.text and not msg.caption:
            return

        text = msg.text or msg.caption or ""
        urls = extract_urls(text)

        if not urls:
            return

        # Check if user is admin
        exempt_admins = ctx.get_config("exempt_admins", True)
        if exempt_admins and msg.from_user:
            try:
                member = await ctx.get_chat_member(msg.from_user.id)
                if member and member.get("status") in ["administrator", "creator"]:
                    return
            except Exception:
                pass

        mode = ctx.get_config("mode", "blacklist")
        allowed = ctx.get_config("allowed_domains", [])
        blocked = ctx.get_config("blocked_domains", [])

        for url in urls:
            if not self._is_link_allowed(url, mode, allowed, blocked):
                # Delete message
                if ctx.get_config("delete_message", True):
                    await ctx.delete_message(msg.id)

                # Warn user
                if ctx.get_config("warn_user", True):
                    warning = ctx.get_config("warning_message", "Links are not allowed.")
                    await ctx.reply(warning)

                return  # Stop after first filtered link


plugin = LinkFilterPlugin
